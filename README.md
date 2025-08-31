# HeyQ - Universal Voice-Controlled Web Automation System 🚀

HeyQ is a **universal voice automation system** that can automate **ANY website** using natural voice commands. Powered by AI intelligence (MCP) + visible Playwright automation, you can control any website just by speaking!

## 🌟 New Features (Latest)
- **🌐 Universal Website Support** - Works with ANY domain (.com, .in, .org, .edu, etc.)
- **🎤 Smart Voice Parsing** - Natural language understanding for complex commands
- **👁️ Visible Browser Automation** - See real browser automation happening
- **🤖 AI-Powered Intelligence** - MCP (Model Context Protocol) for smart strategies
- **⚡ Auto-Close & Test Status** - Browser auto-closes with clear PASS/FAIL feedback
- **🔍 Enhanced Search Parsing** - Handles travel, shopping, and general search queries
- **🎯 Real-Time Results** - Instant feedback with detailed verification

## 🚀 What You Can Do

**Simple Navigation:**
- "open makemytrip.com" → Opens site → Auto-closes → Shows TEST PASSED
- "visit amazon.in" → Opens Amazon India → Verifies load → Auto-closes

**Search Automation:**
- "open youtube search tseries" → Opens YouTube → Searches → Auto-closes
- "go to flipkart search iPhone 16" → Opens Flipkart → Searches → Shows results

**Travel & Booking:**
- "open makemytrip search ticket for Delhi to Bangalore flight"
- "visit bookmyshow find movies in Mumbai"

**Universal Domain Support:**
- Works with ANY website: github.com, stackoverflow.com, netflix.com, etc.
- No hardcoded limitations - if it's a website, HeyQ can automate it!e-Controlled Enterprise Test Automation Framework

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

## 🚀 Quick Start Guide

### 1️⃣ Prerequisites
- **Python 3.10+** (Python 3.13 works fine)
- **macOS/Linux/Windows** supported
- **Node.js** (for Playwright browsers)

### 2️⃣ Installation
```bash
# Clone the repository
git clone https://github.com/Ronaldozero7/HeyQ.git
cd HeyQ

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
```

### 3️⃣ Start the Hybrid Voice Server
```bash
# Start the universal voice automation server
python hybrid_voice_automation.py
```

You'll see:
```
🚀 Starting HYBRID AI+MCP+Playwright Voice Interface...
📍 URL: http://127.0.0.1:8082
🎤 Voice Command: 'search for Python tutorials on YouTube'
👁️ You will see REAL browser automation happening!
🤖 Best of both worlds: MCP AI + Visible Playwright
```

### 4️⃣ Test Your First Voice Command
```bash
# In another terminal, test a simple navigation
curl -X POST "http://127.0.0.1:8082/api/run" \
  -H "Content-Type: application/json" \
  -d '{
    "utterance": "open youtube.com",
    "headed": true,
    "use_ai": true
  }'
```

**You'll see:**
- ✅ Browser opens visibly
- ✅ Navigates to YouTube
- ✅ Verifies page load
- ✅ Auto-closes after 5 seconds
- ✅ Returns "TEST PASSED" status

### 5️⃣ Try Advanced Voice Commands
```bash
# Search automation
curl -X POST "http://127.0.0.1:8082/api/run" \
  -H "Content-Type: application/json" \
  -d '{
    "utterance": "open youtube search AI tutorials",
    "headed": true,
    "use_ai": true
  }'

# Travel booking
curl -X POST "http://127.0.0.1:8082/api/run" \
  -H "Content-Type: application/json" \
  -d '{
    "utterance": "open makemytrip search Delhi to Mumbai flight",
    "headed": true,
    "use_ai": true
  }'
```
## 🎯 Supported Voice Commands

### Navigation Commands
```bash
"open google.com"           # Opens Google
"visit amazon.in"           # Opens Amazon India  
"go to github.com"          # Opens GitHub
"navigate to netflix.com"   # Opens Netflix
```

### Search Commands
```bash
"open youtube search AI tutorials"           # YouTube search
"visit amazon search iPhone 16"             # Amazon product search
"go to google search Python programming"    # Google search
"open stackoverflow search async python"    # Stack Overflow search
```

### Travel & Booking
```bash
"open makemytrip search Delhi to Mumbai flight"
"visit bookmyshow find movies in Bangalore"
"go to airbnb search hotels in Goa"
```

### Universal Support
- **Any Domain:** .com, .in, .org, .edu, .gov, .io, .co.uk, etc.
- **Any Website:** github.com, stackoverflow.com, linkedin.com, etc.
- **Complex Queries:** Travel bookings, product searches, general searches

