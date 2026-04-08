# ATLAS System v2.0 - Async Neural Command Interface

A powerful, cloud-native AI automation system with distributed LLM ensemble processing, non-blocking async architecture, and GitHub-integrated memory persistence.

## 🚀 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ATLAS GENERAL (ASYNC)                    │
│              (CONSTRUCTOR.py - Orchestrator)                 │
└────────────────┬──────────────────────────────────────────┘
                 │
         ┌───────┼───────┬──────────┬─────────────┐
         ▼       ▼       ▼          ▼             ▼
    ┌────────┐┌──────┐┌────────┐┌──────────┐┌──────────┐
    │ BRAIN  ││VISION││ HANDS  ││   COMM   ││ CONFIG   │
    │ENGINE  ││SYSTEM││CONTROL ││   LINK   ││  & LOG   │
    │        ││      ││        ││          ││          │
    │LLM     ││CV &  ││Judge0  ││FastAPI + ││Environment│
    │Router  ││Capture││CLI    ││GitHub    ││Variables │
    │(15 x   ││       ││Compiler││API      ││          │
    │Models) ││       ││        ││          ││          │
    └────────┘└──────┘└────────┘└──────────┘└──────────┘
         │       │       │          │             │
         └───────┴───────┴──────────┴─────────────┘
         All tasks run CONCURRENTLY (non-blocking)
         Result aggregation via asyncio.gather()
```

## 📋 System Components

### 1. **BRAIN_ENGINE.PY** (LLM Router)
- Calls **15 LLM models** in parallel via:
  - **Groq API** (3 models: Llama-3-70B, Llama-3-8B, Llama-2-70B)
  - **HuggingFace** (5 models: various coding models)
  - **GitHub Models** (7 models: GPT-4o, Llama-3-70B, Phi-4)
- **CodeQualityVoter**: Evaluates and selects the best C code
- **Async execution**: All 15 requests happen in parallel
- **Output**: Production-ready C code selected via voting logic

### 2. **VISION_SYSTEM.PY** 
- Screen capture and image processing
- Template matching for UI automation
- Pixel-level color analysis
- Logs screenshots for review

### 3. **HAND_CONTROL.PY** (Judge0 Compiler)
- **Replaced PyAutoGUI** with subprocess CLI execution
- **Judge0 Cloud Compiler**: Remote C code compilation
- **Build Workflow**: 
  1. Syntax validation
  2. Compilation via Judge0
  3. Execution and output capture
  4. Binary/executable generation
  5. Download link generation
- **Async execution**: Non-blocking compilation

### 4. **COMM_LINK.PY** (FastAPI Server)
- **Replaced PyWhatKit** with FastAPI (more robust)
- **REST API Endpoints**:
  - `POST /chat` - Chat messages
  - `POST /command` - System commands
  - `GET /memory` - View memory
  - `WebSocket /ws` - Real-time communication
- **GitHub Persistence**: Auto-commits `memory.json` after each operation
- **Features**: 
  - Web-based chat interface
  - Webhook support
  - Real-time WebSocket communication

### 5. **CONSTRUCTOR.py** (Async General)
- **Orchestrates all subsystems** using asyncio
- **Non-blocking cycle execution**:
  - Vision reconnaissance
  - Neural analysis via LLM ensemble
  - Hand execution with code compilation
  - Remote communication
- **Parallel execution**: All tasks run concurrently
- **Configurable**: Duration, max cycles, interval

## 🔧 Installation & Setup

### Prerequisites
- Python 3.12+
- Git & GitHub account
- API keys for: Groq, HuggingFace, GitHub Models, Judge0

### Step 1: Clone & Install
```bash
git clone https://github.com/atlas215/AI-.git
cd AI-
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp env.example .env
# Edit .env with your API keys:
nano .env
```

### Step 3: Initialize Git (if needed)
```bash
git config user.email "atlas@example.com"
git config user.name "ATLAS System"
git remote add origin https://github.com/YOUR_REPO/AI-.git
```

### Step 4: Run the System
```bash
# Option 1: Run async mission (5 cycles, 1 hour max)
python CONSTRUCTOR.py

# Option 2: Start FastAPI server (separate terminal)
python -m COMM_LINK

# Option 3: Test individual modules
python BRAIN_ENGINE.py
python HAND_CONTROL.py
```

## 🔑 Environment Variables (.env)

```env
# API Keys
GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_hf_key
GITHUB_API_KEY=your_github_key
JUDGE0_API_KEY=your_judge0_key

# GitHub Repository
GITHUB_REPO_OWNER=atlas215
GITHUB_REPO_NAME=AI-
GITHUB_REPO_BRANCH=main

# FastAPI Server
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_DEBUG=False

