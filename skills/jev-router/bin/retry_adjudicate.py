#!/usr/bin/env python3
"""Jev retry adjudicator: decide what to do about a failed action (design b).

Usage:
  retry_adjudicate.py --action <name> --error <text> [--error-file <path>]
                       --attempt <n>

The attempt cap (config max_retries) is enforced in CODE before Jev is
called; Jev never decides whether a cap exists.
Question set: retry-v1 (see references/question-library.md).
Exit codes: 0 = retry_same, 2 = abandon, 3 = escalate,
            4 = replan_different_approach.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/retry.jsonl.
If the gateway is unreachable, the retry escalates (exit 3 in active mode) instead of failing.
"""
import sys, os, argparse, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows, unreachable_code)

QUESTION_SET = 'retry-v1'


def adjudicate(action, error_text, attempt, cfg):
    max_retries = cfg.get('max_retries', 3)
    if attempt >= max_retries:
        rec = {'action': action, 'attempt': attempt, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'abandon',
               'reason': f'code-enforced cap: attempt {attempt} >= max_retries {max_retries}',
               'question_set_version': QUESTION_SET}
        log_record('retry.jsonl', rec)
        return 0 if not mode_allows(cfg) else 2, rec

    if not cfg.get('enabled', True):
        rec = {'action': action, 'attempt': attempt, 'mode': 'off',
               'verdict': 'retry_same',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('retry.jsonl', rec)
        return 0, rec

    state = (f'Failed action: {action}\nAttempt number: {attempt} of {max_retries}\n'
             f'Error output (trimmed):\n{error_text[:2000]}')
    questions = {
        'route': {
            'type': 'choice',
            'instructions': 'What should the agent do about this failed action?',
            'criteria': {
                'retry_same': 'the failure looks transient; running the identical action again is reasonable',
                'replan': 'the approach itself is wrong; a different plan is needed',
                'escalate': 'a human should see this error before anything else runs',
                'abandon': 'further attempts are wasted; log the outcome and close the item',
            },
        },
        'transient': {
            'type': 'boolean',
            'instructions': 'The failure looks transient (rate limit, timeout, flaky network) rather than structural.',
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        rec = {'action': action, 'attempt': attempt,
               'mode': cfg.get('mode', 'shadow'), 'verdict': 'escalate',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('retry.jsonl', rec)
        return unreachable_code(cfg), rec
    answers = data.get('answers', {})
    route_a = answers.get('route', {})
    choice = route_a.get('choice', 'escalate')
    conf = route_a.get('confidence', 0)
    transient = answers.get('transient', {}).get('probability', 0) >= 0.5

    mapping = {'retry_same': ('retry_same', 0), 'replan': ('replan', 4),
               'escalate': ('escalate', 3), 'abandon': ('abandon', 2)}
    verdict, code = mapping.get(choice, ('escalate', 3))

    rec = {'action': action, 'attempt': attempt, 'max_retries': max_retries,
           'mode': cfg.get('mode', 'shadow'), 'choice': choice,
           'choice_confidence': conf, 'transient': transient,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('retry.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev retry adjudicator')
    p.add_argument('--action', required=True)
    p.add_argument('--error', default='')
    p.add_argument('--error-file')
    p.add_argument('--attempt', type=int, required=True)
    args = p.parse_args()
    error_text = args.error
    if args.error_file:
        try:
            with open(args.error_file) as f:
                error_text = f.read()
        except OSError as e:
            print(json.dumps({'error': f'error file unreadable: {args.error_file}: {e.strerror or e}'}),
                  file=sys.stderr)
            sys.exit(1)
    cfg = load_config()
    code, rec = adjudicate(args.action, error_text, args.attempt, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
