#!/usr/bin/env python3
"""Jev question-quality gate: is a question decision-shaped before it is asked.

Usage:
  ask_check.py --questions '<json>' [--threshold 0.7]

The JSON maps a question name to its spec:
  {"retry_q": {"type": "boolean",
               "instructions": "Should this be retried?",
               "criteria": {}}}

Two layers. Code first (exact rules, no Jev call):
  1. known_type: type is boolean, choice, or score.
  2. has_instructions: instructions present, at least 10 chars.
  3. bounded_options: choice has 2-8 options with non-empty criteria;
     score has 2+ non-empty criteria; boolean needs none.
  4. not_vague: instructions carry none of the open-ended markers
     ("what should i do", "what do you think", "tell me about",
      "thoughts on", "anything else", "etc.", "brainstorm").
  5. no_double_negative: fewer than 2 negation words in instructions
     (heuristic, labeled as such).
Any code failure -> reject with the failed checks named, no Jev call.
All code checks pass -> one fanned-out Jev request with a well_formed
boolean per question as backstop.

Question set: askcheck-v1 (see references/question-library.md).
Exit codes: 0 = ask, 2 = reject, 3 = hold_for_review.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
Every verdict appends to logs/askcheck.jsonl.
"""
import sys, os, argparse, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows, threshold_for)

QUESTION_SET = 'askcheck-v1'
KNOWN_TYPES = ('boolean', 'choice', 'score')
VAGUE_MARKERS = ('what should i do', 'what do you think', 'tell me about',
                 'thoughts on', 'anything else', 'etc.', 'brainstorm')
NEGATION_RE = re.compile(r"\b(not|never|no)\b|n't\b", re.IGNORECASE)


def sanitize(name):
    s = re.sub(r'[^0-9a-zA-Z_]', '_', name) or 'q'
    return s if not s[0].isdigit() else 'q_' + s


def code_checks(name, spec):
    """Return a list of failed check names (empty = pass)."""
    failed = []
    qtype = spec.get('type')
    if qtype not in KNOWN_TYPES:
        failed.append('known_type')
    instr = spec.get('instructions') or ''
    if not isinstance(instr, str) or len(instr.strip()) < 10:
        failed.append('has_instructions')
    criteria = spec.get('criteria')
    if qtype == 'choice':
        if not isinstance(criteria, dict) or not (2 <= len(criteria) <= 8):
            failed.append('bounded_options')
        elif any(not str(v).strip() for v in criteria.values()):
            failed.append('bounded_options')
    elif qtype == 'score':
        items = criteria if isinstance(criteria, list) else []
        if len([c for c in items if str(c).strip()]) < 2:
            failed.append('bounded_options')
    low = instr.lower()
    if any(m in low for m in VAGUE_MARKERS):
        failed.append('not_vague')
    if len(NEGATION_RE.findall(instr)) >= 2:
        failed.append('no_double_negative')
    return failed


def check(questions, threshold, cfg):
    if not cfg.get('enabled', True):
        rec = {'mode': 'off', 'verdict': 'ask',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('askcheck.jsonl', rec)
        return 0, rec

    if not questions:
        rec = {'mode': cfg.get('mode', 'shadow'), 'verdict': 'reject',
               'reason': 'caller error: no questions supplied',
               'question_set_version': QUESTION_SET}
        log_record('askcheck.jsonl', rec)
        return 2, rec

    per_question = {}
    for name, spec in questions.items():
        per_question[name] = {'failed': code_checks(name, spec or {})}

    rejected = {n: r for n, r in per_question.items() if r['failed']}
    if rejected:
        # Code owns the rejection: no Jev call is spent on a malformed
        # question.
        rec = {'mode': cfg.get('mode', 'shadow'), 'verdict': 'reject',
               'questions': list(questions),
               'failed_checks': {n: r['failed'] for n, r in rejected.items()},
               'jev_called': False,
               'question_set_version': QUESTION_SET}
        log_record('askcheck.jsonl', rec)
        return (0 if not mode_allows(cfg) else 2), rec

    # Backstop: one fanned-out Jev request, one boolean per question.
    state_lines = []
    keys = {}
    for name, spec in questions.items():
        key = 'wf_' + sanitize(name)
        keys[name] = key
        state_lines.append(
            f"Question '{name}': type={spec.get('type')}\n"
            f"Instructions: {spec.get('instructions')}\n"
            f"Criteria: {json.dumps(spec.get('criteria'))}")
    state = ('Candidate Jev questions to review:\n\n' + '\n\n'.join(state_lines))
    jev_questions = {
        key: {'type': 'boolean',
              'instructions': (
                  f"The question '{name}' is specific and bounded: it asks "
                  'for a decision (yes/no, a pick from a list, or a '
                  'placement on a defined scale), not open-ended text.')}
        for name, key in keys.items()
    }
    try:
        data, latency_ms = evaluate_timed(state, jev_questions)
    except Exception as e:
        rec = {'mode': cfg.get('mode', 'shadow'), 'verdict': 'hold_for_review',
               'reason': 'gateway unreachable; no backstop evaluation',
               'gateway_error': f'{type(e).__name__}: {e}',
               'questions': list(questions),
               'code_checks': 'all passed',
               'question_set_version': QUESTION_SET}
        log_record('askcheck.jsonl', rec)
        return (0 if not mode_allows(cfg) else 3), rec

    answers = data.get('answers', {})
    weak = {}
    for name, key in keys.items():
        p = answers.get(key, {}).get('probability', 0)
        per_question[name]['well_formed_probability'] = p
        if p < threshold:
            weak[name] = p

    verdict, code = ('ask', 0) if not weak else ('hold_for_review', 3)
    rec = {'mode': cfg.get('mode', 'shadow'), 'verdict': verdict,
           'questions': list(questions),
           'code_checks': 'all passed',
           'well_formed': {n: per_question[n].get('well_formed_probability')
                           for n in questions},
           'weak_questions': weak, 'threshold': threshold,
           'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('askcheck.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev question-quality gate')
    p.add_argument('--questions', required=True,
                   help='JSON: {"name": {"type": ..., "instructions": ..., "criteria": ...}}')
    p.add_argument('--threshold', type=float, default=None,
                   help='well_formed probability floor (default: thresholds.askcheck)')
    args = p.parse_args()
    cfg = load_config()
    threshold = args.threshold if args.threshold is not None else threshold_for(cfg, 'askcheck')
    try:
        questions = json.loads(args.questions)
    except json.JSONDecodeError as e:
        print(json.dumps({'verdict': 'reject',
                          'reason': f'caller error: invalid JSON: {e}'}))
        sys.exit(2)
    code, rec = check(questions, threshold, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
