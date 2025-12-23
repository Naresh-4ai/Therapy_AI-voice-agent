# 🧠 Therapy AI Assistant

A **voice-enabled AI therapy support assistant** designed to provide calm, empathetic, and emotionally intelligent conversations with **persistent memory**.  
It supports **continuous voice conversations**, remembers past interactions, and works through both a **web UI** and **command-line interface**.

> ⚠️ This project is a **supportive AI tool**, not a replacement for professional therapy or medical care.

---

## ✨ Key Capabilities

### 🎤 Voice Interaction
- **Continuous Voice Mode** – natural back-and-forth conversation
- **Single Voice Input** – one interaction at a time
- **8 Voice Options** – alloy, echo, fable, onyx, nova, shimmer, coral, sage
- **Real-time transcription** – see what you say as it’s processed
- **Automatic audio playback** – AI responses play instantly

### 🧠 Memory & Context
- **Persistent memory** across sessions using Mem0
- **Context-aware responses** from past conversations
- **Vector search** with Qdrant (semantic memory)
- **Knowledge graph** with Neo4j (relationship memory)
- **Memory management** – view or clear stored memories

### 💬 Interfaces
- **Streamlit Web UI** (`app.py`) – recommended
- **Command-Line Interface** (`main.py`) – terminal-based continuous conversation

### 🤖 AI Behavior
- Therapy-focused, empathetic responses
- Non-judgmental and emotionally validating
- Avoids diagnosis and medical advice
- Encourages professional help when appropriate

---

## ⚠️ Important Disclaimer

- This is a **support tool only**
- It does **not** diagnose, treat, or replace therapy
- Not intended for crisis situations  
- For emergencies, contact professional services immediately

---

## 🏗️ High-Level Architecture

```
┌─────────────────┐
│   User Input    │
│ (Voice/Text)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Speech-to-Text │
│   (Google STT)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Memory Search  │
│   (Mem0/Qdrant) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │
│  (GPT-4)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Memory Storage │
│ (Qdrant + Neo4j)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text-to-Speech │
│   (OpenAI TTS)  │
└─────────────────┘


```

---

## 📋 Prerequisites

### Required
- **Python 3.11 or 3.12**
- **OpenAI API key**
- **Docker** (for databases)

### System Dependencies
- **Windows**: PyAudio wheels available
- **Linux / macOS**: PortAudio required

---

## 📁 Project Structure

```

voice_agents/
├── .devcontainer/
│   └── docker-compose.yml    # Qdrant + Neo4j
├── app.py                    # Streamlit UI
├── main.py                   # CLI interface
├── graph.py                  # LangGraph agent logic
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (CREATE THIS)
└── README.md

````

---

## 🚀 Quick Start (Recommended Flow)

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd voice_agents
````

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### Linux / macOS only (if PyAudio fails)

```bash
# Ubuntu / Debian
sudo apt-get install portaudio19-dev python3-dev gcc

# macOS
brew install portaudio
```

Then re-run:

```bash
pip install -r requirements.txt
```

---

## 🔑 REQUIRED: Create `.env` File

You **must** create a `.env` file in the project root.

### Create file

```bash
touch .env
```

### Add this inside `.env`

```env
OPENAI_API_KEY=your_openai_api_key_here
```



```bash
echo ".env" >> 
```

---

## 🗄️ Start Database Services

```bash
cd .devcontainer
docker-compose up -d
cd ..
```

This starts:

* **Qdrant** → `localhost:6333`
* **Neo4j (Bolt)** → `localhost:7687`
* **Neo4j Browser** → `http://localhost:7474`

---

## ▶️ Run the Application

### Web UI (Recommended)

```bash
streamlit run app.py
```

### Command Line

```bash
python main.py
```

---

## 🎮 Using the App

### Streamlit UI

* Select a voice from the sidebar
* Use text or voice input
* Enable **continuous mode** for natural conversation
* View or clear stored memories anytime

### Voice Options

* **coral** (default): warm & engaging
* **sage**: calm & measured
* **onyx**: deep & authoritative
* **nova / shimmer**: friendly, soft female tones

---

## 🔧 Configuration

### Memory & Model Config

Edit the `config` dictionary in `app.py` or `main.py`:

```python
config = {
    "embedder": {
        "provider": "openai",
        "model": "text-embedding-3-small"
    },
    "llm": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    },
    "vector_store": {
        "provider": "qdrant",
        "host": "localhost",
        "port": 6333
    },
    "graph_store": {
        "provider": "neo4j",
        "url": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "your_password"
    }
}
```

---

## 🛠️ Troubleshooting

### PyAudio Errors

```bash
sudo apt-get install portaudio19-dev python3-dev gcc
pip install pyaudio
```

### Databases Not Connecting

```bash
docker ps
```

If not running:

```bash
cd .devcontainer
docker-compose down
docker-compose up -d
```

### Streamlit Port Issue

```bash
streamlit run app.py --server.port 8502
```

---

## 🔐 Security Best Practices

* Never commit API keys
* Rotate keys regularly
* Use strong Neo4j passwords
* Add authentication before production
* Monitor OpenAI usage

---

## 📄 License

Provided for **educational and experimental purposes only**.



---

🧘 **Final Reminder**

This AI is designed to **support, listen, and validate** —
not to replace professional mental health care.

Made with care for mental wellness ❤️

```

---

### If you want next:
- 🔹 **Ultra-short README** (for GitHub landing)
- 🔹 **Docker-only version**
- 🔹 **Production hardening checklist**
- 🔹 **Investor / portfolio README**

Just tell me what version you want.
```
