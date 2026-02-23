# Secure LLM Gateway - Installation & Quick Start

## Prerequisites
- Python 3.8+ (tested on 3.14.2)
- Ollama installed and running
- Git

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/secure_llm_project.git
cd secure_llm_project
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Ollama Server (separate terminal)
```bash
ollama serve
```

Make sure you have the llama3 model:
```bash
ollama pull llama3
```

### 5. Run Flask Application
```bash
# Windows
python -m flask --app app.server run

# Linux/Mac
python3 -m flask --app app.server run
```

### 6. Access Web Interface
Open browser: `http://localhost:5000`

## Login Credentials

```
Admin Account:
  Username: admin
  Password: admin123

Auditor Account:
  Username: auditor
  Password: auditor456
```

## Project Structure
```
secure_llm_project/
├── app/
│   ├── client.py           # Ollama API client
│   ├── server.py           # Flask application
│   ├── security.py         # Authentication & logging
│   ├── dlp.py              # Data Loss Prevention
│   └── templates/
│       └── index.html      # Web UI
├── query.log               # Audit log
├── requirements.txt        # Dependencies
├── README.md              # Full documentation
└── INSTALL.md             # This file
```

## Troubleshooting

**Flask not starting?**
- Ensure Ollama is running: `ollama serve`
- Use correct Python path: `.venv\Scripts\python.exe -m flask --app app.server run`

**DLP blocking legitimate queries?**
- Remove email addresses, phone numbers, SSN, etc.
- PII patterns: email@domain.com, (123) 456-7890, 123-45-6789

**Port 5000 already in use?**
- Change port: `flask run --port 5001`

## Features
✅ User authentication & sessions
✅ Role-based access control (RBAC)
✅ Data Loss Prevention (PII detection)
✅ Query audit logging
✅ LLaMA3 LLM integration
✅ Error handling & validation

## Support
For issues or questions, open an issue on GitHub.
