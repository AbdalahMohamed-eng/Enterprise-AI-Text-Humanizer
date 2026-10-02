# AI Text Humanizer

A modern, web-based tool that rewrites AI-generated text to sound authentically human and bypass AI detection. It uses a **hybrid approach**:
1. **Rule-Based NLP Preprocessing**: Uses `spaCy` to disrupt statistical invariants (low perplexity, flat burstiness, overused passive voice, AI clichés).
2. **LLM Polishing**: Uses LiteLLM (supporting OpenAI, Gemini, Groq) to smoothly rewrite the preprocessed text, preserving meaning while ensuring human-like flow.

## Features
- **6-Stage NLP Pipeline**: Cliché stripper, contraction injector, passive-to-active voice, burstiness modulator, lexical entropy booster.
- **BYOK (Bring Your Own Key)**: API keys are saved locally in your browser (`localStorage`) and never sent to a database.
- **Real-Time Streaming**: Token-by-token UI updates via SSE.
- **AI Detection Preview**: Checks text against local AI detection models (ModernBERT) and the Sapling API.
- **Interactive UI**: Side-by-side comparison, word-level visual diffing, readability metrics.

## Tech Stack
- **Backend**: FastAPI, LiteLLM, spaCy, NLTK, textstat, HuggingFace Transformers
- **Frontend**: Alpine.js, Tailwind CSS, DaisyUI (No Node.js build step required)

## Installation

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1 on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the spaCy language model
python -m spacy download en_core_web_sm

# 4. Start the server
uvicorn app.main:app --reload
```

## Usage
Open [http://localhost:8000](http://localhost:8000) in your browser.
Click the Settings gear icon to add your API keys (OpenAI, Gemini, Groq, or Sapling).
Paste AI text, select your tone, and click "Humanize Text".
