#!/usr/bin/env python3
"""Muse + Jev: a four-act terminal demo.

Walks through Jev in action using the real gate scripts from
skills/jev-router/bin:

  Act 1  Boolean  safety gate on a risky shell command
  Act 2  Choice   pick between two research plans, with probabilities
  Act 3  Score    judge a draft against an evidence rubric
  Act 4  Router   shadow-mode gating of an expensive browser run

Needs no key. Without VERCEL_AI_GATEWAY_KEY (or JEV_GATEWAY_KEY) it runs
against a deterministic mock gateway that returns Jev-shaped responses,
so every run prints the same verdicts. Set the key and it talks to the
real Vercel AI Gateway instead; nothing else changes.

Usage:
  python3 demo/run.py
"""

import importlib.util
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(REPO_ROOT, "skills", "jev-router", "bin")
sys.path.insert(0, BIN_DIR)

import jev  # noqa: E402  (imported after sys.path is fixed)
from _jev_common import load_config, evaluate_timed  # noqa: E402

KEY = os.environ.get("VERCEL_AI_GATEWAY_KEY") or os.environ.get("JEV_GATEWAY_KEY")
LIVE = bool(KEY)


def load_module(name):
    path = os.path.join(BIN_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Deterministic mock gateway.
#
# Returns the same Jev-shaped response shape the real gateway returns,
# chosen by keyword on the state text. No network, no randomness:
# every run prints identical verdicts. This exists so the demo works
# for anyone who clones the repo, and so CI can run it.
# ---------------------------------------------------------------------------

MOCK = {"model": "mock/jev-deterministic", "usage": {"demo": True}}


def mock_evaluate(state, questions, model="typesafe-ai/jev", timeout=60):
    s = state.lower()
    answers = {}
    for qid, q in questions.items():
        qtype = q.get("type")
        if qtype == "boolean":
            answers[qid] = mock_boolean(s, q)
        elif qtype == "choice":
            answers[qid] = mock_choice(s, q)
        elif qtype == "score":
            answers[qid] = mock_score(s, q)
        else:
            answers[qid] = {"probability": 0.5, "confidence": 0.1}
    return {"answers": answers, "model": MOCK["model"], "usage": MOCK["usage"]}


def mock_boolean(s, q):
    instr = q.get("instructions", "").lower()
    if "safe to execute" in instr:
        if "rm -rf" in s:
            return {"value": False, "probability": 0.03, "confidence": 0.94}
        return {"value": True, "probability": 0.9, "confidence": 0.8}
    if "ready to deliver" in instr:
        return {"value": False, "probability": 0.18, "confidence": 0.7}
    if "hard or impossible to undo" in instr:
        return {"value": False, "probability": 0.12, "confidence": 0.85}
    return {"value": True, "probability": 0.6, "confidence": 0.5}


def mock_choice(s, q):
    criteria = q.get("criteria", {})
    instr = q.get("instructions", "").lower()
    if "plan" in instr or "plan_a" in s:
        return {"choice": "plan_b",
                "probabilities": {"plan_b": 0.78, "plan_a": 0.22},
                "confidence": 0.74}
    if "tool call" in instr:
        if "rm -rf" in s:
            return {"choice": "block",
                    "probabilities": {"block": 0.88, "escalate": 0.10,
                                      "approve_with_warning": 0.02,
                                      "approve": 0.0},
                    "confidence": 0.9}
        return {"choice": "approve",
                "probabilities": {"approve": 0.9, "approve_with_warning": 0.08,
                                  "escalate": 0.02, "block": 0.0},
                "confidence": 0.85}
    if "draft" in instr:
        return {"choice": "revise",
                "probabilities": {"revise": 0.72, "hold_for_human": 0.20,
                                  "deliver": 0.08},
                "confidence": 0.7}
    if "perform this action" in instr:
        if "browser" in s:
            return {"choice": "escalate",
                    "probabilities": {"escalate": 0.81, "proceed": 0.12,
                                      "skip": 0.07},
                    "confidence": 0.77}
        return {"choice": "proceed",
                "probabilities": {"proceed": 0.85, "skip": 0.1,
                                  "escalate": 0.05},
                "confidence": 0.8}
    first = sorted(criteria.keys())[0] if criteria else "unknown"
    return {"choice": first, "probabilities": {first: 0.6}, "confidence": 0.5}


def mock_score(s, q):
    if "risk" in q.get("instructions", "").lower():
        if "rm -rf" in s:
            return {"score": 2, "probabilities": {"0": 0.02, "1": 0.08,
                                                 "2": 0.90},
                    "confidence": 0.92}
        return {"score": 0, "probabilities": {"0": 0.9, "1": 0.08, "2": 0.02},
                "confidence": 0.85}
    if "draft" in s or "evidence" in q.get("instructions", "").lower():
        return {"score": 1, "probabilities": {"0": 0.10, "1": 0.65, "2": 0.20,
                                              "3": 0.05},
                "confidence": 0.68}
    return {"score": 1, "probabilities": {"0": 0.2, "1": 0.6, "2": 0.2},
            "confidence": 0.6}


# ---------------------------------------------------------------------------
# Presentation helpers. Plain text only.
# ---------------------------------------------------------------------------

WIDTH = 64


def rule():
    print("-" * WIDTH)


def act(n, title, setup):
    rule()
    print(f"ACT {n}  {title}")
    rule()
    print(setup)
    print()


def verdict_line(label, value):
    print(f"  {label:<18} {value}")


def probs(probs):
    return ", ".join(f"{k} {v:.2f}" for k, v in
                     sorted(probs.items(), key=lambda kv: -kv[1]))


# ---------------------------------------------------------------------------
# The four acts.
# ---------------------------------------------------------------------------

def act1_safety(safety_gate, cfg):
    act(1, "Boolean: the safety gate on a risky command",
        "The agent wants to run a shell command before a weekly sync.\n"
        "The safety gate classifies the call before it executes.")
    print("  tool:    shell_exec")
    print("  args:    rm -rf ~/workspace/drafts")
    print('  intent:  "Clean up old draft files before the weekly sync."')
    print()
    code, rec = safety_gate.gate(
        "shell_exec", "rm -rf ~/workspace/drafts",
        "Clean up old draft files before the weekly sync.", cfg)
    verdict_line("risk score", f"{rec['risk_score']} / 2 "
                 f"(confidence {rec['risk_confidence']:.2f})")
    verdict_line("safe to run", f"p = {rec['safe_probability']:.2f}")
    verdict_line("route", f"{rec['route_choice']} "
                 f"[{probs(rec['route_probabilities'])}]")
    verdict_line("Jev verdict", rec["verdict"].upper())
    if not cfg.get("mode") == "active":
        print()
        print("  Shadow mode: the verdict is logged, the call would proceed,")
        print("  and you calibrate against the log. In active mode this call")
        print("  would have been blocked (exit 2).")
    print()
    print(f"  logged to skills/jev-router/logs/safety.jsonl "
          f"({rec['latency_ms']} ms, model {rec['model']})")


def act2_choice():
    act(2, "Choice: two plans, one decision",
        "The agent needs current pricing for a research question.\n"
        "Two plans are on the table. Jev picks, with probabilities.")
    print("  Plan A: full browser sweep, 12 page loads, about 9 minutes,")
    print("          roughly $0.40 in gateway and compute cost.")
    print("  Plan B: 2 targeted API calls against cached docs, 40 seconds,")
    print("          roughly $0.02.")
    print()
    state = ("Research strategy decision. Plan A: full browser sweep, 12 page "
             "loads, ~$0.40 estimated cost, 9 minutes. Plan B: 2 targeted API "
             "calls against cached docs, ~$0.02, 40 seconds.")
    questions = {"pick": {
        "type": "choice",
        "instructions": "Which plan should the agent run?",
        "criteria": {
            "plan_a": "the full browser sweep is worth the cost",
            "plan_b": "the targeted API calls are sufficient",
        }}}
    data, latency_ms = evaluate_timed(state, questions)
    a = data["answers"]["pick"]
    verdict_line("Jev choice", a["choice"].replace("_", " ").upper())
    verdict_line("probabilities", probs(a["probabilities"]))
    verdict_line("confidence", f"{a.get('confidence', 0):.2f}")
    print()
    print(f"  ({latency_ms} ms, model {data.get('model')})")
    print("  The margin matters: 0.78 / 0.22 is a decision.")
    print("  0.51 / 0.49 would be a coin flip wearing a verdict.")


def act3_judge(judge_mod, cfg):
    act(3, "Score: a draft against an evidence rubric",
        "The agent drafted a product announcement. Before it goes out,\n"
        "the judge scores its sourcing and routes it.")
    draft_path = os.path.join(REPO_ROOT, "demo", "draft.txt")
    with open(draft_path) as f:
        draft = f.read()
    print("  --- draft (demo/draft.txt) ---")
    for line in draft.strip().splitlines():
        print("  " + line)
    print("  ------------------------------")
    print()
    rubric = {
        "question": "evidence",
        "instructions": "Rate the evidence backing of this draft.",
        "criteria": [
            "0 unsupported: claims with no evidence",
            "1 asserted: claims stated without backing",
            "2 cited: claims carry named sources",
            "3 independently verified: key claims are cross-checked",
        ],
        "pass_score": 2.0,
    }
    code, rec = judge_mod.judge(
        draft,
        request="Announce the new release in one paragraph.",
        constraints="Every performance claim needs a named source.",
        rubric=rubric, rubric_name="demo-evidence", cfg=cfg)
    verdict_line("evidence score", f"{rec['score']} / 3 "
                 f"(confidence {rec['score_confidence']:.2f})")
    verdict_line("weak rungs", ", ".join(rec["weak_rungs"]) or "none")
    verdict_line("ready to deliver", str(rec["ready"]))
    verdict_line("Jev verdict", rec["verdict"].upper())
    print()
    print("  The draft goes back for revision with the weak rungs named,")
    print("  instead of shipping an unverified superlative.")
    print()
    print(f"  logged to skills/jev-router/logs/judge.jsonl "
          f"({rec['latency_ms']} ms, model {rec['model']})")


def act4_router(router_mod, cfg):
    act(4, "Router: shadow mode gates an expensive browser run",
        "The agent proposes a 12-page browser sweep. The usage router\n"
        "asks Jev whether it is worth running. The router is in shadow\n"
        "mode: it logs the decision and lets the action through.")
    code, rec = router_mod.route(
        "browser_run",
        "Sweep 12 product pages for current pricing (est. 9 min, ~$0.40).",
        cfg)
    verdict_line("Jev choice", rec["choice"])
    verdict_line("probabilities", probs(rec["choice_probabilities"]))
    verdict_line("margin", rec["choice_margin"])
    verdict_line("threshold", f"{rec['threshold']:.2f}")
    verdict_line("Jev decision", rec["decision"].upper())
    print()
    print("  Shadow mode: the run proceeds, the decision is logged.")
    print("  After a week of these logs you know your real thresholds,")
    print("  and only then do you flip config.json to active.")
    print()
    print(f"  logged to skills/jev-router/logs/router.jsonl "
          f"({rec['latency_ms']} ms, model {rec['model']})")


def main():
    print()
    print("  MUSE + JEV: four decisions, one demo")
    if LIVE:
        print("  gateway: live (VERCEL_AI_GATEWAY_KEY is set)")
    else:
        print("  gateway: deterministic mock (no key set, no network, "
              "same verdicts every run)")
    print()

    if not LIVE:
        jev.evaluate = mock_evaluate

    safety_gate = load_module("safety_gate")
    judge_mod = load_module("judge")
    router_mod = load_module("router")
    cfg = load_config()
    print(f"  router config: mode={cfg.get('mode')}, "
          f"enabled={cfg.get('enabled')}")
    print()

    act1_safety(safety_gate, cfg)
    print()
    act2_choice()
    print()
    act3_judge(judge_mod, cfg)
    print()
    act4_router(router_mod, cfg)
    print()
    rule()
    print("  Done. Four typed evaluations, three real gate scripts,")
    print("  one philosophy: Jev advises, you authorize.")
    print("  Next: docs/shadow-mode.md")
    rule()
    print()


if __name__ == "__main__":
    main()
