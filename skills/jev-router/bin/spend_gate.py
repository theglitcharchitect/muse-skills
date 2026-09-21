#!/usr/bin/env python3
"""Jev agent spend firewall: approve / review / deny a proposed purchase.

Usage:
  spend_gate.py --item '<what is being bought>' --amount '<price, e.g. 49.99>'
                --vendor '<seller>' [--budget '<budget text>']
                [--rules '<standing spending rules>'] [--context '<task context>']

Question set: spend-v1 (see references/question-library.md).
Exit codes: 0 = approve, 2 = deny, 3 = review (human decides).
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/spend.jsonl.
Deterministic code owns the money math: if config sets
`spend_review_above` and the parsed amount reaches it, the purchase goes
to review no matter what Jev says. Amount parsing never blocks: an
unparseable amount simply skips the cap.
If the gateway is unreachable, the purchase goes to review (exit 3 in
active mode); it is never silently approved.
"""
import sys, os, argparse, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, threshold_for, mode_allows, unreachable_code)

QUESTION_SET = 'spend-v1'


def parse_amount(text):
    """Best-effort float parse; returns None when the amount is not numeric."""
    if text is None:
        return None
    m = re.search(r'[\d,]+(?:\.\d+)?', str(text).replace(',', ''))
    if not m:
        return None
    try:
        return float(m.group(0).replace(',', ''))
    except ValueError:
        return None


def gate(item, amount, vendor, budget, rules, context, cfg):
    if not cfg.get('enabled', True):
        rec = {'item': item, 'amount': amount, 'vendor': vendor,
               'mode': 'off', 'verdict': 'approve',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('spend.jsonl', rec)
        return 0, rec

    # Deterministic cap first: exact amount comparison stays in code.
    cap = cfg.get('spend_review_above')
    value = parse_amount(amount)
    if cap is not None and value is not None and value >= cap:
        rec = {'item': item, 'amount': amount, 'vendor': vendor,
               'mode': cfg.get('mode', 'shadow'), 'verdict': 'review',
               'code_decision': 'spend_review_above',
               'reason': f'amount {value} >= spend_review_above {cap}; Jev was not consulted',
               'question_set_version': QUESTION_SET}
        log_record('spend.jsonl', rec)
        return (0 if not mode_allows(cfg) else 3), rec

    state = (f'Proposed purchase: {item}\nAmount: {amount}\n'
             f'Vendor: {vendor}\nBudget: {budget or "not stated"}\n'
             f'Standing spending rules: {rules or "not stated"}\n'
             f'Task context: {context or "not stated"}')
    questions = {
        'verdict': {
            'type': 'choice',
            'instructions': 'What should happen with this purchase?',
            'criteria': {
                'approve': 'the purchase is within budget and rules and fits the task',
                'review': 'the purchase is plausible but a human should confirm first',
                'deny': 'the purchase violates the rules, looks wasteful, or is out of budget',
            },
        },
        'reversible': {
            'type': 'boolean',
            'instructions': 'This purchase can be fully refunded or cancelled after the fact.',
        },
        'within_policy': {
            'type': 'boolean',
            'instructions': 'This purchase is within the stated budget and spending rules.',
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        # Gateway unreachable: fail toward the human, never toward silent
        # approval. In shadow mode this only logs.
        rec = {'item': item, 'amount': amount, 'vendor': vendor,
               'mode': cfg.get('mode', 'shadow'), 'verdict': 'review',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('spend.jsonl', rec)
        return unreachable_code(cfg), rec
    answers = data.get('answers', {})
    verdict_a = answers.get('verdict', {})
    choice = verdict_a.get('choice', 'review')
    probs = verdict_a.get('probabilities') or {}
    prob = probs.get(choice, 0)
    ranked = sorted(probs.values(), reverse=True)
    margin = round(ranked[0] - ranked[1], 4) if len(ranked) > 1 else None
    reversible = answers.get('reversible', {}).get('probability', 0) >= 0.5
    within_policy = answers.get('within_policy', {}).get('probability', 0) >= 0.5

    # Money gates high: approve needs the verdict probability at the
    # spend threshold AND a within-policy read. Anything else -> review.
    threshold = threshold_for(cfg, 'spend')
    if choice == 'approve' and prob >= threshold and within_policy:
        verdict, code = 'approve', 0
    elif choice == 'deny':
        verdict, code = 'deny', 2
    else:
        verdict, code = 'review', 3

    rec = {'item': item, 'amount': amount, 'vendor': vendor,
           'mode': cfg.get('mode', 'shadow'),
           'route_choice': choice, 'route_probabilities': probs,
           'route_margin': margin, 'route_confidence': verdict_a.get('confidence'),
           'reversible': reversible, 'within_policy': within_policy,
           'threshold': threshold, 'spend_cap': cap,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('spend.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev agent spend firewall')
    p.add_argument('--item', required=True, help='What is being bought')
    p.add_argument('--amount', required=True, help='Price, e.g. 49.99')
    p.add_argument('--vendor', required=True, help='Seller or provider')
    p.add_argument('--budget', default='', help='Budget this spends against')
    p.add_argument('--rules', default='',
                   help='Standing spending rules, quoted')
    p.add_argument('--context', default='', help='Task context for the purchase')
    args = p.parse_args()
    for name in ('item', 'amount', 'vendor'):
        if not getattr(args, name).strip():
            print(json.dumps({'error': f'--{name} must not be empty'}),
                  file=sys.stderr)
            sys.exit(1)
    cfg = load_config()
    code, rec = gate(args.item, args.amount, args.vendor, args.budget,
                     args.rules, args.context, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
