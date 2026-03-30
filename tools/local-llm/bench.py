#!/usr/bin/env python3
"""
Benchmark harness for local-llm/call.py.

Runs bench_tasks/*.json task files against the local LLM, scores each response,
and writes a Markdown + JSON report. Supports comparing two models side-by-side.

Usage:
  python3 bench.py
  python3 bench.py --categories smoke
  python3 bench.py --categories coding,tests
  python3 bench.py --compare qwen/other-model
  python3 bench.py --output ./my-results/

Scoring per task (0-100 before difficulty multiplier):
  +40  All expected_patterns found in output (case-insensitive)
  +20  No forbidden_patterns found in output (case-insensitive)
  +30  Syntax check passes (Python AST parse when syntax_check="python")
  +10  Output length is reasonable (≥ 10 chars, ≤ max_tokens * 8 chars)

Difficulty multiplier: easy=1.0, medium=1.2, hard=1.5
Category score = weighted mean of task scores in category.
Overall score  = weighted mean of all task scores.
"""

import argparse
import ast
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(SCRIPT_DIR, "bench_tasks")
CALL_PY = os.path.join(SCRIPT_DIR, "call.py")

DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.2, "hard": 1.5}
CATEGORY_ORDER = ["coding", "tests", "summarize", "docs", "refactor", "smoke"]


# ─────────────────────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────────────────────

