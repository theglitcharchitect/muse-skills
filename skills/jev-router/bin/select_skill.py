#!/usr/bin/env python3
"""Jev skill selection: which skill should handle the task (select-v1).

Usage:
  select_skill.py --task '<task description>'
                  --candidate '<name>: <one-line capability>' [--candidate ...]
                  [--context '<extra context>']

Question set: select-v1 (see references/question-library.md).
Exit codes: 0 = selected (winner named), 2 = no_fit, 3 = escalate.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/select.jsonl.
If the gateway is unreachable, escalate in active mode (exit 3); 0 in shadow.

Code owns the menu: one candidate is selected directly without calling Jev
(a selection among fewer than two is not a decision); zero candidates is a
caller error; more than eight candidates are truncated with the cut logged.
Checker hygiene: the state carries the task and the candidate capability
lines only, never the worker's reasoning about which to pick.
"""
import sys, os, argparse, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows, threshold_for)

QUESTION_SET = 'select-v1'
MAX_CANDIDATES = 8


def parse_candidates(raw):
    out = []
    for item in raw:
        name, sep, cap = item.partition(':')
        name, cap = name.strip(), cap.strip()
        if not name:
            continue
        out.append({'name': name, 'capability': cap or '(no description given)'})
    return out


def select(task, candidates, context, cfg):
    if not cfg.get('enabled', True):
        rec = {'task': task, 'mode': 'off', 'verdict': 'no_fit',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('select.jsonl', rec)
        return 0, rec

    if not candidates:
        rec = {'task': task, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'no_fit', 'reason': 'caller error: no candidates',
               'question_set_version': QUESTION_SET}
        log_record('select.jsonl', rec)
        return 2, rec

    if len(candidates) == 1:
        # Not a decision: code selects the only candidate, no Jev call.
        rec = {'task': task, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'selected', 'winner': candidates[0]['name'],
               'reason': 'code decision: single candidate, no Jev call',
               'question_set_version': QUESTION_SET}
        log_record('select.jsonl', rec)
        return 0, rec

    truncated = []
    if len(candidates) > MAX_CANDIDATES:
        truncated = [c['name'] for c in candidates[MAX_CANDIDATES:]]
        candidates = candidates[:MAX_CANDIDATES]

    menu = '\n'.join(f"- {c['name']}: {c['capability']}" for c in candidates)
    state = f'Task: {task}\nCandidate skills:\n{menu}'
    if context:
        state += f'\nExtra context: {context}'
    criteria = {c['name']: f"{c['capability']}" for c in candidates}
    criteria['none_abstain'] = 'no candidate is a good fit for this task'
    questions = {
        'best': {
            'type': 'choice',
            'instructions': 'Which candidate skill is the best fit for this task?',
            'criteria': criteria,
        },
        'clear_winner': {
            'type': 'boolean',
            'instructions': 'One candidate is clearly the best fit for this task, not a close call.',
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        rec = {'task': task, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'escalate',
               'reason': 'gateway unreachable; orchestrator decides',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('select.jsonl', rec)
        return (0 if not mode_allows(cfg) else 3), rec

    answers = data.get('answers', {})
    best_a = answers.get('best', {})
    winner = best_a.get('choice', 'none_abstain')
    probs = best_a.get('probabilities') or {}
    winner_p = probs.get(winner, 0)
    ranked = sorted(probs.values(), reverse=True)
    margin = round(ranked[0] - ranked[1], 4) if len(ranked) > 1 else None
    clear = answers.get('clear_winner', {}).get('probability', 0) >= 0.5
    threshold = threshold_for(cfg, 'select')

    if winner == 'none_abstain':
        verdict, code = 'no_fit', 2
    elif winner_p >= threshold and clear:
        verdict, code = 'selected', 0
    else:
        verdict, code = 'escalate', 3

    rec = {'task': task, 'candidates': [c['name'] for c in candidates],
           'truncated': truncated, 'mode': cfg.get('mode', 'shadow'),
           'winner': winner, 'winner_probability': winner_p,
           'choice_probabilities': probs, 'choice_margin': margin,
           'clear_winner': clear, 'threshold': threshold,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('select.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev skill selection')
    p.add_argument('--task', required=True)
    p.add_argument('--candidate', action='append', default=[],
                   help="'<name>: <one-line capability>', repeatable")
    p.add_argument('--context', default='')
    args = p.parse_args()
    cfg = load_config()
    code, rec = select(args.task, parse_candidates(args.candidate),
                       args.context, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
