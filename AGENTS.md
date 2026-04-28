# Project Instructions

## Safety
- Do not read `.env`, `.env.*`, private keys, credentials, or files that appear to contain secrets.
- Ask before editing files.
- Ask before installing packages, running network commands, or starting long-running processes.
- Do not run destructive commands such as `rm -rf`, `git reset --hard`, or `git checkout --` unless explicitly requested.
- Do not commit, push, create branches, or open pull requests unless explicitly requested.

## Project Style
- Prefer simple, course-friendly Python code.
- Keep the architecture explainable for a GenAI engineering project.
- Favor readable names and straightforward modules over clever abstractions.
- Add variables typing and short 1-line docstring description for each function.
- Keep README instructions current as the project evolves.

## Environment
- Use `.env.example` to document required environment variables.
- Never write real API keys or credentials into tracked files.
- Keep generated data, local vector stores, and cache files out of git unless explicitly approved.
