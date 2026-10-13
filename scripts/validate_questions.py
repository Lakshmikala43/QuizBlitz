#!/usr/bin/env python3
"""
Quiz Royale — Question Bank Quality Assurance and Validation Tool

Performs strict automated validation on every question in the seed dataset:
1. Valid category slug linkage
2. Difficulty matches 'easy', 'medium', or 'hard'
3. Exactly four distinct answer options
4. Exactly one answer option marked correct
5. Non-empty educational explanation
6. Duplicate question detection
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_data.programming import PROGRAMMING_CATEGORIES, PROGRAMMING_QUESTIONS
from scripts.seed_data.computer_science import CS_CATEGORIES, CS_QUESTIONS
from scripts.seed_data.general import GENERAL_CATEGORIES, GENERAL_QUESTIONS


def validate_dataset() -> Tuple[bool, List[str], Dict[str, int]]:
    all_categories = PROGRAMMING_CATEGORIES + CS_CATEGORIES + GENERAL_CATEGORIES
    all_questions = PROGRAMMING_QUESTIONS + CS_QUESTIONS + GENERAL_QUESTIONS

    valid_slugs = {c["slug"] for c in all_categories}
    errors = []
    seen_questions = set()
    stats = {
        "total_categories": len(all_categories),
        "total_questions": len(all_questions),
        "easy": 0,
        "medium": 0,
        "hard": 0,
    }

    # Validate categories
    for cat in all_categories:
        if not cat.get("name") or not cat.get("slug"):
            errors.append(f"Category missing name or slug: {cat}")

    # Validate questions
    for idx, q in enumerate(all_questions, 1):
        q_text = q.get("question_text", "").strip()
        slug = q.get("category_slug", "")
        diff = q.get("difficulty", "")
        options = q.get("options", [])
        explanation = q.get("explanation", "").strip()

        # 1. Text length
        if len(q_text) < 10:
            errors.append(f"Question #{idx}: Text too short ({len(q_text)} chars).")

        # 2. Duplicate check
        norm_text = q_text.lower()
        if norm_text in seen_questions:
            errors.append(f"Question #{idx}: Duplicate question text detected: '{q_text[:40]}...'")
        seen_questions.add(norm_text)

        # 3. Category existence
        if slug not in valid_slugs:
            errors.append(f"Question #{idx}: Invalid category slug '{slug}'.")

        # 4. Difficulty validation
        if diff not in {"easy", "medium", "hard"}:
            errors.append(f"Question #{idx}: Invalid difficulty '{diff}'.")
        else:
            stats[diff] += 1

        # 5. Exactly 4 options
        if len(options) != 4:
            errors.append(f"Question #{idx}: Expected 4 options, found {len(options)}.")

        # 6. Exactly 1 correct option
        correct_count = sum(1 for opt in options if opt.get("is_correct") is True)
        if correct_count != 1:
            errors.append(f"Question #{idx}: Expected exactly 1 correct option, found {correct_count}.")

        # 7. Check option uniqueness
        opt_texts = [opt.get("text", "").strip().lower() for opt in options]
        if len(set(opt_texts)) != len(opt_texts):
            errors.append(f"Question #{idx}: Duplicate option texts detected.")

        # 8. Explanation check
        if len(explanation) < 10:
            errors.append(f"Question #{idx}: Explanation missing or too short.")

    is_valid = len(errors) == 0
    return is_valid, errors, stats


def main():
    print("=" * 60)
    print("Quiz Royale — Running Question Bank Quality Assurance Check...")
    print("=" * 60)

    is_valid, errors, stats = validate_dataset()

    print(f"Categories Audited : {stats['total_categories']}")
    print(f"Questions Audited  : {stats['total_questions']}")
    print(f"  - Easy           : {stats['easy']}")
    print(f"  - Medium         : {stats['medium']}")
    print(f"  - Hard           : {stats['hard']}")
    print("-" * 60)

    if is_valid:
        print("[SUCCESS] All questions passed strict validation! 100% compliant.")
        sys.exit(0)
    else:
        print(f"[FAILED] Found {len(errors)} validation error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
