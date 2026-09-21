#!/usr/bin/env python3
"""Jev usage router: gate expensive agent actions behind Jev decisions.

Usage:
  router.py check --action <name> --detail '<what it would do>'

Question set: router-v1 (see references/question-library.md).
Exit codes: 0 = ALLOW, 2 = DENY (skip), 3 = ESCALATE (ask the user).
In shadow mode (or when disabled) the decision is logged and 0 is returned.
Actions in config auto_escalate skip Jev and escalate directly.
Every decision appends to logs/router.jsonl.
If the gateway is unreachable, the action escalates (exit 3 in active mode) instead of failing.
"""
import sys, os, argparse, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, threshold_for, mode_allows, unreachable_code)

QUESTION_SET = 'router-v1'


def route(action, detail, cfg):
    if not cfg.get('enabled', True):
        rec = {'action': action, 'detail': detail, 'mode': 'off',
               'decision': 'allow', 'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('router.jsonl', rec)
        return 0, rec

    if action in cfg.get('auto_escalate', []):
        rec = {'action': action, 'detail': detail,
               'mode': cfg.get('mode', 'shadow'), 'decision': 'escalate',
               'reason': 'auto_escalate list: Jev bypassed',
               'question_set_version': QUESTION_SET}
        log_record('router.jsonl', rec)
        return 0 if not mode_allows(cfg) else 3, rec

    state = f'Proposed agent action: {action}. Detail: {detail}'
    questions = {
        'route': {
            'type': 'choice',
            'instructions': 'Should the agent perform this action now?',
            'criteria': {
                'proceed': 'the action is worthwhile and safe to run now',
                'skip': 'the action is redundant, low-value, or premature',
                'escalate': 'the action is costly, hard to reverse, or needs human judgment first',
            },
        },
        'irreversible': {
            'type': 'boolean',
            'instructions': 'Is this action hard or impossible to undo (spending, sending, deleting, publishing)?',
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        rec = {'action': action, 'detail': detail,
               'mode': cfg.get('mode', 'shadow'), 'decision': 'escalate',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('router.jsonl', rec)
        return unreachable_code(cfg), rec
    answers = data.get('answers', {})
    route_a = answers.get('route', {})
    irr_a = answers.get('irreversible', {})
    choice = route_a.get('choice', 'escalate')
    probs = route_a.get('probabilities') or {}
    prob = probs.get(choice, 0)
    conf = route_a.get('confidence', 0)
    # Margin between the top two options: a 0.51/0.49 split must not look
    # like a 0.91/0.05 split at calibration time. Full distribution is
    # logged so close calls stay visible.
    ranked = sorted(probs.values(), reverse=True)
    margin = round(ranked[0] - ranked[1], 4) if len(ranked) > 1 else None
    irreversible = irr_a.get('probability', 0) >= 0.5

    threshold = threshold_for(cfg, action)
    if choice == 'proceed' and prob >= threshold and not irreversible:
        decision, code = 'allow', 0
    elif choice == 'skip' and not irreversible:
        decision, code = 'deny', 2
    else:
        decision, code = 'escalate', 3

    rec = {'action': action, 'detail': detail,
           'mode': cfg.get('mode', 'shadow'),
           'choice': choice, 'choice_probability': prob,
           'choice_probabilities': probs, 'choice_margin': margin,
           'choice_confidence': conf, 'threshold': threshold,
           'irreversible': irreversible, 'decision': decision,
           'model': model_of(data), 'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('router.jsonl', rec)

    if not mode_allows(cfg):
        return 0, rec  # shadow: log only, always allow
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev usage router')
    p.add_argument('check', choices=['check'])
    p.add_argument('--action', required=True,
                   help='browser_run | research | retry | publish | send_message | delete | ...')
    p.add_argument('--detail', required=True, help='What the action would do')
    args = p.parse_args()
    cfg = load_config()
    code, rec = route(args.action, args.detail, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
