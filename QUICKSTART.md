# ATLAS System v2.0 - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Environment Setup (1 min)
```bash
# Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR on Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration (2 min)
```bash
# Copy environment template
cp env.example .env

# Edit with your API keys
nano .env  # or use your editor

# Required keys:
# GROQ_API_KEY, HUGGINGFACE_API_KEY, GITHUB_API_KEY, JUDGE0_API_KEY
```

### Step 3: Git Setup (1 min)
```bash
# Configure git (for GitHub commits)
git config user.email "atlas@example.com"
git config user.name "ATLAS"

# Optional: Add remote
git remote add origin https://github.com/your_username/AI-.git
```

### Step 4: Run the System (1 min)

**Option A: Full Async Mission**
```bash
python CONSTRUCTOR.py
# Runs 5 cycles with Vision → Brain → Hands → Comm
```

**Option B: Start Web Server**
```bash
# Terminal 1: Start FastAPI
python -m COMM_LINK

# Terminal 2: Test API
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

**Option C: Test LLM Brain**
```bash
python BRAIN_ENGINE.py
# Tests ensemble of 15 LLM models
```

**Option D: Test Code Compilation**
```bash
python HAND_CONTROL.py
# Tests Judge0 cloud compiler
```

## 🧪 API Endpoints (if running FastAPI server)

### Interactive API Docs
```
http://localhost:8000/docs
```

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "sir_boss",
    "message": "Generate C string copy function"
  }'
```

### System Status
```bash
curl http://localhost:8000/health
```

### View Memory
```bash
curl http://localhost:8000/memory | jq .
```

## 📊 Expected Output

### When Running CONSTRUCTOR.py
```
============================================================
SYSTEM BOOT: 2026-04-08 07:30:00
VERSION: ATLAS-V2.0-REFACTORED
============================================================
Initializing Brain Engine (LLM Router)...
Initializing Vision System...
Initializing Hand Control (Judge0)...
Initializing Communication Link (FastAPI)...

[SUCCESS]: ALL SYSTEMS ONLINE. ATLAS IS READY, SIR.

--- CYCLE #1 START: 07:30:15 ---
VISUAL: Starting reconnaissance...
NEURAL: Calling 15 LLM models in parallel...
HANDS: Starting execution workflow...
COMM: Sending status update...

--- CYCLE #1 COMPLETE ---
Results: {
  "cycle": 1,
  "brain": {"status": "success", "confidence": 0.87},
  "hands": {"status": "success", "workflow_status": "complete"},
  ...
}
```

## 🔍 Monitoring & Logs

### View System Logs
```bash
# Real-time logs
tail -f logs/atlas.log

# All logs
ls logs/
```

### View Memory Snapshots
```bash
# System memory
cat memory.json | jq .

# Brain decisions
cat brain_decisions.json | jq .

# Vision logs
ls logs/vision/
```

## ⚙️ Common Configurations

### Faster Cycles
Edit `config.py`:
```python
CYCLE_INTERVAL = 30  # 30 seconds instead of 60
```

### More Cycles
Run with parameter:
```python
# In CONSTRUCTOR.py
await general.start_mission(duration_hours=0.5, max_cycles=10)
```

### Log Verbosity
Edit `config.py`:
```python
LOG_LEVEL = "DEBUG"  # More detailed logs
```

## 🐛 Quick Troubleshooting

### "API key not found"
```bash
# Check .env file exists
cat .env

# Verify GROQ_API_KEY is set
echo $GROQ_API_KEY  # Should print your key
```

### "Module not found"
```bash
# Ensure you're in project directory
cd /path/to/AI-

# Verify Python path
python -c "import sys; print(sys.path)"

# Install package in dev mode
pip install -e .
```

### "Connection refused" (FastAPI)
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Change port in .env
FASTAPI_PORT=8001
```

### "Judge0 timeout"
```bash
# Increase timeout in config.py
JUDGE0_TIMEOUT = 30

# Or use faster language
# C compilation is faster than C++
```

## 📈 Performance Tips

| Task | Time | Improvement |
|------|------|-------------|
| Single cycle | 5-10 sec | ✅ Non-blocking I/O |
| LLM response | ~3 sec | ✅ Parallel 15 models |
| Code compilation | ~2 sec | ✅ Cloud-based (Judge0) |
| GitHub commit | ~1 sec | ✅ Async git operations |

## 🔐 Security Notes

⚠️ **Never commit .env file to git!**
```bash
# Verify .gitignore contains .env
grep ".env" .gitignore
```

⚠️ **Rotate API keys regularly**
```bash
# Generate new GitHub token
# Update GITHUB_TOKEN in .env
```

⚠️ **Use strong SECRET_KEY in production**
```bash
# Generate random key
openssl rand -hex 32
# Add to .env as SECRET_KEY
```

## 📞 Support

### Getting Help
1. Check README.md
2. Read MIGRATION.md
3. Review module docstrings
4. Check GitHub issues

### Common Questions

**Q: Can I run multiple instances?**
A: Yes! Each instance needs its own port:
```bash
# Terminal 1
FASTAPI_PORT=8000 python -m COMM_LINK

# Terminal 2
FASTAPI_PORT=8001 python -m COMM_LINK
```

**Q: How do I train the brain?**
A: v2.0 uses external LLMs (Groq, HuggingFace). No local training needed.

**Q: Can I compile other languages?**
A: Yes! Judge0 supports 80+ languages. See config.py:
```python
JUDGE0_LANGUAGE_IDS = {
    "c": 50,
    "cpp": 54,
    "python": 71,
    ...
}
```

**Q: How do I export decisions?**
A: Memory is in memory.json:
```bash
# Export to CSV
python -c "
import json, csv
with open('memory.json') as f:
    data = json.load(f)
with open('export.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'decision'])
    for d in data['decisions']:
        writer.writerow(d)
"
```

## 🎯 Next Steps

1. ✅ Complete quick start above
2. 📖 Read full [README.md](README.md)
3. 🔧 Review [config.py](config.py) for customization
4. 🧪 Run individual module tests
5. 🚀 Deploy to production
6. 📊 Monitor memory.json for insights

---

**Happy Automating! 🤖**
