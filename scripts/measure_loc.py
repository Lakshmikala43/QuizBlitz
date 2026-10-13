#!/usr/bin/env python3
"""
Quiz Royale — Reproducible Lines of Code (LOC) and Project Metrics Measurement Tool

Accurately measures and categorizes lines of code across:
1. Total production source LOC (Frontend + Backend)
2. Frontend source LOC (HTML, CSS, JS)
3. Backend source LOC (Python application code)
4. Test source LOC (Unit, integration, e2e tests)
5. Documentation LOC (Markdown and architecture docs)
6. Generated and vendored code LOC (separately reported)
7. Source files by language
8. Total Git commits and merged pull requests
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "ENV",
    "env",
    "__pycache__",
    "instance",
    ".pytest_cache",
    "htmlcov",
    ".egg-info",
    "build",
    "dist",
    ".idea",
    ".vscode",
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".mp3",
    ".wav",
    ".ogg",
    ".zip",
    ".tar",
    ".gz",
}

LANGUAGE_EXTS = {
    ".py": "Python",
    ".html": "HTML",
    ".css": "CSS",
    ".js": "JavaScript",
    ".md": "Markdown",
    ".toml": "TOML",
    ".ini": "INI",
    ".txt": "Text/Config",
    ".sh": "Shell",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
}


def is_comment(line: str, ext: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if ext in {".py", ".sh", ".toml", ".ini", ".yaml", ".yml"}:
        return s.startswith("#")
    if ext in {".js", ".css"}:
        return s.startswith("//") or s.startswith("/*") or s.endswith("*/") or s.startswith("*")
    if ext in {".html"}:
        return s.startswith("<!--") or s.endswith("-->")
    return False


def analyze_file(filepath: Path) -> Dict[str, int]:
    ext = filepath.suffix.lower()
    total = 0
    blank = 0
    comment = 0
    code = 0

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total += 1
                stripped = line.strip()
                if not stripped:
                    blank += 1
                elif is_comment(line, ext):
                    comment += 1
                else:
                    code += 1
    except Exception:
        pass

    return {"total": total, "blank": blank, "comment": comment, "code": code}


def categorize_path(rel_path: str) -> str:
    norm = rel_path.replace("\\", "/")
    if norm.startswith("app/templates/") or norm.startswith("app/static/"):
        return "frontend"
    if norm.startswith("app/") or norm in {"run.py", "wsgi.py", "config.py"}:
        return "backend"
    if norm.startswith("tests/"):
        return "test"
    if norm.startswith("docs/") or norm == "README.md":
        return "documentation"
    if norm.startswith("scripts/"):
        return "tooling"
    if norm.startswith("vendor/") or norm.startswith("generated/"):
        return "vendored_generated"
    return "configuration"


def get_git_metrics() -> Tuple[int, int]:
    commits = 0
    merged_prs = 0
    try:
        commit_res = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if commit_res.returncode == 0:
            commits = int(commit_res.stdout.strip())

        log_res = subprocess.run(
            ["git", "log", "--grep=Merge pull request", "--oneline"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if log_res.returncode == 0:
            lines = [l for l in log_res.stdout.strip().split("\n") if l.strip()]
            merged_prs = len(lines)
    except Exception:
        pass
    return commits, merged_prs


def run_measurement() -> Dict:
    metrics = {
        "categories": {
            "frontend": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "backend": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "test": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "documentation": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "tooling": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "configuration": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
            "vendored_generated": {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0},
        },
        "languages": {},
        "files_summary": [],
    }

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            p = Path(root) / file
            ext = p.suffix.lower()
            if ext in EXCLUDE_EXTS:
                continue

            rel_str = str(p.relative_to(PROJECT_ROOT))
            cat = categorize_path(rel_str)
            stats = analyze_file(p)

            lang = LANGUAGE_EXTS.get(ext, "Other")
            if lang not in metrics["languages"]:
                metrics["languages"][lang] = {"files": 0, "total": 0, "code": 0}
            metrics["languages"][lang]["files"] += 1
            metrics["languages"][lang]["total"] += stats["total"]
            metrics["languages"][lang]["code"] += stats["code"]

            cat_stats = metrics["categories"][cat]
            cat_stats["files"] += 1
            cat_stats["total"] += stats["total"]
            cat_stats["blank"] += stats["blank"]
            cat_stats["comment"] += stats["comment"]
            cat_stats["code"] += stats["code"]

            metrics["files_summary"].append({
                "path": rel_str,
                "category": cat,
                "language": lang,
                **stats,
            })

    commits, prs = get_git_metrics()
    metrics["git"] = {"commits": commits, "merged_prs": prs}

    fe_code = metrics["categories"]["frontend"]["code"]
    be_code = metrics["categories"]["backend"]["code"]
    metrics["summary"] = {
        "production_source_code_sloc": fe_code + be_code,
        "production_total_lines": (
            metrics["categories"]["frontend"]["total"] + metrics["categories"]["backend"]["total"]
        ),
        "frontend_sloc": fe_code,
        "backend_sloc": be_code,
        "test_sloc": metrics["categories"]["test"]["code"],
        "docs_sloc": metrics["categories"]["documentation"]["code"],
        "tooling_sloc": metrics["categories"]["tooling"]["code"],
        "vendored_sloc": metrics["categories"]["vendored_generated"]["code"],
        "grand_total_sloc": sum(c["code"] for c in metrics["categories"].values()),
        "grand_total_lines": sum(c["total"] for c in metrics["categories"].values()),
    }
    return metrics


def format_report_markdown(metrics: Dict) -> str:
    s = metrics["summary"]
    git = metrics["git"]
    lines = [
        "# Quiz Royale — Reproducible Lines of Code (LOC) Audit Report",
        "",
        f"> Generated dynamically by `scripts/measure_loc.py`.",
        "",
        "## 1. Executive Summary",
        "",
        "| Metric | Total Lines | Code Only (SLOC) | Files |",
        "|---|---|---|---|",
        f"| **Production Source (Frontend + Backend)** | {s['production_total_lines']:,} | **{s['production_source_code_sloc']:,}** | {metrics['categories']['frontend']['files'] + metrics['categories']['backend']['files']} |",
        f"| — Frontend (HTML / CSS / JS) | {metrics['categories']['frontend']['total']:,} | {s['frontend_sloc']:,} | {metrics['categories']['frontend']['files']} |",
        f"| — Backend (Python Flask / ORM) | {metrics['categories']['backend']['total']:,} | {s['backend_sloc']:,} | {metrics['categories']['backend']['files']} |",
        f"| **Test Suites** | {metrics['categories']['test']['total']:,} | {s['test_sloc']:,} | {metrics['categories']['test']['files']} |",
        f"| **Documentation & Specs** | {metrics['categories']['documentation']['total']:,} | {s['docs_sloc']:,} | {metrics['categories']['documentation']['files']} |",
        f"| **Tooling & Scripts** | {metrics['categories']['tooling']['total']:,} | {s['tooling_sloc']:,} | {metrics['categories']['tooling']['files']} |",
        f"| **Configuration** | {metrics['categories']['configuration']['total']:,} | {metrics['categories']['configuration']['code']:,} | {metrics['categories']['configuration']['files']} |",
        f"| **Vendored / Generated Code** | {metrics['categories']['vendored_generated']['total']:,} | {s['vendored_sloc']:,} | {metrics['categories']['vendored_generated']['files']} |",
        f"| **Grand Total (Entire Repository)** | **{s['grand_total_lines']:,}** | **{s['grand_total_sloc']:,}** | {sum(c['files'] for c in metrics['categories'].values())} |",
        "",
        "## 2. Git & Pull Request Activity",
        "",
        f"- **Total Git Commits**: {git['commits']}",
        f"- **Merged Pull Requests**: {git['merged_prs']}",
        "",
        "## 3. Breakdown by Language",
        "",
        "| Language | Files | Code Lines (SLOC) | Total Lines |",
        "|---|---|---|---|",
    ]
    for lang, lstats in sorted(metrics["languages"].items(), key=lambda x: x[1]["code"], reverse=True):
        lines.append(f"| {lang} | {lstats['files']} | {lstats['code']:,} | {lstats['total']:,} |")

    lines.extend([
        "",
        "## 4. Verification Standards Note",
        "Every file counted belongs strictly to the project source tree. Dependencies, virtual environments, binaries, cache databases, and build output directories are explicitly excluded.",
    ])
    return "\n".join(lines)


def main():
    metrics = run_measurement()
    if "--json" in sys.argv:
        print(json.dumps(metrics, indent=2))
        return

    md_report = format_report_markdown(metrics)
    print(md_report)

    if "--update-doc" in sys.argv or True:
        report_path = PROJECT_ROOT / "docs" / "LOC_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_report + "\n")
        print(f"\n[OK] Updated report in {report_path}")


if __name__ == "__main__":
    main()
