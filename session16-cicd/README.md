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

## Verification update (Oct 7)

Re-verified against the official Session 16 spec (final-cicd-pipeline README in `session-16-github-actions/`):

- **Build artifact:** the Build job now also uploads the packaged build with `actions/upload-artifact` (artifact name `calculator-build`), so the pipeline demonstrates a stored artifact in addition to job-to-job handoff. Confirmed present on the green run (902 bytes).
- **Failure gate demonstrated:** a deliberately broken push failed at the Test stage, and the Build + Deploy jobs were correctly skipped: https://github.com/rachit-suresh/devops-heros/actions/runs/37577639562
- **Green run after fix:** the follow-up push restored all four stages to green: https://github.com/rachit-suresh/devops-heros/actions/runs/37577740951
