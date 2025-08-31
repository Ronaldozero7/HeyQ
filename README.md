# HeyQ - Voice-Controlled Enterprise Test Automation Framework

HeyQ lets you run browser automation via voice (“Hey Q”) or YAML/JSON data-driven tests, with NLP to parse commands, Playwright for automation, and local secrets file.

## Features
- Wake-word voice control ("Hey Q") using SpeechRecognition + Whisper/Google STT
- NLP intents/entities via lightweight regex rules
- Playwright automation with Page Object Model (POM)
- Multi-browser: chromium, firefox, webkit (Safari engine), Edge (if installed)
- Data-driven tests (YAML/JSON)
- Secure secrets via local `config/secrets.yaml`, audit logging, redaction
- Pytest-based orchestration with parallel runs and HTML reports
- CI ready: Jenkinsfile and GitLab CI

## Quick Start

### 1) Prereqs
- Python 3.10+
- macOS: `brew install ffmpeg` (optional: `brew install portaudio` if you plan to use live microphone input)
  - Note: On Python 3.13, the SpeechRecognition package depends on aifc which was removed. Voice mode may be unavailable; use the plan runner instead or run on Python 3.12.
- Node browsers for Playwright: will be installed later

### 2) Create venv and install requirements
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install
```

### 3) Add local secrets
Edit `config/secrets.yaml` (already created) and set:
```yaml
flipkart_username: testuser@example.com
flipkart_password: P@ssw0rd!
card_number: 4111111111111111
card_name: Test User
card_exp: 12/30
card_cvv: 123
```

### 4) Run a sample test (data-driven checkout)
```bash
# Fast local run (unit-level):
pytest --html=heyq/reports/report.html --self-contained-html

# Live Flipkart e2e is skipped by default. To enable it explicitly:
HEYQ_RUN_E2E=1 pytest -k e2e --html=heyq/reports/report.html --self-contained-html
```

### 5) Voice control mode
- With a working microphone and Whisper installed (or use Google STT):
```bash
# Voice may be unavailable on Python 3.13 due to aifc removal in stdlib
heyq --mode voice --browser chromium --headed
```

### 6) Web App (voice in browser)
Run a local web UI that listens for "Hey Q" and triggers the Flipkart flow:

```bash
heyq-web
# Open http://127.0.0.1:8000 in a Chromium-based browser for best Web Speech API support.
```
Set your Flipkart username/password in `config/secrets.yaml` before running. The app will log progress and launch a Playwright browser (headless by default, toggle in UI).
Say "Hey Q" to wake, then commands like:
- "Open flipkart"
- "Search for iPhone 16 Pro"
- "Add to cart"
- "Checkout"
- "Login with saved credentials"
- "Place order"

### 6) CLI
```bash
heyq --help
```

## Repo Structure
```
heyq/
  voice/      # wake word, STT, voice loop
  nlp/        # intents/entities, context manager
  automation/ # Playwright engine and action runner
  pages/      # POM for Flipkart
  security/   # secrets loader, audit
  tests/      # pytest tests
  data/       # test data yaml/json
  reports/    # reports output
```

## Parallel and CI
- Parallel: `pytest -n auto`
- Jenkins: use `Jenkinsfile`
- GitLab: use `.gitlab-ci.yml`

## Notes
- This project connects to live Flipkart; site changes can affect selectors. The code includes timeouts and retries.
- Secrets are read from `config/secrets.yaml` and redacted in logs.

