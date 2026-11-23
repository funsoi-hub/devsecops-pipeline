# Vulnerable example (do not deploy)

A tiny Flask app with planted flaws, one for each scanner in the gate. The
[self-test workflow](../../.github/workflows/self-test.yml) runs the gate against
it in report-only mode and **fails if the gate finds nothing**, which proves the
scanners are actually working rather than silently passing.

| Planted flaw | Should be caught by |
|---|---|
| SQL injection (string-built query) | Semgrep, Bandit |
| Command injection (`shell=True`) | Semgrep, Bandit |
| Unsafe `yaml.load` | Bandit |
| Flask `debug=True` | Bandit |
| Hard-coded API key in git | Gitleaks |
| Old Flask / PyYAML / Jinja2 / requests | Trivy (dependencies) |
| EOL `python:3.7` base image | Trivy (image) |
| Container runs as root | Trivy (Dockerfile) |
