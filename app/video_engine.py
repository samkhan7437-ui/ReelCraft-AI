import os
import subprocess
import random
import requests
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import (
    BACKGROUNDS_DIR, MUSIC_DIR, VIDEO_OUTPUT_DIR, BASE_DIR, PEXELS_API_KEY, NICHES, OUTPUT_DIR
)

IMAGES_OUTPUT_DIR = OUTPUT_DIR / "images"

def get_ffmpeg_bin() -> str:
    """Finds FFmpeg from system PATH or falls back to imageio-ffmpeg binary."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    return "ffmpeg"

# Niche-specific Procedural Visual Filter Generators
NICHE_VISUAL_FILTERS = {
    "true_crime": (
        "color=c=0x050c18:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=16:allf=t+u,eq=contrast=1.2:brightness=-0.08,"
        "colorbalance=rs=-0.05:gs=0.04:bs=0.18,vignette=PI/3"
    ),
    "scary_horror": (
        "color=c=0x0c0406:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=24:allf=t+u,eq=contrast=1.35:brightness=-0.12,"
        "colorbalance=rs=0.18:gs=-0.05:bs=-0.05,vignette=PI/2.5"
    ),
    "mindset_stoic": (
        "color=c=0x0a0c10:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=12:allf=t+u,eq=contrast=1.28:brightness=-0.05,"
        "colorbalance=rs=0.12:gs=0.06:bs=-0.06,vignette=PI/3.5"
    ),
    "reddit_stories": (
        "color=c=0x100922:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=15:allf=t+u,eq=contrast=1.2:brightness=-0.05,"
        "colorbalance=rs=0.15:gs=0.02:bs=0.22,vignette=PI/3.2"
    ),
    "wild_facts": (
        "color=c=0x04101e:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=18:allf=t+u,eq=contrast=1.25:brightness=-0.06,"
        "colorbalance=gs=0.12:bs=0.25,vignette=PI/3"
    ),
    "conspiracies": (
        "color=c=0x14100a:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=22:allf=t+u,eq=contrast=1.22:brightness=-0.05,"
        "colorbalance=rs=0.18:gs=0.12:bs=-0.12,vignette=PI/2.8"
    ),
    "finance_crypto": (
        "color=c=0x04140c:s=1080x1920:d={d}:r=30[bg];"
        "[bg]noise=alls=14:allf=t+u,eq=contrast=1.24:brightness=-0.05,"
        "colorbalance=rs=-0.04:gs=0.20:bs=0.08,vignette=PI/3.2"
    )
}

def get_available_backgrounds(niche: Optional[str] = None) -> list:
    """Lists all video files in assets/backgrounds, prioritizing niche matches."""
    valid_exts = {".mp4", ".mov", ".mkv", ".webm"}
    all_files = [p for p in BACKGROUNDS_DIR.glob("*") if p.suffix.lower() in valid_exts]
    if niche:
        matched = [p for p in all_files if niche.lower() in p.stem.lower()]
        if matched:
            return matched
    return all_files

def get_available_music(mood: Optional[str] = None) -> list:
    """Lists all valid audio files in assets/music."""
    valid_exts = {".mp3", ".wav", ".aac", ".m4a", ".ogg"}
    music_files = [p for p in MUSIC_DIR.glob("*") if p.suffix.lower() in valid_exts]
    if mood:
        matched = [p for p in music_files if mood.lower() in p.stem.lower()]
        if matched:
            return matched
    return music_files

def fetch_pexels_video(query: str) -> Optional[Path]:
    """Optionally downloads a matching 9:16 vertical video from Pexels if API key configured."""
    if not PEXELS_API_KEY:
        return None
    try:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "orientation": "portrait", "per_page": 5}
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            videos = data.get("videos", [])
            for v in videos:
                # Find vertical files
                files = v.get("video_files", [])
                for vf in files:
                    if vf.get("width", 0) <= vf.get("height", 0) and vf.get("quality") == "hd":
                        download_url = vf.get("link")
                        target = BACKGROUNDS_DIR / f"pexels_{v['id']}.mp4"
                        if not target.exists():
                            r_dl = requests.get(download_url, timeout=30)
                            with open(target, "wb") as f:
                                f.write(r_dl.content)
                        return target
    except Exception as e:
        print(f"[Pexels Fetch Error] {e}")
    return None


def _build_slideshow_input(scene_images: List[Dict[str, Any]], duration: float) -> tuple:
    """
    Builds the FFmpeg input and filtergraph for a Ken Burns-style slideshow
    from scene images. Each image gets smooth zoom/pan animation + crossfade.
    
    Returns:
        (input_args: list, filtergraph: str, video_stream: str)
    """
    valid_images = [s for s in scene_images if s.get("image_path") and Path(s["image_path"]).exists()]
    
    if not valid_images:
        return None, None, None
    
    num_images = len(valid_images)
    # Each scene gets equal duration
    scene_duration = duration / num_images
    # Crossfade overlap between scenes (0.8 seconds)
    xfade_dur = min(0.8, scene_duration * 0.15)
    
    input_args = []
    filter_parts = []
    
    # Add each image as an input with loop + duration
    for i, scene in enumerate(valid_images):
        img_path = scene["image_path"]
        input_args.extend([
            "-loop", "1",
            "-t", str(scene_duration + (xfade_dur if i < num_images - 1 else 0)),
            "-i", str(img_path)
        ])
    
    # Build filtergraph
    # Step 1: Scale each image to 1080x1920 with Ken Burns zoom effect
    scaled_labels = []
    for i in range(num_images):
        # Alternate between zoom-in and slight pan for visual variety
        if i % 3 == 0:
            # Slow zoom in
            effect = (
                f"[{i}:v]scale=1296:2304,zoompan=z='min(zoom+0.0008,1.2)':"
                f"d={int(scene_duration * 30)}:s=1080x1920:fps=30[v{i}]"
            )
        elif i % 3 == 1:
            # Slow pan left to right
            effect = (
                f"[{i}:v]scale=1296:2304,zoompan=z='1.15':"
                f"x='if(eq(on,1),0,x+1)':d={int(scene_duration * 30)}:s=1080x1920:fps=30[v{i}]"
            )
        else:
            # Slow zoom out
            effect = (
                f"[{i}:v]scale=1296:2304,zoompan=z='if(eq(on,1),1.2,max(zoom-0.0008,1.0))':"
                f"d={int(scene_duration * 30)}:s=1080x1920:fps=30[v{i}]"
            )
        filter_parts.append(effect)
        scaled_labels.append(f"[v{i}]")
    
    # Step 2: Crossfade between scenes if multiple images
    if num_images == 1:
        # Single image: just apply dark cinematic overlay
        filter_parts.append(
            f"[v0]eq=brightness=-0.06:contrast=1.15,vignette=PI/3[vslide]"
        )
        final_label = "[vslide]"
    else:
        # Chain crossfades between all scenes
        current_label = scaled_labels[0]
        for i in range(1, num_images):
            next_label = scaled_labels[i]
            out_label = f"[xf{i}]"
            offset = scene_duration * i - xfade_dur * i
            filter_parts.append(
                f"{current_label}{next_label}xfade=transition=fadeblack:"
                f"duration={xfade_dur}:offset={max(0, offset)}{out_label}"
            )
            current_label = out_label
        
        # Apply cinematic post-processing
        filter_parts.append(
            f"{current_label}eq=brightness=-0.06:contrast=1.15,vignette=PI/3[vslide]"
        )
        final_label = "[vslide]"
    
    filtergraph = ";".join(filter_parts)
    return input_args, filtergraph, final_label


def render_reel(
    audio_path: str,
    ass_path: str,
    duration: float,
    output_filename: str,
    niche: Optional[str] = "true_crime",
    script_keywords: Optional[str] = None,
    custom_bg: Optional[str] = None,
    custom_music: Optional[str] = None,
    scene_images: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Renders a vertical 9:16 (1080x1920) Reel with visuals tailored directly to the niche & story.
    Now supports AI-generated scene images as slideshow backgrounds.
    """
    output_path = VIDEO_OUTPUT_DIR / output_filename
    niche_key = niche if niche in NICHES else "true_crime"
    niche_info = NICHES[niche_key]

    # Path escaping for libass
    try:
        safe_ass_path = os.path.relpath(ass_path, os.getcwd()).replace("\\", "/")
    except Exception:
        safe_ass_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

    # Determine visual source priority:
    # 1. AI-generated scene images (slideshow)
    # 2. Custom background video
    # 3. Niche-matched background videos
    # 4. Pexels B-roll
    # 5. Procedural niche filter (fallback)
    
    use_slideshow = False
    slideshow_input_args = None
    slideshow_filter = None
    slideshow_stream = None
    
    if scene_images:
        valid_images = [s for s in scene_images if s.get("image_path") and Path(s["image_path"]).exists()]
        if valid_images:
            slideshow_input_args, slideshow_filter, slideshow_stream = _build_slideshow_input(valid_images, duration)
            if slideshow_input_args:
                use_slideshow = True
                print(f"[Video Engine] 🖼️ Using {len(valid_images)} AI-generated scene images as slideshow")

    # Build FFmpeg command
    cmd = [get_ffmpeg_bin(), "-y"]

    if use_slideshow:
        # Scene image slideshow mode
        cmd.extend(slideshow_input_args)
        # Audio input (index after all image inputs)
        audio_input_idx = len([s for s in scene_images if s.get("image_path") and Path(s["image_path"]).exists()])
        cmd.extend(["-i", str(audio_path)])
        
        # Build full filtergraph with captions burned on top of slideshow
        video_filters = f"{slideshow_filter};[vslide]ass=filename='{safe_ass_path}'[vout]"
        
        # Select background music
        music_path = None
        if custom_music and Path(custom_music).exists():
            music_path = Path(custom_music)
        else:
            available_music = get_available_music(niche_info.get("music_mood"))
            if available_music:
                music_path = random.choice(available_music)
        
        if music_path and music_path.exists():
            cmd.extend(["-stream_loop", "-1", "-i", str(music_path)])
            music_input_idx = audio_input_idx + 1
            audio_filters = f"[{audio_input_idx}:a]volume=1.0[v_voice];[{music_input_idx}:a]volume=0.12[v_music];[v_voice][v_music]amix=inputs=2:duration=first[aout]"
            cmd.extend(["-filter_complex", f"{video_filters};{audio_filters}", "-map", "[vout]", "-map", "[aout]"])
        else:
            cmd.extend(["-filter_complex", video_filters, "-map", "[vout]", "-map", f"{audio_input_idx}:a"])
    
    else:
        # Original video/procedural background mode
        bg_path = None
        if custom_bg and Path(custom_bg).exists():
            bg_path = Path(custom_bg)
        else:
            matched_bgs = get_available_backgrounds(niche_key)
            if matched_bgs:
                bg_path = random.choice(matched_bgs)
            elif PEXELS_API_KEY and script_keywords:
                bg_path = fetch_pexels_video(script_keywords)

        if bg_path and bg_path.exists():
            cmd.extend(["-stream_loop", "-1", "-i", str(bg_path)])
            video_filters = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,eq=brightness=-0.08:contrast=1.15,"
                f"ass=filename='{safe_ass_path}'[vout]"
            )
        else:
            # Generate bespoke procedural visual animation tailored to this niche
            proc_filter = NICHE_VISUAL_FILTERS.get(niche_key, NICHE_VISUAL_FILTERS["true_crime"]).format(d=duration)
            cmd.extend(["-f", "lavfi", "-i", proc_filter])
            video_filters = f"[0:v]ass=filename='{safe_ass_path}'[vout]"

        # Audio inputs & mixing
        cmd.extend(["-i", str(audio_path)])

        music_path = None
        if custom_music and Path(custom_music).exists():
            music_path = Path(custom_music)
        else:
            available_music = get_available_music(niche_info.get("music_mood"))
            if available_music:
                music_path = random.choice(available_music)

        if music_path and music_path.exists():
            cmd.extend(["-stream_loop", "-1", "-i", str(music_path)])
            # Subtle ducking: voiceover at 1.0, background music at 0.12
            audio_filters = "[1:a]volume=1.0[v_voice];[2:a]volume=0.12[v_music];[v_voice][v_music]amix=inputs=2:duration=first[aout]"
            cmd.extend(["-filter_complex", f"{video_filters};{audio_filters}", "-map", "[vout]", "-map", "[aout]"])
        else:
            cmd.extend(["-filter_complex", video_filters, "-map", "[vout]", "-map", "1:a"])

    # Output parameters (H.264 high quality, faststart for instant streaming)
    cmd.extend([
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path)
    ])

    print(f"[FFmpeg Rendering] Generating niche-themed reel: {output_path} (Niche: {niche_key}, Duration: {duration}s, Slideshow: {use_slideshow})")
    process = subprocess.run(cmd, capture_output=True, text=True)

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed with error:\n{process.stderr[-800:]}")

    file_size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2)
    return {
        "success": True,
        "video_path": str(output_path),
        "filename": output_filename,
        "duration": duration,
        "niche": niche_key,
        "file_size_mb": file_size_mb,
        "url": f"/media/videos/{output_filename}",
        "has_ai_visuals": use_slideshow
    }
