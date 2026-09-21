#!/usr/bin/env python3
"""Jev output judge: score a draft before delivery (design d).

Usage:
  judge.py --draft <file> --rubric sourcing [--rubric-file <json>]
           [--request 'original request'] [--constraints 'hard constraints']

Question set: judge-v1 (see references/question-library.md).
Exit codes: 0 = deliver, 2 = revise, 3 = hold_for_human.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/judge.jsonl.
If the gateway is unreachable, the draft is held for a human (exit 3 in active mode) instead of failing.
"""
import sys, os, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows, unreachable_code)

QUESTION_SET = 'judge-v1'

BUILTIN_RUBRICS = {
    'sourcing': {
        'question': 'quality',
        'instructions': 'Rate the sourcing rigor of this draft.',
        'criteria': [
            '0 unsupported: claims with no evidence',
            '1 asserted: claims stated without backing',
            '2 cited: claims carry named sources',
            '3 independently verified: key claims are cross-checked',
        ],
        'pass_score': 2.0,
    },
}


def build_questions(rubric, rubric_name):
    return {
        rubric['question']: {
            'type': 'score',
            'instructions': rubric['instructions'],
            'criteria': rubric['criteria'],
        },
        'ready': {
            'type': 'boolean',
            'instructions': 'This draft is ready to deliver as-is, meeting every hard constraint.',
        },
        'route': {
            'type': 'choice',
            'instructions': 'What should happen to this draft?',
            'criteria': {
                'deliver': 'quality passes and every hard constraint is met',
                'revise': 'fixable weaknesses: name the failing parts and send back',
                'hold_for_human': 'not safe to deliver or revise without a human decision',
            },
        },
    }


def judge(draft_text, request, constraints, rubric, rubric_name, cfg):
    if not cfg.get('enabled', True):
        rec = {'mode': 'off', 'verdict': 'deliver',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET, 'rubric': rubric_name}
        log_record('judge.jsonl', rec)
        return 0, rec

    state = f'Draft:\n{draft_text}\n\nOriginal request: {request}\nHard constraints: {constraints}'
    questions = build_questions(rubric, rubric_name)
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        # Gateway unreachable: never traceback. Hold for the human; the
        # draft is not delivered on a failed evaluation.
        rec = {'mode': cfg.get('mode', 'shadow'), 'rubric': rubric_name,
               'verdict': 'hold_for_human',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('judge.jsonl', rec)
        return unreachable_code(cfg), rec
    answers = data.get('answers', {})
    score_a = answers.get(rubric['question'], {})
    ready_a = answers.get('ready', {})
    route_a = answers.get('route', {})
    score = score_a.get('score', 0)
    ready = ready_a.get('probability', 0) >= 0.5
    choice = route_a.get('choice', 'hold_for_human')
    conf = route_a.get('confidence', 0)

    if choice == 'deliver' and score >= rubric['pass_score'] and ready:
        verdict, code = 'deliver', 0
    elif choice == 'revise':
        verdict, code = 'revise', 2
    else:
        verdict, code = 'hold_for_human', 3

    weak_rungs = [k for k, p in (score_a.get('probabilities') or {}).items()
                  if float(k) < rubric['pass_score'] and p > 0.3]
    rec = {'mode': cfg.get('mode', 'shadow'), 'rubric': rubric_name,
           'score': score, 'score_confidence': score_a.get('confidence'),
           'ready': ready, 'route_choice': choice,
           'route_confidence': conf, 'weak_rungs': weak_rungs,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('judge.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def read_input_file(path, label):
    """Read a CLI input file; exit 1 with a clean JSON error instead of a traceback."""
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        print(json.dumps({'error': f'{label} unreadable: {path}: {e.strerror or e}'}),
              file=sys.stderr)
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description='Jev draft judge')
    p.add_argument('--draft', required=True, help='Path to the draft file')
    p.add_argument('--rubric', default='sourcing',
                   choices=list(BUILTIN_RUBRICS))
    p.add_argument('--rubric-file', help='Custom rubric JSON (overrides --rubric)')
    p.add_argument('--request', default='', help='The original request')
    p.add_argument('--constraints', default='', help='Hard constraints the draft must meet')
    args = p.parse_args()

    draft_text = read_input_file(args.draft, 'draft file')
    if args.rubric_file:
        rubric_text = read_input_file(args.rubric_file, 'rubric file')
        try:
            rubric = json.loads(rubric_text)
        except json.JSONDecodeError as e:
            print(json.dumps({'error': f'rubric file is not valid JSON: {e}'}),
                  file=sys.stderr)
            sys.exit(1)
        rubric_name = os.path.basename(args.rubric_file)
    else:
        rubric = BUILTIN_RUBRICS[args.rubric]
        rubric_name = args.rubric

    cfg = load_config()
    code, rec = judge(draft_text, args.request, args.constraints,
                      rubric, rubric_name, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
