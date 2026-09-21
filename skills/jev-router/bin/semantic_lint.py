#!/usr/bin/env python3
"""Jev semantic code linting: check plain-English rules against code.

Usage:
  semantic_lint.py --rule '<rule in plain English>' --code '<snippet>'
  semantic_lint.py --rule '<rule>' --code-file <path>

Question set: codelint-v1 (see references/question-library.md).
Exit codes: 0 = pass, 2 = flag_for_review, 3 = block.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/lint.jsonl.
If the gateway is unreachable, the snippet is flagged for review (exit 2
in active mode): neither silently passed nor hard-blocking CI.
"""
import sys, os, argparse, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows)

QUESTION_SET = 'codelint-v1'
CODE_MAX = 8000


def read_code(args):
    if args.code_file:
        with open(args.code_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.code or ''
    text = text.strip()
    if len(text) > CODE_MAX:
        text = text[:CODE_MAX] + '...[truncated]'
    return text


def lint(rule, code, cfg):
    if not cfg.get('enabled', True):
        rec = {'rule': rule, 'mode': 'off', 'verdict': 'pass',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('lint.jsonl', rec)
        return 0, rec

    state = (f'Rule to check: {rule}\n'
             f'Code under review:\n{code}')
    questions = {
        'violates': {
            'type': 'boolean',
            'instructions': 'This code violates the rule stated above.',
        },
        'severity': {
            'type': 'score',
            'instructions': 'If the rule is violated, how serious is it?',
            'criteria': [
                '0 none: no violation',
                '1 minor: style-level or low-impact breach',
                '2 serious: correctness, security, or data-handling breach',
            ],
        },
        'route': {
            'type': 'choice',
            'instructions': 'What should happen with this code review?',
            'criteria': {
                'pass': 'the code satisfies the rule',
                'flag_for_review': 'possible violation; a human should look',
                'block': 'clear serious violation; do not merge or ship',
            },
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        # Gateway unreachable: flag, don't pass silently and don't block CI.
        rec = {'rule': rule, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'flag_for_review',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('lint.jsonl', rec)
        return (0 if not mode_allows(cfg) else 2), rec
    answers = data.get('answers', {})
    violates = answers.get('violates', {}).get('probability', 0) >= 0.5
    sev_a = answers.get('severity', {})
    severity = sev_a.get('score', 0)
    route_a = answers.get('route', {})
    choice = route_a.get('choice', 'flag_for_review')
    probs = route_a.get('probabilities') or {}
    ranked = sorted(probs.values(), reverse=True)
    margin = round(ranked[0] - ranked[1], 4) if len(ranked) > 1 else None

    mapping = {'pass': ('pass', 0),
               'flag_for_review': ('flag_for_review', 2),
               'block': ('block', 3)}
    verdict, code = mapping.get(choice, ('flag_for_review', 2))
    # Code owns the combination: a serious severity never passes on a
    # bare "pass" vote.
    overridden = False
    if verdict == 'pass' and severity >= 1.5:
        verdict, code, overridden = 'flag_for_review', 2, True

    rec = {'rule': rule, 'mode': cfg.get('mode', 'shadow'),
           'violates': violates,
           'severity': severity,
           'severity_confidence': sev_a.get('confidence'),
           'severity_distribution': sev_a.get('probabilities') or {},
           'route_choice': choice, 'route_probabilities': probs,
           'route_margin': margin,
           'route_confidence': route_a.get('confidence'),
           'code_override': overridden,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('lint.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev semantic code linting')
    p.add_argument('--rule', required=True,
                   help='Rule to check, in plain English')
    p.add_argument('--code', default='', help='Code snippet to review')
    p.add_argument('--code-file', default='',
                   help='Read the code from a file instead')
    args = p.parse_args()
    if not args.code and not args.code_file:
        print(json.dumps({'error': 'one of --code or --code-file is required'}),
              file=sys.stderr)
        sys.exit(1)
    try:
        code = read_code(args)
    except OSError as e:
        print(json.dumps({'error': f'cannot read code: {e}'}), file=sys.stderr)
        sys.exit(1)
    if not code:
        print(json.dumps({'error': 'code is empty'}), file=sys.stderr)
        sys.exit(1)
    cfg = load_config()
    code_, rec = lint(args.rule, code, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code_)


if __name__ == '__main__':
    main()
