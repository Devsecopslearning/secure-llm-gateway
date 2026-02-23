# Secure LLM Gateway - M Tech Project

## Project Overview

A **Secure AI Interaction Framework** that provides safe access to local LLaMA3 language models with enterprise-grade security controls including authentication, role-based authorization, and Data Loss Prevention (DLP).

---

## Key Features

### 1. **Authentication & Authorization**
- ✅ Session-based user authentication
- ✅ Role-based access control (RBAC) with admin/auditor roles
- ✅ Secure password validation
- ✅ Session management with secret key

**Credentials:**
```
Username: admin    | Password: admin123    | Role: admin
Username: auditor  | Password: auditor456   | Role: auditor
```

### 2. **Data Loss Prevention (DLP)**
- ✅ Enterprise-grade PII detection using Microsoft Presidio
- ✅ Detects sensitive data:
  - Personal information (names, email addresses, phone numbers)
  - Financial data (credit card numbers, bank accounts)
  - Government IDs (passports, SSN, driver licenses)
  - Network information (IP addresses, URLs)
  - Healthcare information (medical licenses)

- ✅ Blocks prompts containing PII automatically
- ✅ Provides detailed detection reports

### 3. **Query Logging & Audit Trail**
- ✅ All queries logged to `query.log`
- ✅ User identification in logs
- ✅ Audit trail for compliance

### 4. **LLM Integration**
- ✅ Direct API communication with local Ollama instance
- ✅ LLaMA3 model support
- ✅ Error handling and timeout management (120s timeout)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (UI)                        │
│                   (index.html - Login/Query)                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────────────────────┐
│                    Flask Web Server                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Authentication│ │ DLP Module  │ │ Query Handler│     │
│  │  (session)   │  │ (Presidio)  │  │   (Logging)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼──────┐          ┌─────────▼────────┐
│  Ollama API │          │  Query Logger    │
│  (client.py)│          │  (security.py)   │
└──────┬──────┘          └──────────────────┘
       │
