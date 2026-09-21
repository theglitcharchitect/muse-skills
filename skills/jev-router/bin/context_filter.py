#!/usr/bin/env python3
"""Jev context filter: keep or drop a candidate context piece before it
reaches the expensive model.

Usage:
  context_filter.py --task '<current task>' --piece '<candidate text>'
  context_filter.py --task '<current task>' --piece-file <path>

Question set: contextfilter-v1 (see references/question-library.md).
Exit codes: 0 = keep, 2 = drop.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/context.jsonl.
If the gateway is unreachable, the piece is kept: dropping context on a
failed evaluation would silently degrade the agent, so the filter fails
open and the miss is logged.
"""
import sys, os, argparse, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows)

QUESTION_SET = 'contextfilter-v1'
PIECE_MAX = 4000


def read_piece(args):
    if args.piece_file:
        with open(args.piece_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.piece or ''
    text = text.strip()
    if len(text) > PIECE_MAX:
        text = text[:PIECE_MAX] + '...[truncated]'
    return text


def filt(task, piece, cfg):
    if not cfg.get('enabled', True):
        rec = {'task': task, 'mode': 'off', 'verdict': 'keep',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('context.jsonl', rec)
        return 0, rec

    state = (f'Current task: {task}\n'
             f'Candidate context piece:\n{piece}')
    questions = {
        'relevance': {
            'type': 'score',
            'instructions': 'Rate how relevant this context piece is to the current task.',
            'criteria': [
                '0 irrelevant: the model does not need this for the next decision',
                '1 background: useful color but not load-bearing',
                '2 needed: the next decision depends on this information',
            ],
        },
        'duplicated': {
            'type': 'boolean',
            'instructions': 'This information is already present in the task context above.',
        },
        'route': {
            'type': 'choice',
            'instructions': 'Should this context piece be passed to the model?',
            'criteria': {
                'keep': 'the piece is relevant and not duplicated',
                'drop': 'the piece is irrelevant, duplicated, or distracting',
            },
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        # Gateway unreachable: fail open. Dropping context on a failed
        # evaluation would silently degrade the agent.
        rec = {'task': task, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'keep',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('context.jsonl', rec)
        return 0, rec
    answers = data.get('answers', {})
    rel_a = answers.get('relevance', {})
    relevance = rel_a.get('score', 0)
    duplicated = answers.get('duplicated', {}).get('probability', 0) >= 0.5
    route_a = answers.get('route', {})
    choice = route_a.get('choice', 'keep')
    probs = route_a.get('probabilities') or {}
    ranked = sorted(probs.values(), reverse=True)
    margin = round(ranked[0] - ranked[1], 4) if len(ranked) > 1 else None

    # Code owns the combination: duplicated pieces drop even if the
    # choice said keep; irrelevant scores drop even on a keep vote.
    if choice == 'drop' or duplicated or relevance < 0.5:
        verdict, code, overridden = 'drop', 2, (choice != 'drop')
    else:
        verdict, code, overridden = 'keep', 0, False

    rec = {'task': task, 'mode': cfg.get('mode', 'shadow'),
           'relevance': relevance,
           'relevance_confidence': rel_a.get('confidence'),
           'relevance_distribution': rel_a.get('probabilities') or {},
           'duplicated': duplicated,
           'route_choice': choice, 'route_probabilities': probs,
           'route_margin': margin,
           'route_confidence': route_a.get('confidence'),
           'code_override': overridden,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('context.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev context relevance filter')
    p.add_argument('--task', required=True, help='Current task the context serves')
    p.add_argument('--piece', default='', help='Candidate context text')
    p.add_argument('--piece-file', default='',
                   help='Read the candidate context from a file instead')
    args = p.parse_args()
    if not args.piece and not args.piece_file:
        print(json.dumps({'error': 'one of --piece or --piece-file is required'}),
              file=sys.stderr)
        sys.exit(1)
    try:
        piece = read_piece(args)
    except OSError as e:
        print(json.dumps({'error': f'cannot read piece: {e}'}), file=sys.stderr)
        sys.exit(1)
    if not piece:
        print(json.dumps({'error': 'context piece is empty'}), file=sys.stderr)
        sys.exit(1)
    cfg = load_config()
    code, rec = filt(args.task, piece, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