def score_task(task: dict, output: str) -> dict:
    """Score a single task output. Returns a dict with score and breakdown."""
    output_lower = output.lower()
    breakdown = {}

    # +40: all expected_patterns present
    expected = task.get("expected_patterns", [])
    if expected:
        hits = [p for p in expected if p.lower() in output_lower]
        pattern_score = 40 if len(hits) == len(expected) else int(40 * len(hits) / len(expected))
        breakdown["expected_patterns"] = {
            "score": pattern_score,
            "max": 40,
            "hits": hits,
            "misses": [p for p in expected if p.lower() not in output_lower],
        }
    else:
        pattern_score = 40
        breakdown["expected_patterns"] = {"score": 40, "max": 40, "hits": [], "misses": []}

    # +20: no forbidden_patterns
    forbidden = task.get("forbidden_patterns", [])
    if forbidden:
        violations = [p for p in forbidden if p.lower() in output_lower]
        forbidden_score = 0 if violations else 20
        breakdown["forbidden_patterns"] = {
            "score": forbidden_score,
            "max": 20,
            "violations": violations,
        }
    else:
        forbidden_score = 20
        breakdown["forbidden_patterns"] = {"score": 20, "max": 20, "violations": []}

    # +30: syntax check
    syntax_check = task.get("syntax_check", "none")
    if syntax_check == "python":
        try:
            ast.parse(output)
            syntax_score = 30
            breakdown["syntax_check"] = {"score": 30, "max": 30, "passed": True}
        except SyntaxError as e:
            syntax_score = 0
            breakdown["syntax_check"] = {"score": 0, "max": 30, "passed": False, "error": str(e)}
    else:
        syntax_score = 30
        breakdown["syntax_check"] = {"score": 30, "max": 30, "passed": True, "skipped": True}

    # +10: reasonable length
    max_chars = task.get("max_tokens", 512) * 8
    length_ok = 10 <= len(output) <= max_chars
    length_score = 10 if length_ok else 0
    breakdown["length"] = {
        "score": length_score,
        "max": 10,
        "chars": len(output),
        "max_chars": max_chars,
    }

    raw_score = pattern_score + forbidden_score + syntax_score + length_score
    difficulty = task.get("difficulty", "easy")
    weight = DIFFICULTY_WEIGHT.get(difficulty, 1.0)
    weighted_score = raw_score * weight

    return {
        "raw_score": raw_score,
        "weighted_score": weighted_score,
        "weight": weight,
        "breakdown": breakdown,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Task runner
# ─────────────────────────────────────────────────────────────────────────────

def run_task(task: dict, model: Optional[str] = None, verbose: bool = False) -> dict:
    """Run call.py for a single task. Returns result dict."""
    # Use explicit task_type if set; fall back to category-based mapping.
    task_type = task.get("task_type") or _category_to_task_type(task.get("category", "coding"))
    cmd = [
        sys.executable,
        CALL_PY,
        "--task-type", task_type,
        "--prompt", task["prompt"],
        "--max-tokens", str(task.get("max_tokens", 512)),
        "--no-cache",
    ]
    if model:
        cmd += ["--model", model]

    if verbose:
        print(f"  Running {task['id']} ({task.get('difficulty','easy')})... ", end="", flush=True)

    t0 = time.monotonic()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        if verbose:
            print("TIMEOUT")
        return {
            "task_id": task["id"],
            "task_name": task.get("name", ""),
            "exit_code": -1,
            "output": "",
            "stderr": "process timeout after 600s",
            "latency": elapsed,
            "score": None,
            "error": "timeout",
        }

    elapsed = time.monotonic() - t0
    output = result.stdout.rstrip("\n")
    scoring = score_task(task, output)

    if verbose:
        status = f"score={scoring['raw_score']}/100 latency={elapsed:.1f}s"
        if scoring["breakdown"]["expected_patterns"]["misses"]:
            status += f" MISSING={scoring['breakdown']['expected_patterns']['misses']}"
        print(status)

    return {
        "task_id": task["id"],
        "task_name": task.get("name", ""),
        "difficulty": task.get("difficulty", "easy"),
        "exit_code": result.returncode,
        "output": output,
        "stderr": result.stderr.strip(),
        "latency": elapsed,
        **scoring,
    }


def _category_to_task_type(category: str) -> str:
    mapping = {
        "coding": "coding",
        "tests": "tests",
        "summarize": "summarize",
        "docs": "docs",
        "refactor": "refactor",
        "smoke": "generic",
    }
    return mapping.get(category, "generic")


# ─────────────────────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────────────────────

def compute_summary(results: list) -> dict:
    """Compute per-category and overall scores from a list of task results."""
    by_category = {}
    for r in results:
        # Infer category from task_id prefix
        cat = r["task_id"].split("-")[0]
        by_category.setdefault(cat, []).append(r)

    category_summaries = {}
    all_weighted = []
    all_weights = []

    for cat, cat_results in by_category.items():
        valid = [r for r in cat_results if r.get("raw_score") is not None]
        if not valid:
            continue
        weighted_sum = sum(r["weighted_score"] for r in valid)
        weight_sum = sum(r["weight"] for r in valid)
        avg_weighted = weighted_sum / weight_sum if weight_sum else 0
        latencies = [r["latency"] for r in valid]
        category_summaries[cat] = {
            "score": round(avg_weighted),
            "tasks": len(cat_results),
            "pass": sum(1 for r in valid if r["raw_score"] >= 70),
            "fail": sum(1 for r in valid if r["raw_score"] < 70),
            "avg_latency": round(sum(latencies) / len(latencies), 1) if latencies else 0,
            "p95_latency": round(sorted(latencies)[int(len(latencies) * 0.95)], 1) if latencies else 0,
        }
        all_weighted.extend(r["weighted_score"] for r in valid)
        all_weights.extend(r["weight"] for r in valid)

    overall = round(sum(all_weighted) / sum(all_weights)) if all_weights else 0
    return {"overall": overall, "categories": category_summaries}


def routing_recommendation(summary: dict) -> dict:
    """Return routing recommendation per category based on score threshold."""
    rec = {}
    for cat, data in summary["categories"].items():
        if data["score"] >= 70:
            rec[cat] = "ROUTE_LOCAL"
        elif data["score"] >= 50:
            rec[cat] = "MARGINAL (Claude review recommended)"
        else:
            rec[cat] = "KEEP_ON_CLAUDE"
    return rec


def write_markdown_report(
    results: list,
    summary: dict,
    model: str,
    compare_results: Optional[list],
    compare_model: Optional[str],
    output_dir: str,
    config_path: str,
) -> str:
    lines = [
        "# Local LLM Benchmark Report",
        f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Model: `{model}`",
        f"Config: `{config_path}`",
        "",
        f"## Overall Score: {summary['overall']}/100",
        "",
    ]

    # Category table
    lines += ["## Category Scores", ""]
    header = "| Category | Score | Tasks | Pass | Fail | Avg Latency |"
    sep = "|---|---|---|---|---|---|"
    if compare_results and compare_model:
        header = "| Category | Score | Score (compare) | Tasks | Pass | Fail | Avg Latency |"
        sep = "|---|---|---|---|---|---|---|"
    lines += [header, sep]

    compare_summary = compute_summary(compare_results) if compare_results else None
    for cat in CATEGORY_ORDER:
        if cat not in summary["categories"]:
            continue
        d = summary["categories"][cat]
        if compare_summary and cat in compare_summary["categories"]:
            cd = compare_summary["categories"][cat]
            lines.append(
                f"| {cat} | {d['score']} | {cd['score']} | {d['tasks']} | {d['pass']} | {d['fail']} | {d['avg_latency']}s |"
            )
        else:
            lines.append(
                f"| {cat} | {d['score']} | {d['tasks']} | {d['pass']} | {d['fail']} | {d['avg_latency']}s |"
            )

    if compare_summary and compare_model:
        lines += ["", f"*Compare model: `{compare_model}`*"]

    # Routing recommendations
    rec = routing_recommendation(summary)
    lines += ["", "## Routing Recommendation", ""]
    for cat, r in rec.items():
        lines.append(f"- **{cat}**: {r}")

    # Failures
    failures = [r for r in results if r.get("raw_score") is not None and r["raw_score"] < 70]
    if failures:
        lines += ["", "## Failures", ""]
        for r in failures:
            lines.append(f"### {r['task_id']}: {r['task_name']} ({r.get('difficulty','?')})")
            lines.append(f"Score: {r['raw_score']}/100 | Latency: {r['latency']:.1f}s")
            bd = r.get("breakdown", {})
            if bd.get("expected_patterns", {}).get("misses"):
                lines.append(f"Missing patterns: {bd['expected_patterns']['misses']}")
            if bd.get("forbidden_patterns", {}).get("violations"):
                lines.append(f"Forbidden found: {bd['forbidden_patterns']['violations']}")
            if bd.get("syntax_check", {}).get("error"):
                lines.append(f"Syntax error: {bd['syntax_check']['error']}")
            lines.append(f"```\n{r['output'][:500]}{'...' if len(r['output']) > 500 else ''}\n```")
            lines.append("")

    # Performance summary
    valid = [r for r in results if r.get("latency") is not None]
    total_time = sum(r["latency"] for r in valid)
    avg_time = total_time / len(valid) if valid else 0
    lines += [
        "## Performance Summary",
        "",
        f"- Total tasks: {len(results)}",
        f"- Total time: {total_time:.1f}s",
        f"- Avg task time: {avg_time:.1f}s",
    ]

    report_path = os.path.join(output_dir, "bench-report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return report_path


def write_json_report(results: list, summary: dict, output_dir: str) -> str:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "routing_recommendation": routing_recommendation(summary),
        "results": results,
    }
    path = os.path.join(output_dir, "bench-report.json")
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Task loading
# ─────────────────────────────────────────────────────────────────────────────

def load_tasks(categories: Optional[list]) -> list:
    tasks = []
    task_files = sorted(Path(TASKS_DIR).glob("*.json"))
    if not task_files:
        print(f"ERROR: no task files found in {TASKS_DIR}", file=sys.stderr)
        sys.exit(1)

    for task_file in task_files:
        cat_name = task_file.stem  # e.g. "coding"
        if categories and cat_name not in categories:
            continue
        with open(task_file) as f:
            data = json.load(f)
        file_category = data.get("category", cat_name)
        for task in data.get("tasks", []):
            task["category"] = file_category  # ensure category is set on each task
            tasks.append(task)

    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Local LLM benchmark harness")
    parser.add_argument(
        "--categories",
        help="Comma-separated categories to run (default: all). E.g. coding,tests or smoke",
    )
    parser.add_argument(
        "--compare",
        metavar="MODEL",
        help="A second model name to compare against (runs all tasks twice)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(SCRIPT_DIR, "bench-results"),
        help="Output directory for report files (default: tools/local-llm/bench-results/)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print each task as it runs")
    parser.add_argument(
        "--config",
        default=os.path.join(SCRIPT_DIR, "config.json"),
        help="Path to config.json",
    )
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",")] if args.categories else None

    # Load config to get default model name
    try:
        with open(args.config) as f:
            cfg = json.load(f)
        model = cfg.get("model", "unknown")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR reading config: {e}", file=sys.stderr)
        sys.exit(2)

    tasks = load_tasks(categories)
    if not tasks:
        print("No tasks matched the specified categories.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    # ── Primary model run ──────────────────────────────────────────────────
    print(f"Running {len(tasks)} tasks on model: {model}")
    print(f"Output: {args.output}")
    print()

    results = []
    for task in tasks:
        r = run_task(task, verbose=args.verbose)
        results.append(r)

    summary = compute_summary(results)

    # ── Compare model run (optional) ───────────────────────────────────────
    compare_results = None
    if args.compare:
        print(f"\nRunning {len(tasks)} tasks on compare model: {args.compare}")
        compare_results = []
        for task in tasks:
            r = run_task(task, model=args.compare, verbose=args.verbose)
            compare_results.append(r)

    # ── Reports ────────────────────────────────────────────────────────────
    md_path = write_markdown_report(
        results, summary, model, compare_results, args.compare, args.output, args.config
    )
    json_path = write_json_report(results, summary, args.output)

    # ── Console summary ────────────────────────────────────────────────────
    print(f"\n{'-' * 50}")
    print(f"Overall score: {summary['overall']}/100")
    print()
    for cat in CATEGORY_ORDER:
        if cat not in summary["categories"]:
            continue
        d = summary["categories"][cat]
        rec = routing_recommendation(summary).get(cat, "?")
        print(f"  {cat:12s}  {d['score']:3d}/100  {d['pass']}/{d['tasks']} pass  {d['avg_latency']}s avg  -> {rec}")

    print(f"\nReports written to:")
    print(f"  {md_path}")
    print(f"  {json_path}")


if __name__ == "__main__":
    main()