┌──────▼──────────────────────────────┐
│    LLaMA3 Language Model            │
│   (Local - http://localhost:11434)  │
└─────────────────────────────────────┘
```

---

## Project Structure

```
secure_llm_project/
├── app/
│   ├── __init__.py
│   ├── client.py           # Ollama API communication
│   ├── server.py           # Flask application & routes
│   ├── security.py         # Logging & credential validation
│   ├── dlp.py              # Data Loss Prevention (Presidio)
│   └── templates/
│       └── index.html      # Web UI (Login & Query)
├── .venv/                  # Virtual environment
├── query.log               # Audit log file
└── requirements.txt        # Project dependencies
```

---

## Module Description

### **client.py** - LLM Communication
Handles HTTP communication with Ollama's REST API
```python
query_llama3(prompt, user=USER_NAME)
  → Sends prompt to Ollama API
  → Returns model response or error
  → 120-second timeout for responses
```

### **server.py** - Flask Web Server
Main application server with security endpoints
```python
GET  /                 → Serve login UI
POST /login            → Authenticate user (create session)
POST /logout           → Destroy session
POST /secure-query     → Query LLM with DLP & auth checks
```

### **security.py** - Audit & Validation
```python
check_api_key(key)     → Validate API key
check_role(role)       → Validate user role
log_query(user, prompt)→ Write to audit log
```

### **dlp.py** - Data Loss Prevention
Enterprise-grade PII detection using Microsoft Presidio
```python
check_pii(text)           → Detect PII entities in text
block_if_pii(text)        → Check if text should be blocked
anonymize_pii(text)       → Redact sensitive information
```

### **index.html** - Frontend UI
JavaScript-based login and query interface
- Login form with username/password
- Secure query submission (session-based)
- Response display and error handling

---

## Security Implementation

### 1. **Authentication Layer**
- Session-based authentication
- Secure password validation
- Session timeout (browser managed)

### 2. **Authorization Layer**
- Role-based access control (RBAC)
- Endpoint protection on `/secure-query`
- Role validation (admin/auditor)

### 3. **DLP Layer**
- PII detection before LLM query
- Blocks sensitive data transmission
- Detailed detection reporting

### 4. **Audit Layer**
- Query logging with user identification
- Timestamp recording
- Compliance audit trail

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Ollama installed and running
- LLaMA3 model downloaded

### Installation Steps

1. **Clone/Setup Project**
```bash
cd c:\secure_llm_project
python -m venv .venv
.venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install flask requests presidio-analyzer presidio-anonymizer
```

3. **Start Ollama Server** (in separate terminal)
```bash
ollama serve
```

4. **Run Flask Application**
```bash
python -m flask --app app.server run
```

5. **Access Web UI**
Open browser: `http://localhost:5000`

---

## Usage Examples

### Example 1: Successful Query
```
Login: admin / admin123
Query: "What is machine learning?"
Result: ✅ Processed successfully
Response: [LLaMA3 model response]
```

### Example 2: DLP Block - Email Address
```
Query: "My email is john@example.com"
Result: ❌ Blocked
Error: "Query blocked by DLP policy. Detected sensitive data: EMAIL_ADDRESS"
```

### Example 3: DLP Block - Phone Number
```
Query: "Call me at 555-123-4567"
Result: ❌ Blocked
Error: "Query blocked by DLP policy. Detected sensitive data: PHONE_NUMBER"
```

### Example 4: Unauthorized Role
```
Login: auditor / auditor456
Query: [Any query]
Result: ✅ Allowed (auditor role authorized)
```

---

## PII Detection Capabilities

Presidio detects and blocks:
- **PERSON** - Person names
- **EMAIL_ADDRESS** - Email addresses
- **PHONE_NUMBER** - Phone numbers
- **CREDIT_CARD** - Credit card numbers
- **PASSPORT** - Passport numbers
- **DRIVER_LICENSE** - Driver license numbers
- **IP_ADDRESS** - IP addresses
- **US_SSN** - Social Security Numbers
- **LOCATION** - Physical locations
- **ORGANIZATION** - Company names
- **MEDICAL_LICENSE** - Medical licenses

---

## Testing

### Test DLP Blocking
```bash
# Test 1: Email Detection
Input: "Contact me at user@domain.com"
Expected: BLOCKED

# Test 2: Phone Detection
Input: "My number is (123) 456-7890"
Expected: BLOCKED

# Test 3: SSN Detection
Input: "My SSN is 123-45-6789"
Expected: BLOCKED

# Test 4: Normal Query
Input: "How do I learn Python?"
Expected: PROCESSED
```

---

## Security Considerations

✅ **Implemented:**
- Session-based authentication
- Role-based authorization
- DLP with PII detection
- Query audit logging
- HTTPS-ready architecture
- Error handling & logging

**Future Enhancements:**
- HTTPS/TLS encryption
- API key-based authentication
- Rate limiting
- Database audit logs
- Multi-factor authentication (MFA)
- Encryption at rest for logs

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Flask |
| **Frontend** | HTML, JavaScript, CSS |
| **LLM Integration** | Ollama API |
| **DLP/PII Detection** | Microsoft Presidio |
| **Authentication** | Flask Sessions |
| **Logging** | Python logging module |

---

## References

- **Microsoft Presidio**: https://microsoft.github.io/presidio/
- **Ollama**: https://ollama.ai/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **OWASP Security Guidelines**: https://owasp.org/

---

## Conclusion

This project demonstrates a **production-grade security architecture** for AI applications, combining:
1. **Authentication** - User identity verification
2. **Authorization** - Role-based access control
3. **Data Protection** - PII detection and prevention
4. **Audit Trail** - Query logging and compliance

Suitable for enterprise deployments and regulatory compliance scenarios.

---

**Project Status**: Ready for M Tech Presentation
**Last Updated**: February 2026
