# Quiz Royale — Git & Pull Request Workflow

## Git Branching Strategy
Quiz Royale follows a Git Flow-inspired feature branch workflow tailored for strict verification:
- `main`: Production-ready branch. Only clean, tested, and reviewed code is merged here.
- `feature/<name>`: Feature branches for discrete units of functional capability.
- `bugfix/<name>`: Bugfix branches for targeted defect remediation.
- `docs/<name>`: Documentation, architecture specs, and reports.
- `test/<name>`: Test suites and QA automation.
- `ci/<name>`: CI/CD workflows and deployment configurations.

## Merging Policy
- Every change is developed on its dedicated branch.
- No direct commits to `main` without a branch.
- Merges are executed using `--no-ff` (non-fast-forward) to preserve clear commit provenance, branch history, and pull request boundaries.
- Every merge commit is titled: `Merge pull request #<number> from <branch>: <Description>`.
- Every pull request is logged in [`docs/PR_TRACKER.md`](PR_TRACKER.md) with scope, verification results, and merge commit hashes.

## Synchronizing with Remote GitHub
When a remote repository is configured by the developer:
```bash
# Add remote origin
git remote add origin https://github.com/<your-username>/quiz-royale.git

# Push main and all feature branches
git push -u origin main
git push origin --all
```
