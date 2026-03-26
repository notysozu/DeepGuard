# Contributing to DeepGuard

Thanks for helping improve DeepGuard. This project aims to stay approachable for contributors while keeping the repository dependable for production-style experimentation.

## Development Setup

1. Fork and clone the repository.
2. Create a local environment:

```bash
./scripts/bootstrap.sh
cp -n .env.example .env
```

3. Create a localhost model registry for local runs:

```bash
cat > configs/models.local.yaml <<'EOF'
models:
  - name: model_a
    url: http://127.0.0.1:8001/predict
  - name: model_b
    url: http://127.0.0.1:8002/predict
EOF
```

4. Run the backend tests:

```bash
source .venv/bin/activate
python -m pytest
```

5. Build the web UI:

```bash
npm --prefix web_ui ci
npm --prefix web_ui run build
```

## Coding Standards

- Prefer small, focused pull requests.
- Preserve existing architecture boundaries between gateway, model services, shared code, and UI.
- Keep comments minimal and helpful.
- Avoid introducing secrets, tokens, or private dataset paths into tracked files.
- Add or update tests whenever behavior changes.

## Commit Conventions

Use Conventional Commits:

- `feat:` for new functionality
- `fix:` for bug fixes
- `docs:` for documentation-only changes
- `test:` for test additions or updates
- `refactor:` for behavior-preserving code improvements
- `chore:` for tooling, CI, or repository maintenance

Examples:

- `docs: add maintainer and security documentation`
- `test: add pytest configuration`
- `chore: add github actions workflow`

## Pull Request Process

1. Sync with the latest default branch before starting work.
2. Make sure relevant tests pass locally.
3. Describe the problem, the approach, and any tradeoffs in the PR description.
4. Include screenshots or terminal output when UI or operational behavior changes.
5. Request review only after the branch is ready to merge.
