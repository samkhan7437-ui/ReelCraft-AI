# 🎬 ReelCraft AI — Faceless Video Studio & Auto-Poster

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-00589e.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Edge-TTS](https://img.shields.io/badge/TTS-Edge--TTS-brightgreen.svg)](https://github.com/rany2/edge-tts)

**ReelCraft AI** is an all-in-one automated pipeline for creating, rendering, and auto-publishing viral, faceless short-form videos (**Instagram Reels, TikToks, and YouTube Shorts**). 

From generating niche-targeted scripts to rendering vertical 9:16 videos with dynamic animated captions, AI images, background music, and auto-publishing to Instagram on a schedule — ReelCraft AI handles the entire creation lifecycle.

---

## ✨ Key Features

- 🧠 **AI Script Engine**:
  - Built-in viral templates (works offline without any API keys).
  - Integrations for **Ollama (local LLMs like Llama 3)**, **Google Gemini**, and **OpenAI GPT-4**.
  - Multi-part series generation with cliffhangers (Part 1 / Part 2 / Part 3).

- 🎙️ **Hyper-Realistic Neural Voiceovers**:
  - Powered by Microsoft Edge Neural TTS (100% free, no credit card or subscription needed).
  - Multi-language support: English (US/GB), Hindi (हिंदी), Spanish (Español), French, German, Portuguese, Italian, and Japanese.
  - Granular control over speaking speed and vocal tone.

- 🎨 **Visual & Scene Synthesis**:
  - Multi-scene image generation with **DALL-E 3**, **Gemini**, or **Pollinations AI**.
  - Automatic vertical B-roll clip downloading via **Pexels API**.
  - Dynamic panning, zoom (Ken Burns effect), and visual themes tailored to each niche.

- 💬 **Dynamic Kinetic Subtitles**:
  - Word-level timestamp synchronization (.ass subtitles).
  - High-visibility viral typography, colored word highlights, and outline effects.

- 🎵 **Audio Mixing & Ducking**:
  - Ambient and tension background soundtracks.
  - Automatic audio ducking to lower music volume when voiceover speaks.

- 📱 **Instagram Graph API Auto-Poster & Scheduler**:
  - Native integration with Instagram Business/Creator accounts.
  - Built-in cron / interval autopilot scheduler (`APScheduler`) for automated daily posting.
  - Auto-generated captions and optimized niche hashtags.

- 🖥️ **Interactive Studio Dashboard**:
  - Modern, dark-mode glassmorphism web interface.
  - Real-time video/audio preview player, voice tester, and rendering queue.

---

## 🎯 Supported Niches

| Niche Preset | Aesthetic / Tone | Default Voice |
| :--- | :--- | :--- |
| **True Crime & Mysteries** | Suspenseful, dark, measured pace | `Christopher (US)` |
| **Horror & Paranormal** | Eerie, shocking climax, whispering hooks | `Christopher (US)` |
| **Reddit Confessions & Drama** | First-person conversational, fast-paced | `Guy (US)` |
| **Stoic Wisdom & Motivation** | Deep, authoritative, commanding | `Brian (US)` |
| **Wild Facts & Science** | High-energy, curiosity-driven | `Jenny (US)` |
| **Conspiracy & Secret History** | Investigative, dramatic, classified | `Ryan (GB)` |
| **Wealth, Finance & Crypto** | Sharp, analytical, insider knowledge | `Eric (US)` |

---

## 🏗️ Project Architecture

```plaintext
ReelCraft-AI/
├── api/
│   └── index.py            # Serverless / Vercel entrypoint
├── app/
│   ├── audio_engine.py     # Voiceover generation & subtitle sync (Edge-TTS)
│   ├── config.py           # Presets, voices, niches, and environment config
│   ├── image_engine.py     # Multi-scene AI image generation (DALL-E, Gemini, Pollinations)
│   ├── instagram_engine.py # Instagram Graph API uploader & publisher
│   ├── main.py             # FastAPI backend endpoints & routing
│   ├── scheduler.py        # Background job scheduler for autopilot posting
│   ├── script_engine.py    # Viral hooks, multi-part logic, & LLM integrations
│   └── video_engine.py     # FFmpeg video rendering & audio ducking pipeline
├── assets/
│   ├── backgrounds/        # Loopable ambient vertical background videos
│   └── music/              # Curated background audio tracks
├── static/
│   ├── index.html          # Web Studio dashboard UI
│   ├── app.js              # Client-side reactivity & API handler
│   └── style.css           # Modern dark-glass theme
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── run.py                  # Local server startup script
├── start_studio.bat        # 1-click Windows launcher
└── vercel.json             # Deployment configuration for Vercel
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed
- **FFmpeg** installed and accessible in your system `PATH` (or install via `imageio-ffmpeg` package included in `requirements.txt`)
- Git installed

### 2. Clone Repository
```bash
git clone https://github.com/samkhan7437-ui/ReelCraft-AI.git
cd ReelCraft-AI
```

### 3. Setup Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a local `.env` file from the provided example:
```bash
cp .env.example .env
```

Open `.env` and configure your settings:
```ini
# LLM Provider for Script Generation: "builtin", "ollama", "gemini", or "openai"
LLM_PROVIDER=builtin

# Cloud LLM API Keys (optional if using builtin or local ollama)
GEMINI_API_KEY=
OPENAI_API_KEY=

# Image Provider: "openai", "gemini", or "pollinations"
IMAGE_PROVIDER=pollinations

# Optional: Meta / Instagram Graph API Configuration (for Auto-Posting)
INSTAGRAM_ACCOUNT_ID=
INSTAGRAM_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

# Optional: Pexels API Key (for auto-downloading matching B-roll footage)
PEXELS_API_KEY=

# Server Port
PORT=8000
HOST=127.0.0.1
```

> [!TIP]
> **Zero-Cost Out of the Box**: You can run ReelCraft AI completely free! Keep `LLM_PROVIDER=builtin` and `IMAGE_PROVIDER=pollinations`. Edge-TTS provides free vocal synthesis.

---

## 🖥️ Running the Studio

### Windows 1-Click:
Double-click `start_studio.bat` or run:
```powershell
.\start_studio.bat
```

### Command Line:
```bash
python run.py
```

Once started, open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🛠️ REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the ReelCraft Web Studio UI |
| `GET` | `/health` | Health check endpoint |
| `POST` | `/api/script/generate` | Generates a viral reel script based on niche & topic |
| `POST` | `/api/audio/generate` | Generates neural voiceover audio & synchronized subtitles |
| `POST` | `/api/video/render` | Assembles video, subtitles, music, & scene images |
| `POST` | `/api/instagram/publish` | Publishes a rendered video to an Instagram account |
| `GET` | `/api/autopilot/status` | Retrieves current status of scheduled autopilot runs |
| `POST` | `/api/autopilot/configure` | Configures automated posting schedule intervals |

---

## 🔒 Security & Git Hygiene

Make sure you do **not** push sensitive files:
- **Never commit `.env`**: Always keep credentials local. Use `.env.example` to share configuration structures.
- **Generated Media**: Rendered MP4/MP3/PNG files in `output/` are automatically excluded via `.gitignore` to keep repository size lean.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
