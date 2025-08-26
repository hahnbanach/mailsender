# AGENTS Guidelines

This repository contains scripts and services for generating and sending campaign emails.

## Contributor Instructions
- Use Python 3 for all scripts and modules.
- Keep the OpenAI Python SDK up to date:
  ```bash
  pip install --upgrade openai
  ```
- Before committing, ensure all Python files compile:
  ```bash
  python -m py_compile $(git ls-files '*.py')
  ```
- When working on email generation or sending features, log the prompt,
  generated content, and SendGrid request at DEBUG level for troubleshooting.
- Write concise, imperative commit messages.

