"""Shared plumbing for the jev-router bin tools.

load_config()      -> merged config.json over defaults
evaluate_timed()   -> (data, latency_ms) around jev.evaluate
log_record()       -> append a JSON record with model version + latency
mode_allows()      -> True when the tool should honor the verdict
"""
import os, json, time, datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, 'config.json')
LOG_DIR = os.path.join(SKILL_DIR, 'logs')

DEFAULT_CONFIG = {
    'enabled': True,
    'mode': 'shadow',
    'proceed_threshold': 0.6,
    'thresholds': {},
    'auto_escalate': [],
    'hard_deny_tools': [],
    'max_retries': 3,
    'quiet_hours': {'start': '23:00', 'end': '07:00', 'tz': 'UTC'},
}


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    try:
        with open(CONFIG_PATH) as f:
            saved = json.load(f)
        for k, v in saved.items():
            cfg[k] = v
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return cfg


def threshold_for(cfg, action):
    return cfg.get('thresholds', {}).get(action, cfg.get('proceed_threshold', 0.6))


def evaluate_timed(state, questions, model='typesafe-ai/jev', timeout=60):
    from jev import evaluate
    t0 = time.monotonic()
    try:
        data = evaluate(state, questions, model=model, timeout=timeout)
    finally:
        latency_ms = int((time.monotonic() - t0) * 1000)
    return data, latency_ms


def log_record(log_name, record):
    os.makedirs(LOG_DIR, exist_ok=True)
    record['ts'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(os.path.join(LOG_DIR, log_name), 'a') as f:
        f.write(json.dumps(record) + '\n')


def model_of(data):
    return data.get('model')


def cost_of(data):
    return (data.get('providerMetadata') or {}).get('gateway', {}).get('cost')


def mode_allows(cfg):
    """True when verdicts should be honored (active + enabled)."""
    return bool(cfg.get('enabled', True)) and cfg.get('mode') == 'active'


def unreachable_code(cfg):
    """Exit code when the gateway cannot be reached: escalate in active,
    0 in shadow. Every gate CLI uses this so a dead gateway never
    produces a traceback instead of a verdict."""
    return 0 if not mode_allows(cfg) else 3
