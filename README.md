# Armenian Bank Voice AI Support Agent

A voice AI assistant for Armenian banks built with LiveKit (open-source). The agent understands and speaks Armenian, and answers questions strictly about credits, deposits, and branch locations based on scraped bank website data.

## Architecture

```
User (microphone)
      ↓
LiveKit Server (self-hosted)
      ↓
Agent (agent.py)
 ├── STT: OpenAI Whisper — transcribes Armenian speech to text
 ├── LLM: GPT-4o — generates response based on RAG context
 └── TTS: ElevenLabs Multilingual v2 — converts response to Armenian speech
      ↓
ChromaDB (vector store)
      ↑
LlamaIndex RAG pipeline
      ↑
Scraped bank data (Ameriabank, ACBA, InecoBank)
```

### How it works

1. `scrape.py` crawls the official websites of 3 Armenian banks and saves the content to `data.json`
2. `ingest.py` converts the scraped text into vector embeddings using a Armenian-specific embedding model and stores them in ChromaDB
3. At agent startup, `query_engine.py` queries ChromaDB for relevant context about credits, deposits, and branches
4. The context is injected into the system prompt, so GPT-4o answers strictly based on the bank data
5. The user speaks Armenian — Whisper transcribes it, GPT-4o responds, ElevenLabs speaks the answer back

### Model choices

**STT — OpenAI Whisper**
Whisper has strong multilingual support including Armenian. Other STT providers like Deepgram do not support Armenian at all, making Whisper the clear choice for this task.

**LLM — GPT-4o**
GPT-4o handles Armenian well and follows system prompt instructions reliably. The RAG context is injected into the system prompt, and GPT-4o stays within the provided data without hallucinating outside knowledge.

**TTS — ElevenLabs Multilingual v2**
ElevenLabs Multilingual v2 supports Armenian and produces natural-sounding speech. OpenAI TTS has limited Armenian quality in comparison.

**Embeddings — Metric-AI/armenian-text-embeddings-2-large**
This is an Armenian-specific embedding model trained by Metric-AI. Using a language-specific model improves retrieval accuracy compared to generic multilingual embeddings, since the bank data is entirely in Armenian.

**Vector Store — ChromaDB**
Lightweight, local, no infrastructure needed. Persists to disk and loads fast at agent startup.

### Scalability

Adding a new bank requires only editing `config.json`:

```json
{
  "name": "NewBank",
  "pages": [
    {"url": "https://newbank.am/loans", "topic": "credits"},
    {"url": "https://newbank.am/deposits", "topic": "deposits"},
    {"url": "https://newbank.am/branches", "topic": "branches"}
  ]
}
```

Then re-run `scrape.py` and `ingest.py`. No code changes needed.

### Known limitations

Branch location data for some banks (Ameriabank, InecoBank) is rendered via Google Maps JavaScript and cannot be extracted by the scraper. A future fix would involve intercepting the bank's internal API endpoints (visible in browser DevTools Network tab) that serve branch data as JSON, and calling those directly instead of scraping the rendered page.

---

## Setup

### Requirements

- Python 3.10+
- API keys: OpenAI, ElevenLabs
- LiveKit server binary (see below)

### 1. Clone the repo

```bash
git clone https://github.com/MilenAyvazyan/armenian-bank-voice-ai
cd armenian-bank-voice-ai
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=your_openai_key
ELEVEN_API_KEY=your_elevenlabs_key
```

### 5. Scrape bank data

```bash
python scrape.py
```

This will create `data.json` with content from Ameriabank, ACBA, and InecoBank.

### 6. Ingest into ChromaDB

```bash
python ingest.py
```

This creates the `chroma_db/` vector store. This step takes a few minutes on CPU.

### 7. Start LiveKit server

Download the binary from https://github.com/livekit/livekit/releases/latest (`livekit-server_windows_amd64.zip`) and run:

```bash
.\livekit-server.exe --dev
```

### 8. Start the agent

In a new terminal:

```bash
python agent.py dev
```

### 9. Test via browser

Open https://agents-playground.livekit.io and connect with:
- URL: `ws://localhost:7880`
- API Key: `devkey`
- API Secret: `secret`

Click **Connect**, then speak in Armenian.

---

## Project structure

```
armenian-bank-voice-ai/
├── agent.py          # LiveKit agent — STT, LLM, TTS pipeline
├── scrape.py         # Scrapes bank websites
├── ingest.py         # Builds ChromaDB vector store
├── query_engine.py   # RAG query interface
├── config.json       # Bank URLs config
├── .env.example      # Environment variable template
├── requirements.txt  # Python dependencies
└── README.md
```
=======

