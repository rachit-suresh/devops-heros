# Session 16: CI/CD with GitHub Actions

Student: 24BCS10139

Based on the instructor's `Nency-Ravaliya/devops-heros` Session 16 final calculator pipeline. Calculator source and baseline tests are from that teaching material. The root workflow makes it runnable from this course fork.

Pipeline: Test Application -> Security Check -> Build Application -> Deploy and Smoke Test.

- Tests: pytest verifies add, subtract, multiply, divide, and division-by-zero handling.
- Security: a classroom-only sensitive-file-pattern check, not a full security audit.
- Build: package calculator.py and build-info.txt and pass the small built package to the deploy job without persistent artifact storage.
- Deploy: receive the actual build artifact into a fresh runner and execute it in an isolated Python container, with smoke-test assertions.

The deployment is an ephemeral classroom demo, not a public or production deployment. It needs no cloud credentials or paid infrastructure.

Workflow: `.github/workflows/session16-cicd.yml`.

Environment: prepared remotely with assistant help; execution evidence must come from the real Codespaces terminal and GitHub Actions run, not example output.
