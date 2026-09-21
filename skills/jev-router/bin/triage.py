#!/usr/bin/env python3
"""Jev triage: is a cron/hook finding worth interrupting the user (design f).

Usage:
  triage.py --finding '...' --rule 'standing notification rule, quoted'
            [--topic 'rom-watch'] [--last-notified '2026-09-20T09:12:00+06:00']

Question set: triage-v1 (see references/question-library.md).
Exit codes: 0 = notify_now, 2 = batch_in_digest, 3 = silent_log.
In shadow mode (or when disabled) the verdict is logged and 0 is returned.
During quiet hours notify_now demotes to batch_in_digest unless urgency is 2.
Every verdict appends to logs/triage.jsonl.
If the gateway is unreachable, the finding is batched into the digest (exit 2 in active mode) instead of failing.
"""
import sys, os, argparse, json
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _jev_common import (load_config, evaluate_timed, log_record, model_of,
                         cost_of, mode_allows)

QUESTION_SET = 'triage-v1'


def in_quiet_hours(cfg, now=None):
    qh = cfg.get('quiet_hours') or {}
    try:
        tz = ZoneInfo(qh.get('tz', 'UTC'))
    except Exception:
        return False
    now = now or datetime.now(tz)
    start = qh.get('start', '23:00')
    end = qh.get('end', '07:00')
    cur = now.strftime('%H:%M')
    if start <= end:
        return start <= cur < end
    return cur >= start or cur < end


def triage(finding, rule, topic, last_notified, cfg):
    if not cfg.get('enabled', True):
        rec = {'topic': topic, 'mode': 'off', 'verdict': 'silent_log',
               'reason': 'kill switch: enabled=false',
               'question_set_version': QUESTION_SET}
        log_record('triage.jsonl', rec)
        return 0, rec

    state = (f'Finding: {finding}\nTopic: {topic}\n'
             f'Standing notification rule: {rule}\n'
             f'Last user notification on this topic: {last_notified or "never"}')
    questions = {
        'worth_it': {
            'type': 'boolean',
            'instructions': 'This finding is worth interrupting the user now, given the standing rule above.',
        },
        'urgency': {
            'type': 'score',
            'instructions': 'Rate the urgency of this finding.',
            'criteria': [
                '0 routine: the next digest is fine',
                '1 notable: belongs in the next digest',
                '2 urgent: tell the human now',
            ],
        },
        'route': {
            'type': 'choice',
            'instructions': 'What should happen with this finding?',
            'criteria': {
                'notify_now': 'interrupt the user with a message now',
                'batch_in_digest': 'append to the next digest, do not interrupt',
                'silent_log': 'log only, the user never needs to see this',
            },
        },
    }
    try:
        data, latency_ms = evaluate_timed(state, questions)
    except Exception as e:
        # Gateway unreachable: hold the finding for the next digest rather
        # than dropping it or interrupting the user on a failed evaluation.
        rec = {'topic': topic, 'mode': cfg.get('mode', 'shadow'),
               'verdict': 'batch_in_digest',
               'reason': 'gateway unreachable; no evaluation performed',
               'gateway_error': f'{type(e).__name__}: {e}',
               'question_set_version': QUESTION_SET}
        log_record('triage.jsonl', rec)
        return (0 if not mode_allows(cfg) else 2), rec
    answers = data.get('answers', {})
    worth_it = answers.get('worth_it', {}).get('probability', 0) >= 0.5
    urgency_a = answers.get('urgency', {})
    urgency = urgency_a.get('score', 0)
    route_a = answers.get('route', {})
    choice = route_a.get('choice', 'silent_log')

    mapping = {'notify_now': ('notify_now', 0),
               'batch_in_digest': ('batch_in_digest', 2),
               'silent_log': ('silent_log', 3)}
    verdict, code = mapping.get(choice, ('silent_log', 3))

    quiet = in_quiet_hours(cfg)
    demoted = False
    if verdict == 'notify_now' and quiet and urgency < 1.5:
        verdict, code, demoted = 'batch_in_digest', 2, True

    rec = {'topic': topic, 'mode': cfg.get('mode', 'shadow'),
           'worth_interrupting': worth_it, 'urgency': urgency,
           'urgency_confidence': urgency_a.get('confidence'),
           'route_choice': choice, 'route_confidence': route_a.get('confidence'),
           'quiet_hours': quiet, 'demoted_to_batch': demoted,
           'verdict': verdict, 'model': model_of(data),
           'question_set_version': QUESTION_SET,
           'latency_ms': latency_ms, 'usage': data.get('usage'),
           'cost': cost_of(data)}
    log_record('triage.jsonl', rec)
    if not mode_allows(cfg):
        return 0, rec  # shadow: log only
    return code, rec


def main():
    p = argparse.ArgumentParser(description='Jev finding triage')
    p.add_argument('--finding', required=True)
    p.add_argument('--rule', required=True,
                   help='Standing notification rule for this watch, quoted verbatim')
    p.add_argument('--topic', default='')
    p.add_argument('--last-notified', default='')
    args = p.parse_args()
    cfg = load_config()
    code, rec = triage(args.finding, args.rule, args.topic,
                       args.last_notified, cfg)
    print(json.dumps(rec, indent=2))
    sys.exit(code)


if __name__ == '__main__':
    main()
