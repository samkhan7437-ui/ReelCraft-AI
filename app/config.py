import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ASSETS_DIR = BASE_DIR / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

OUTPUT_DIR = BASE_DIR / "output"
AUDIO_OUTPUT_DIR = OUTPUT_DIR / "audio"
VIDEO_OUTPUT_DIR = OUTPUT_DIR / "videos"

# Ensure directories exist
for path in [BACKGROUNDS_DIR, MUSIC_DIR, FONTS_DIR, AUDIO_OUTPUT_DIR, VIDEO_OUTPUT_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Settings from Environment
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "builtin").lower()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "127.0.0.1")

# Curated Niche Presets with Personas & Visual Aesthetics
NICHES = {
    "true_crime": {
        "name": "True Crime & Unsolved Mysteries",
        "description": "Chilling true stories, bizarre disappearances, and shocking twists.",
        "default_voice": "en-US-ChristopherNeural",
        "tone": "Suspenseful, serious, mysterious, measured pace",
        "visual_theme": "abyss_blue",
        "music_mood": "eerie",
        "hashtags": ["#truecrime", "#mystery", "#unsolved", "#crimestories", "#creepy", "#documentary", "#reels"]
    },
    "scary_horror": {
        "name": "Horror & Paranormal Encounters",
        "description": "Terrifying urban legends, paranormal sightings, and nightmare tales.",
        "default_voice": "en-US-ChristopherNeural",
        "tone": "Dark, tense, shocking climax, whispering hooks",
        "visual_theme": "blood_darkness",
        "music_mood": "horror",
        "hashtags": ["#horror", "#scarystories", "#paranormal", "#creepy", "#nightmare", "#ghoststories"]
    },
    "reddit_stories": {
        "name": "Reddit Confessions & Drama",
        "description": "AITA, wild relationship drama, entitled people, and revenge stories.",
        "default_voice": "en-US-GuyNeural",
        "tone": "First-person conversational, emotional, relatable, fast",
        "visual_theme": "neon_grid",
        "music_mood": "chill",
        "hashtags": ["#redditstories", "#aita", "#redditreadings", "#confession", "#storytime", "#drama"]
    },
    "mindset_stoic": {
        "name": "Motivation & Stoic Wisdom",
        "description": "High-value rules, Marcus Aurelius quotes, discipline, and mental toughness.",
        "default_voice": "en-US-BrianNeural",
        "tone": "Authoritative, deep, commanding, inspiring",
        "visual_theme": "golden_slate",
        "music_mood": "epic",
        "hashtags": ["#motivation", "#stoicism", "#mindset", "#discipline", "#success", "#masculinity", "#quotes"]
    },
    "wild_facts": {
        "name": "Mind-Blowing Facts & Science",
        "description": "Bizarre science, strange historical facts, and things that sound fake but are real.",
        "default_voice": "en-US-JennyNeural",
        "tone": "Energetic, mind-blown, punchy, curiosity-driven",
        "visual_theme": "cosmic_cyan",
        "music_mood": "upbeat",
        "hashtags": ["#didyouknow", "#facts", "#mindblown", "#sciencefacts", "#crazyfacts", "#learnontiktok"]
    },
    "conspiracies": {
        "name": "Conspiracies & Secret History",
        "description": "Classified operations, ancient civilizations, and unexplained historical coverups.",
        "default_voice": "en-GB-RyanNeural",
        "tone": "Investigative, skeptical, revelatory, dramatic",
        "visual_theme": "sepia_classified",
        "music_mood": "eerie",
        "hashtags": ["#conspiracy", "#secrethistory", "#ancientsecrets", "#illuminati", "#hiddenfacts"]
    },
    "finance_crypto": {
        "name": "Wealth, Business & Crypto Secrets",
        "description": "Billionaire strategies, economic crashes, scam exposures, and wealth creation.",
        "default_voice": "en-US-EricNeural",
        "tone": "Sharp, insider knowledge, fast-paced analytical",
        "visual_theme": "emerald_matrix",
        "music_mood": "chill",
        "hashtags": ["#money", "#wealth", "#investing", "#finance", "#crypto", "#business", "#entrepreneur"]
    }
}

# Multi-Language Catalog
LANGUAGES = [
    {"code": "en", "name": "English", "flag": "🇺🇸 / 🇬🇧", "default_voice": "en-US-ChristopherNeural"},
    {"code": "hi", "name": "Hindi (हिंदी)", "flag": "🇮🇳", "default_voice": "hi-IN-MadhurNeural"},
    {"code": "es", "name": "Spanish (Español)", "flag": "🇪🇸 / 🇲🇽", "default_voice": "es-ES-AlvaroNeural"},
    {"code": "fr", "name": "French (Français)", "flag": "🇫🇷", "default_voice": "fr-FR-HenriNeural"},
    {"code": "de", "name": "German (Deutsch)", "flag": "🇩🇪", "default_voice": "de-DE-ConradNeural"},
    {"code": "pt", "name": "Portuguese (Português)", "flag": "🇧🇷 / 🇵🇹", "default_voice": "pt-BR-AntonioNeural"},
    {"code": "it", "name": "Italian (Italiano)", "flag": "🇮🇹", "default_voice": "it-IT-DiegoNeural"},
    {"code": "ja", "name": "Japanese (日本語)", "flag": "🇯🇵", "default_voice": "ja-JP-KeitaNeural"}
]