# System
LOG_LEVEL=INFO
ENABLE_AUTH=True
SECRET_KEY=change-me-in-production
```

## 📡 API Usage Examples

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "sir_boss",
    "message": "Generate safe C string copy function"
  }'
```

### Command Endpoint
```bash
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "system_check",
    "parameters": {}
  }'
```

### WebSocket (Real-time Chat)
```javascript
const ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen = () => {
  ws.send(JSON.stringify({
    user: "sir_boss",
    message: "System status check"
  }));
};
ws.onmessage = (event) => console.log(event.data);
```

## 🧠 How the Brain Engine Works

1. **LLM Ensemble Request**:
   ```python
   result = await brain.get_ensemble_response(
     "Generate a safe string copy function in C"
   )
   ```

2. **Parallel Calls** (all 15 simultaneously):
   - Groq: Llama-3-70B, Llama-3-8B, Llama-2-70B
   - HuggingFace: 5 inference endpoints
   - GitHub Models: 7 models

3. **Quality Voting**:
   - Score each response (0-1 scale)
   - Metrics: memory safety, error handling, code quality
   - Select best by voting mechanism

4. **Output**:
   ```json
   {
     "selected_code": "...",
     "best_provider": "groq:llama-3-70b-versatile",
     "quality_score": 0.87,
     "timestamp": "2026-04-08T07:30:00"
   }
   ```

## 🔄 Execution Flow (Async Cycle)

```
CYCLE START
  │
  ├─► VISION (async) ──────┐
  │                         │
  ├─► BRAIN (async) ────────┤───► HANDS ──► COMM ──► GitHub Commit
  │                         │
  └─ (wait for both) ───────┘

All tasks are non-blocking!
Memory is auto-saved every cycle.
```

## 📊 Performance Optimizations

- **Asyncio**: Non-blocking I/O for all operations
- **Parallel LLM Calls**: 15 models called simultaneously (not sequentially)
- **Judge0 Cloud**: Offload compilation to remote servers
- **Streaming**: Large responses streamed instead of loaded entirely
- **Caching**: Memory.json caches decisions for quick replay

## 🛡️ Security Features

- **Environment variables**: Never hardcode API keys
- **GitHub token**: Requires authentication for commits
- **Auth middleware**: FastAPI with optional auth
- **Memory encryption**: (Future: Add encryption layer)

## 📝 File Structure

```
.
├── BRAIN_ENGINE.PY          # LLM router (15 parallel models)
├── VISION_SYSTEM.PY         # Screen capture & analysis
├── HAND_CONTROL.PY          # Judge0 compiler + subprocess
├── COMM_LINK.PY             # FastAPI server
├── CONSTRUCTOR.py           # Async general orchestrator
├── config.py                # Centralized configuration
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables template
├── memory.json              # Auto-saved decision log
├── brain_decisions.json     # Brain engine decisions
├── logs/                    # Log files
│   └── vision/              # Screenshot logs
└── README.md               # This file
```

## 🚦 Status Codes & Messages

| Code | Meaning |
|------|---------|
| `success` | Operation completed normally |
| `pending` | Operation in progress |
| `failed_syntax` | C code syntax errors |
| `failed_compilation` | Judge0 compilation error |
| `failed_executable` | Binary generation failed |
| `error` | Unexpected error |

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'config'"
```bash
# Ensure config.py is in the same directory
# Or add to PYTHONPATH:
export PYTHONPATH="${PYTHONPATH}:/path/to/AI-"
```

### "Judge0 timeout"
- Increase `JUDGE0_TIMEOUT` in config.py
- Check Judge0 API rate limits

### "GitHub commit failed"
- Verify GITHUB_TOKEN is set
- Ensure git.Repo() is initialized
- Check repository permissions

### "LLM models returning empty"
- Verify API keys are correct
- Check rate limits for each provider
- Review API response logs

## 🔐 Production Checklist

- [ ] Change `SECRET_KEY` in .env
- [ ] Enable `ENABLE_AUTH` in config
- [ ] Set `LOG_LEVEL = WARNING` for production
- [ ] Rotate API keys regularly
- [ ] Set up GitHub Actions for CI/CD
- [ ] Add database for persistent memory (replace JSON)
- [ ] Implement model validation/fine-tuning
- [ ] Add monitoring & alerting
- [ ] Set resource limits for containers
- [ ] Enable HTTPS for FastAPI

## 📚 Documentation

### Module Docstrings
Each module includes comprehensive docstrings. Check the code for detailed function signatures.

### Examples
See `if __name__ == "__main__"` sections in each module for usage examples.

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following PEP-8
3. Test: `pytest`
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request

## 📄 License

MIT License - See LICENSE file

## 👨‍💼 Author

**SIR, BURTON** (atlas215)  
ATLAS System v2.0  
April 2026

---

**Last Updated**: April 8, 2026  
**Version**: 2.0 (Async Neural Router Edition)