## 🛠️ API Reference

### POST /api/run
Execute voice automation commands:

```json
{
  "utterance": "open youtube search AI tutorials",
  "headed": true,     // Show visible browser
  "use_ai": true      // Use AI intelligence
}
```

**Response:**
```json
{
  "ok": true,
  "automation_status": "PASSED",
  "target_url": "https://youtube.com",
  "flow_type": "complex",
  "success_message": "✅ TEST PASSED! Successfully searched for 'AI tutorials'",
  "verification": {
    "test_status": "PASS",
    "auto_closed": true,
    "message": "✅ Search Test PASSED"
  }
}
```

## 🏗️ Architecture

### Hybrid AI+MCP+Playwright System
```
Voice Command → URL Extraction → AI Strategy → Playwright Automation → Auto-Close → Results
```

**Components:**
- **Universal URL Extraction:** Multi-pattern regex for ANY domain
- **AI Strategy Analysis:** MCP intelligence for smart automation
- **Visible Browser Control:** Python Playwright with real browser
- **Auto-Close Logic:** Smart timing based on task complexity
- **Test Verification:** Clear PASS/FAIL status with details

## 🧪 Testing & Validation

### Run Test Scripts
```bash
# Test universal URL extraction
python test_universal_automation.py

# Test real website automation
python test_real_any_website.py

# Run all tests
pytest heyq/tests/
```

### Legacy Features (Still Available)
```bash
# Original voice control with wake word
heyq --mode voice --browser chromium --headed

# Web app interface
heyq-web  # Open http://127.0.0.1:8000

# Data-driven tests
pytest --html=heyq/reports/report.html --self-contained-html
```

## 📁 Project Structure
```
HeyQ/
├── hybrid_voice_automation.py    # 🆕 Main hybrid automation server
├── real_voice_mcp.py            # MCP integration layer
├── test_universal_automation.py  # Universal automation tests
├── requirements.txt             # Python dependencies
├── heyq/                       # Core framework
│   ├── automation/             # Playwright automation engine
│   ├── voice/                  # Voice processing & STT
│   ├── nlp/                    # Natural language processing
│   ├── pages/                  # Page Object Models
│   ├── security/               # Secrets & security
│   └── webapp/                 # Web interface
├── mcp_integration/            # Model Context Protocol
├── playwright-mcp/             # Playwright MCP server
└── config/                     # Configuration files
    └── secrets.yaml           # Local secrets (create from template)
```

## 🔧 Configuration

### Environment Setup
```bash
# Create secrets file from template
cp config/secrets.yaml.template config/secrets.yaml

# Edit with your credentials (optional, for legacy features)
nano config/secrets.yaml
```

### Browser Options
- **Visible Browser:** `headed: true` (default for demo)
- **Headless Browser:** `headed: false` (for production)
- **Browser Types:** Chromium, Firefox, WebKit

## 🚀 Production Deployment

### Docker Support (Coming Soon)
```bash
# Build container
docker build -t heyq-automation .

# Run container
docker run -p 8082:8082 heyq-automation
```

### CI/CD Integration
- **Jenkins:** Use included `Jenkinsfile`
- **GitHub Actions:** Create workflow for automation tests
- **GitLab CI:** Use `.gitlab-ci.yml` template

## 🛡️ Security & Privacy

- **Local Execution:** All automation runs locally on your machine
- **No Data Sharing:** Voice commands processed locally
- **Secure Secrets:** Local secrets file with audit logging
- **Visible Automation:** See exactly what the system is doing

## 🐛 Troubleshooting

### Common Issues

**1. Server won't start:**
```bash
# Check if port is in use
lsof -i :8082

# Kill existing processes
pkill -f "python.*hybrid_voice_automation.py"
```

**2. Browser automation fails:**
```bash
# Reinstall Playwright browsers
python -m playwright install --force
```

**3. Voice parsing issues:**
- Check server logs for URL extraction details
- Verify command format: "open website.com" or "visit domain.com"

**4. Module not found errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test
4. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest heyq/tests/

# Format code
black hybrid_voice_automation.py

# Check code quality
flake8 heyq/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🌟 Star History

If HeyQ helped you automate websites with voice commands, please ⭐ star this repo!

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Ronaldozero7/HeyQ/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Ronaldozero7/HeyQ/discussions)
- **Email:** bhanuprakashj7@gmail.com

---

**🎉 Happy Voice Automation! Say it, and HeyQ will automate it! 🚀**

