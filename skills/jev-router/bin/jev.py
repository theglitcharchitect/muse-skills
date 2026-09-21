#!/usr/bin/env python3
"""Jev client: typed evaluations (Choice / Score / Boolean) via Vercel AI Gateway.

Usage:
  jev.py evaluate --state '...' --questions '{"q1": {"type": "boolean", "instructions": "..."}}'
  jev.py smoke

Auth, in order of preference:
  1. Hatch runtime: the stored `custom.vercel` credential via the surrogate
     exchange (only available on Hatch; skipped silently elsewhere).
  2. Env var VERCEL_AI_GATEWAY_KEY (or JEV_GATEWAY_KEY): sent as a
     Bearer token to the gateway.

Never prints or persists raw credentials.
"""
import os, sys, json, argparse, urllib.request, urllib.error

BASE = 'https://ai-gateway.vercel.sh'
ALLOWED = ['ai-gateway.vercel.sh']
MODEL = 'typesafe-ai/jev'


def _attach_auth(req):
    # Hatch surrogate path, when the helper exists.
    try:
        sys.path.insert(0, '/opt/hatch/skills/skill-creator/bin')
        from dynamic_credentials import add_surrogate_to_request
        add_surrogate_to_request(req, 'custom.vercel', allowed_hosts=ALLOWED)
        return
    except ImportError:
        pass
    # Portable fallback: caller-supplied gateway key.
    key = os.environ.get('VERCEL_AI_GATEWAY_KEY') or os.environ.get('JEV_GATEWAY_KEY')
    if not key:
        raise SystemExit(
            'No gateway auth: set VERCEL_AI_GATEWAY_KEY (or JEV_GATEWAY_KEY), '
            'or connect custom.vercel on Hatch.'
        )
    req.add_header('Authorization', 'Bearer ' + key)


class GatewayError(Exception):
    """The gateway call failed (HTTP error, timeout, DNS, bad response).
    Raised instead of SystemExit so library callers can handle it; the CLI
    commands below convert it to a clean SystemExit message."""


def evaluate(state, questions, model=MODEL, timeout=60):
    payload = {'model': model, 'state': state, 'questions': questions}
    req = urllib.request.Request(
        BASE + '/v1/evaluate',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
    )
    _attach_auth(req)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        raise GatewayError(f'Gateway HTTP {e.code}: {body}')
    except urllib.error.URLError as e:
        raise GatewayError(f'Gateway unreachable: {e.reason}')
    return data


def cmd_evaluate(args):
    try:
        questions = json.loads(args.questions)
    except json.JSONDecodeError as e:
        raise SystemExit(f'--questions must be valid JSON: {e}')
    try:
        data = evaluate(args.state, questions, model=args.model)
    except GatewayError as e:
        raise SystemExit(str(e))
    print(json.dumps({
        'model': data.get('model'),
        'answers': data.get('answers'),
        'usage': data.get('usage'),
        'cost': (data.get('providerMetadata') or {}).get('gateway', {}).get('cost'),
    }, indent=2))


def cmd_smoke(args):
    try:
        data = evaluate(
            'The build failed with exit code 1.',
            {'passed': {'type': 'boolean', 'instructions': 'Did the build succeed?'}},
        )
    except GatewayError as e:
        raise SystemExit(str(e))
    ans = data.get('answers', {}).get('passed', {})
    ok = ans.get('probability', 1) < 0.5
    print(json.dumps({'ok': ok, 'answers': data.get('answers'),
                      'cost': (data.get('providerMetadata') or {}).get('gateway', {}).get('cost')}, indent=2))
    sys.exit(0 if ok else 1)


def main():
    p = argparse.ArgumentParser(description='Jev typed-evaluation client')
    sub = p.add_subparsers(dest='cmd', required=True)
    pe = sub.add_parser('evaluate', help='Run a typed evaluation')
    pe.add_argument('--state', required=True, help='State string, object, or array as JSON/text')
    pe.add_argument('--questions', required=True, help='Questions object as JSON string')
    pe.add_argument('--model', default=MODEL)
    pe.set_defaults(fn=cmd_evaluate)
    ps = sub.add_parser('smoke', help='Health check: boolean eval with known answer')
    ps.set_defaults(fn=cmd_smoke)
    args = p.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