# High-Quality Neural Voices Organized by Language
VOICES = [
    # English Voices
    {"id": "en-US-ChristopherNeural", "lang": "en", "name": "Christopher (US)", "gender": "Male", "style": "Deep, Serious & Dramatic (Mystery/Crime)"},
    {"id": "en-US-GuyNeural", "lang": "en", "name": "Guy (US)", "gender": "Male", "style": "Conversational & Natural (Reddit/Storytime)"},
    {"id": "en-US-BrianNeural", "lang": "en", "name": "Brian (US)", "gender": "Male", "style": "Deep, Authoritative & Strong (Motivation)"},
    {"id": "en-US-EricNeural", "lang": "en", "name": "Eric (US)", "gender": "Male", "style": "Sharp & Confident (Business/Finance)"},
    {"id": "en-US-JennyNeural", "lang": "en", "name": "Jenny (US)", "gender": "Female", "style": "Energetic & Clear (Facts/Science)"},
    {"id": "en-US-AriaNeural", "lang": "en", "name": "Aria (US)", "gender": "Female", "style": "Warm & Expressive (Emotional Stories)"},
    {"id": "en-GB-RyanNeural", "lang": "en", "name": "Ryan (UK)", "gender": "Male", "style": "British Documentary & Mysterious"},
    {"id": "en-GB-SoniaNeural", "lang": "en", "name": "Sonia (UK)", "gender": "Female", "style": "Sophisticated & Elegant"},

    # Hindi Voices
    {"id": "hi-IN-MadhurNeural", "lang": "hi", "name": "Madhur (मधुर - IN)", "gender": "Male", "style": "गहरा और प्रभावशाली (Deep & Dramatic Hindi)"},
    {"id": "hi-IN-SwaraNeural", "lang": "hi", "name": "Swara (स्वरा - IN)", "gender": "Female", "style": "स्पष्ट और आकर्षक (Clear & Engaging Hindi)"},

    # Spanish Voices
    {"id": "es-ES-AlvaroNeural", "lang": "es", "name": "Álvaro (ES)", "gender": "Male", "style": "Voz Profunda y Misteriosa (Deep Spanish Male)"},
    {"id": "es-ES-ElviraNeural", "lang": "es", "name": "Elvira (ES)", "gender": "Female", "style": "Expresiva y Clara (Expressive Spanish Female)"},
    {"id": "es-MX-JorgeNeural", "lang": "es", "name": "Jorge (MX)", "gender": "Male", "style": "Cálido y Dinámico (Latin American Male)"},

    # French Voices
    {"id": "fr-FR-HenriNeural", "lang": "fr", "name": "Henri (FR)", "gender": "Male", "style": "Voix Profonde et Mystérieuse (Deep French Male)"},
    {"id": "fr-FR-DeniseNeural", "lang": "fr", "name": "Denise (FR)", "gender": "Female", "style": "Claire et Expressive (Clear French Female)"},

    # German Voices
    {"id": "de-DE-ConradNeural", "lang": "de", "name": "Conrad (DE)", "gender": "Male", "style": "Tief und Kraftvoll (Deep & Strong German Male)"},
    {"id": "de-DE-KatjaNeural", "lang": "de", "name": "Katja (DE)", "gender": "Female", "style": "Klar und Fesselnd (Clear German Female)"},

    # Portuguese Voices
    {"id": "pt-BR-AntonioNeural", "lang": "pt", "name": "Antônio (BR)", "gender": "Male", "style": "Voz Firme e Envolvente (Firm Brazilian Male)"},
    {"id": "pt-BR-FranciscaNeural", "lang": "pt", "name": "Francisca (BR)", "gender": "Female", "style": "Clara e Dinâmica (Clear Brazilian Female)"},

    # Italian Voices
    {"id": "it-IT-DiegoNeural", "lang": "it", "name": "Diego (IT)", "gender": "Male", "style": "Profondo e Coinvolgente (Deep Italian Male)"},
    {"id": "it-IT-ElsaNeural", "lang": "it", "name": "Elsa (IT)", "gender": "Female", "style": "Chiara ed Espressiva (Clear Italian Female)"},

    # Japanese Voices
    {"id": "ja-JP-KeitaNeural", "lang": "ja", "name": "Keita (JP)", "gender": "Male", "style": "落ち着いた声 (Calm & Deep Japanese Male)"},
    {"id": "ja-JP-NanamiNeural", "lang": "ja", "name": "Nanami (JP)", "gender": "Female", "style": "聞き取りやすい声 (Clear Japanese Female)"}
]

# Speech Speed Options (Default slightly slower for high retention reels)
SPEECH_SPEEDS = [
    {"id": "-15%", "name": "Slower (-15% - Dramatic & Intense)"},
    {"id": "-10%", "name": "Slightly Slower (-10% - Recommended for Reels)", "default": True},
    {"id": "-5%", "name": "Gentle Slower (-5%)"},
    {"id": "+0%", "name": "Normal Pace (0%)"},
    {"id": "+10%", "name": "Fast Paced (+10%)"}
]
