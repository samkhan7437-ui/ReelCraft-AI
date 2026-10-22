import asyncio
import edge_tts
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
import re
import subprocess
from app.config import AUDIO_OUTPUT_DIR

def format_time_ass(seconds: float) -> str:
    """Converts seconds into ASS format: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def get_audio_duration(file_path: str) -> float:
    """Uses ffprobe to obtain precise audio duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 45.0

def get_font_for_language(language: str) -> str:
    """Selects the best font for the target script."""
    lang = (language or "en").lower()
    if lang == "hi":
        return "Nirmala UI"
    elif lang == "ja":
        return "MS Gothic"
    else:
        return "Impact"

def generate_ass_subtitles(
    cues: List[Any],
    ass_path: Path,
    total_duration: float,
    language: str = "en",
    part_number: Optional[int] = None,
    total_parts: Optional[int] = None
):
    """
    Transforms sentence cues into high-energy 2-4 word animated reels captions
    with bold typography, high contrast colors, and thick border.
    Supports Hindi Devanagari, Spanish, French, German, and English.
    """
    font_name = get_font_for_language(language)

    ass_header = f"""[Script Info]
Title: ReelCraft Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: PartBadge,{font_name},52,&H0000FFFF,&H000000FF,&H00000000,&HB0000000,-1,0,0,0,100,100,0,0,3,14,0,8,60,60,160,1
Style: YellowPop,{font_name},76,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,720,1
Style: WhitePop,{font_name},76,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,720,1
Style: GreenPop,{font_name},76,&H0000FF00,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,720,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    # If this is part of a series, render the top badge throughout the video
    if part_number is not None:
        total_time_str = format_time_ass(total_duration)
        if language == "hi":
            badge_label = f"[ भाग {part_number} / {total_parts} ]" if total_parts else f"[ भाग {part_number} ]"
        elif language == "es":
            badge_label = f"[ PARTE {part_number} DE {total_parts} ]" if total_parts else f"[ PARTE {part_number} ]"
        else:
            badge_label = f"[ PART {part_number} OF {total_parts} ]" if total_parts else f"[ PART {part_number} ]"
        events.append(f"Dialogue: 1,0:00:00.00,{total_time_str},PartBadge,,0,0,0,,{badge_label}")

    style_cycle = ["YellowPop", "WhitePop", "GreenPop", "WhitePop"]
    style_idx = 0

    for cue in cues:
        raw_text = cue.content.strip()
        words = raw_text.split()
        if not words:
            continue

        c_start = cue.start.total_seconds()
        c_end = cue.end.total_seconds()
        c_dur = max(0.5, c_end - c_start)

        # Break into 2-3 word segments
        chunk_size = 3
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        total_words = len(words)
        curr_time = c_start
        
        for chunk in chunks:
            chunk_ratio = len(chunk) / total_words
            chunk_dur = c_dur * chunk_ratio
            chunk_start = curr_time
            chunk_end = curr_time + chunk_dur
            curr_time = chunk_end

            # Capitalize if latin script, preserve if non-latin
            phrase = " ".join(chunk)
            if language in ("en", "es", "fr", "de", "pt", "it"):
                phrase = phrase.upper()

            style_name = style_cycle[style_idx % len(style_cycle)]
            style_idx += 1

            s_time = format_time_ass(chunk_start)
            e_time = format_time_ass(chunk_end)
            events.append(f"Dialogue: 0,{s_time},{e_time},{style_name},,0,0,0,,{phrase}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))

async def generate_speech_and_subtitles(
    text: str,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "-10%",
    language: str = "en",
    output_basename: str = None,
    part_number: Optional[int] = None,
    total_parts: Optional[int] = None
) -> Dict[str, Any]:
    """
    Synthesizes speech using Edge-TTS with configurable speech speed rate (default -10% slower)
    and generates synchronized ASS captions in the target language.
    """
    if not output_basename:
        output_basename = f"audio_{uuid.uuid4().hex[:8]}"

    mp3_path = AUDIO_OUTPUT_DIR / f"{output_basename}.mp3"
    ass_path = AUDIO_OUTPUT_DIR / f"{output_basename}.ass"

    # Clean text of markdown or special chars for cleaner TTS speech
    cleaned_text = re.sub(r"[*_#~`]", "", text).strip()

    # Pass speech rate (e.g. "-10%" for dramatic storytelling pace)
    communicate = edge_tts.Communicate(cleaned_text, voice, rate=rate)
    submaker = edge_tts.SubMaker()
    audio_chunks = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            submaker.feed(chunk)

    # Save audio file
    with open(mp3_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    # Get exact audio duration via ffprobe
    duration = get_audio_duration(str(mp3_path))

    # Generate Styled ASS Subtitle File
    generate_ass_subtitles(submaker.cues, ass_path, duration, language, part_number, total_parts)

    return {
        "audio_path": str(mp3_path),
        "ass_path": str(ass_path),
        "duration": duration,
        "rate": rate,
        "language": language,
        "cues_count": len(submaker.cues)
    }
