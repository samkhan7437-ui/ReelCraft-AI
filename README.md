# 🎬 ReelCraft AI — Faceless Video Studio & Auto-Poster

**ReelCraft AI** is an end-to-end automated platform that generates and posts high-retention vertical Instagram Reels and YouTube Shorts (9:16) for **any niche**—completely runnable on your local machine.

---

## ✨ Features

- **Any Niche Supported**:
  - Built-in presets: *True Crime & Mysteries, Horror Encounters, Reddit Stories & Drama, Stoic Motivation, Mind-Blowing Facts, Conspiracies & Secret History, Wealth & Crypto*.
  - **Custom Topic / Prompt**: Type in any topic (e.g., *"The Dyatlov Pass Incident"*, *"Ancient Spartan Laws"*).
- **Single Reel vs. Multi-Part Series**:
  - **Single Reel (30–50s)**: High-speed retention, strong hook, payoff, and call-to-action.
  - **Multi-Part Series (Part 1, Part 2, etc.)**: Calculated cliffhangers with automated top banner overlays (`[ PART 1 OF 2 ]`).
- **100% Free High-Quality Voiceover**:
  - Powered by **Edge-TTS** (Microsoft neural voices: deep crime narrators, energetic science hosts, conversational Reddit storytellers).
  - No GPU or paid subscription required.
- **Dynamic CapCut-Style Animated Captions**:
  - High-contrast, bold typography with thick black outlines, centered at the sweet spot for mobile viewing.
  - Alternating yellow and white highlight animations.
- **Automated Video Compositing (FFmpeg)**:
  - Scales and crops to vertical 1080x1920 (9:16).
  - Loops background footage, mixes ducked ambient music, and renders crisp MP4s.
- **Hands-Free Autopilot Scheduler**:
  - Run the scheduler in the background to automatically create and queue reels on set intervals (e.g., every 12 hours).
- **Instagram Auto-Publisher**:
  - Uses the official **Meta Graph API** to publish reels directly to your Instagram Creator/Business account.
  - Simulates and queues posts locally when testing without API tokens.

---

## 🚀 Quick Start (1-Click Launch)

### Option A: Double-Click (Windows)
Double-click the file:
```
start_studio.bat
```
This automatically starts the server and opens your browser to:
👉 **`http://localhost:8000`**

### Option B: Terminal Command
```bash
python run.py
```
Then visit **`http://localhost:8000`** in your browser.

---

## 🎨 Adding Your Own Video Clips & Music

You can customize the visuals and sound at any time:
1. **Background Footage**:
   - Drop any `.mp4` video (gameplay like Minecraft parkour, GTA driving, satisfying kinetic sand, nature/drone shots) into the folder:
     ```
     assets/backgrounds/
     ```
   - The studio will automatically detect and allow you to select it from the dropdown.
2. **Background Music**:
   - Drop any background music `.mp3` into:
     ```
     assets/music/
     ```
   - ReelCraft will automatically duck the music volume (-18dB) so the voiceover stays crystal clear.

---

## ⚙️ Configuration & API Setup (`.env`)

ReelCraft AI works **100% out of the box** without any API keys using its built-in viral story library. 

If you want to connect external services, edit the `.env` file in this directory:

### 1. Instagram Graph API (For Live Posting)
To post directly to your Instagram account:
```env
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
INSTAGRAM_ACCESS_TOKEN=your_meta_system_user_or_page_token
```
*(Requires an Instagram Business or Creator account linked to a Facebook Page).*

### 2. LLM Providers for Unlimited Dynamic Scriptwriting
Choose your provider in `.env`:
```env
# Options: "builtin", "ollama", "gemini", or "openai"
LLM_PROVIDER=builtin

# If using local Ollama (Llama 3 / Mistral)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Or Cloud APIs (optional)
GEMINI_API_KEY=
OPENAI_API_KEY=
```

---

## 📁 Project Architecture

```
dailyposts/
├── app/
│   ├── main.py              # FastAPI Web & API Server
│   ├── config.py            # Niche definitions, voices, paths
│   ├── script_engine.py     # Story & scriptwriter (Single & Multi-Part)
│   ├── audio_engine.py      # Edge-TTS voice synthesis & ASS caption timing
│   ├── video_engine.py      # FFmpeg 9:16 vertical video composer
│   ├── instagram_engine.py  # Meta Graph API publisher & history
│   └── scheduler.py         # Autonomous background posting scheduler
├── assets/
│   ├── backgrounds/         # 9:16 video clips (Minecraft, GTA, atmospheric)
│   ├── music/               # Royalty-free background music tracks
│   └── fonts/               # Bold fonts for captions
├── output/
│   ├── audio/               # Synthesized audio & subtitle files (.mp3, .ass)
│   ├── videos/              # Rendered 1080x1920 MP4 reels
│   └── posts_history.json   # Queue & publishing history
├── static/
│   ├── index.html           # Dark glassmorphic studio interface
│   ├── style.css            # Modern studio styling
│   └── app.js               # Interactive frontend controller
├── run.py                   # Python server entrypoint
├── start_studio.bat         # 1-click Windows launcher
└── requirements.txt         # Dependencies
```

---

## 🔒 Ban Prevention & Best Practices
- The **Meta Graph API** is the official, approved way to publish to Instagram Reels. It never triggers account checkpoint blocks or shadowbans.
- Recommended posting pace: **1 to 3 reels per day** for organic algorithm growth.
