Contributing to Time Tracker Pro

Thanks for your interest in contributing! This guide explains how to set up your environment and submit clean, consistent changes.

Getting Started
- Install Python 3.8+.
- Create a virtual environment: `python -m venv time_tracker_env`
- Activate it and install dependencies: `pip install -r requirements.txt`

Run the App
- Local run: `streamlit run time_tracker.py`
- Launcher: `python launch.py`

Pre-commit Hooks (recommended)
- Install pre-commit: `pip install pre-commit`
- Install hooks: `pre-commit install`
- Run on all files: `pre-commit run --all-files`

Coding Standards
- Keep changes focused and minimal.
- Follow existing code style; prefer clear names and small functions.
- Avoid noisy prints; surface concise user messages via Streamlit when needed.

Git Workflow
- Create a feature branch from `main`.
- Use clear commit messages (imperative mood):
  - Good: "Add schedule planner conflict detection"
  - Good: "Fix CSV write race with atomic move"
- Open a PR with a summary of changes and testing notes.

Pull Request Checklist
- Compiles with `python -m compileall .`.
- Passes CI (import dependencies, CSV header sanity).
- No accidental data files or secrets committed.
- Screenshots/gifs for UI changes are helpful.

Issue Reporting
- For bugs, include steps to reproduce, expected vs. actual behavior, and environment details.

