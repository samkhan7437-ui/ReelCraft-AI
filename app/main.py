import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from app.config import (
    BASE_DIR, NICHES, VOICES, LANGUAGES, SPEECH_SPEEDS, VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR,
    LLM_PROVIDER, OLLAMA_MODEL, INSTAGRAM_ACCOUNT_ID, OUTPUT_DIR
)
from app.script_engine import generate_script
from app.audio_engine import generate_speech_and_subtitles
from app.video_engine import render_reel, get_available_backgrounds, get_available_music
from app.image_engine import generate_scene_images, IMAGES_OUTPUT_DIR
from app.instagram_engine import publish_reel, load_history, check_credentials
from app.scheduler import start_scheduler, configure_autopilot, get_scheduler_status

app = FastAPI(
    title="ReelCraft AI Studio",
    description="Automated Faceless Instagram Reels Generator & Auto-Poster",
    version="1.2.0"
)

# Mount Static Files and Media Directories
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/media/videos", StaticFiles(directory=str(VIDEO_OUTPUT_DIR)), name="videos")
app.mount("/media/audio", StaticFiles(directory=str(AUDIO_OUTPUT_DIR)), name="audio")
app.mount("/media/images", StaticFiles(directory=str(IMAGES_OUTPUT_DIR)), name="images")

@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "ReelCraft AI backend is running."}

# Models
class ScriptRequest(BaseModel):
    niche: str
    topic: Optional[str] = None
    is_multipart: bool = False
    parts_count: int = 2
    language: Optional[str] = "en"

class RenderRequest(BaseModel):
    script_data: Dict[str, Any]
    voice: Optional[str] = "en-US-ChristopherNeural"
    speech_speed: Optional[str] = "-10%"
    language: Optional[str] = "en"
    custom_bg: Optional[str] = None
    custom_music: Optional[str] = None
    enable_ai_visuals: Optional[bool] = True
    num_scenes: Optional[int] = 4

class GenerateImagesRequest(BaseModel):
    script_text: str
    niche: str = "true_crime"
    num_scenes: int = 4

class PublishRequest(BaseModel):
    filename: str
    caption: str
    public_url: Optional[str] = None

class AutopilotRequest(BaseModel):
    enabled: bool
    interval_hours: int = 12
    niche: str = "true_crime"
    voice: str = "en-US-ChristopherNeural"
    is_multipart: bool = False

# API Endpoints
@app.get("/api/niches")
def get_niches():
    return {"niches": NICHES}

@app.get("/api/languages")
def get_languages():
    return {"languages": LANGUAGES}

@app.get("/api/speeds")
def get_speeds():
    return {"speeds": SPEECH_SPEEDS}

@app.get("/api/voices")
def get_voices(lang: Optional[str] = None):
    if lang:
        filtered = [v for v in VOICES if v.get("lang") == lang]
        return {"voices": filtered if filtered else VOICES}
    return {"voices": VOICES}

@app.get("/api/assets")
def get_assets():
    bgs = [p.name for p in get_available_backgrounds()]
    musics = [p.name for p in get_available_music()]
    return {"backgrounds": bgs, "music": musics}

@app.post("/api/generate-script")
def api_generate_script(req: ScriptRequest):
    try:
        script_res = generate_script(
            niche=req.niche,
            topic=req.topic,
            is_multipart=req.is_multipart,
            parts_count=req.parts_count,
            language=req.language or "en"
        )
        return {"success": True, "data": script_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-images")
def api_generate_images(req: GenerateImagesRequest):
    """
    Standalone endpoint to generate AI scene images from a script.
    Useful for previewing visuals before rendering the full video.
    """
    try:
        base_id = f"preview_{int(time.time())}"
        result = generate_scene_images(
            script_text=req.script_text,
            niche=req.niche,
            base_id=base_id,
            num_scenes=req.num_scenes
        )
        return {"success": result["success"], "data": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/render-video")
async def api_render_video(req: RenderRequest):
    data = req.script_data
    voice = req.voice or "en-US-ChristopherNeural"
    speech_speed = req.speech_speed or "-10%"
    language = req.language or data.get("language", "en")
    niche = data.get("niche", "true_crime")
    is_multipart = data.get("is_multipart", False)
    enable_ai_visuals = req.enable_ai_visuals if req.enable_ai_visuals is not None else True
    num_scenes = req.num_scenes or 4
    rendered_videos = []

    try:
        if not is_multipart:
            # Single Reel
            text = data.get("script", "")
            base_id = f"reel_{int(time.time())}"
            
            # 1. Generate AI Scene Images (if enabled)
            scene_images = None
            if enable_ai_visuals and text:
                print(f"[Pipeline] 🎨 Generating AI scene images...")
                img_result = generate_scene_images(
                    script_text=text,
                    niche=niche,
                    base_id=base_id,
                    num_scenes=num_scenes
                )
                if img_result["success"]:
                    scene_images = img_result["scenes"]
                    print(f"[Pipeline] ✅ {img_result['images_generated']} scene images ready")
                else:
                    print(f"[Pipeline] ⚠️ Image generation failed, falling back to procedural visuals")

            # 2. Generate Voice & Synchronized Captions (with slower speed rate)
            audio_info = await generate_speech_and_subtitles(
                text=text,
                voice=voice,
                rate=speech_speed,
                language=language,
                output_basename=base_id
            )

            # 3. Render Niche-Themed Video (with scene images if available)
            out_filename = f"{base_id}.mp4"
            video_info = render_reel(
                audio_path=audio_info["audio_path"],
                ass_path=audio_info["ass_path"],
                duration=audio_info["duration"],
                output_filename=out_filename,
                niche=niche,
                script_keywords=data.get("title"),
                custom_bg=req.custom_bg,
                custom_music=req.custom_music,
                scene_images=scene_images
            )

            rendered_videos.append({
                "part": 1,
                "title": data.get("title", "Untitled Reel"),
                "filename": out_filename,
                "url": video_info["url"],
                "duration": video_info["duration"],
                "file_size_mb": video_info["file_size_mb"],
                "caption": f"{data.get('caption', '')}\n\n{' '.join(data.get('hashtags', []))}",
                "has_ai_visuals": video_info.get("has_ai_visuals", False),
                "scene_images": [
                    {"scene": s["scene_index"], "url": s.get("image_url")}
                    for s in (scene_images or []) if s.get("image_url")
                ]
            })
        else:
            # Multi-part series
            parts = data.get("parts", [])
            total_parts = len(parts)

            for p in parts:
                p_num = p.get("part", 1)
                text = p.get("script", "")
                base_id = f"series_{int(time.time())}_part{p_num}"

                # Generate AI images for each part
                scene_images = None
                if enable_ai_visuals and text:
                    img_result = generate_scene_images(
                        script_text=text,
                        niche=niche,
                        base_id=base_id,
                        num_scenes=num_scenes
                    )
                    if img_result["success"]:
                        scene_images = img_result["scenes"]

                audio_info = await generate_speech_and_subtitles(
                    text=text,
                    voice=voice,
                    rate=speech_speed,
                    language=language,
                    output_basename=base_id,
                    part_number=p_num,
                    total_parts=total_parts
                )

                out_filename = f"{base_id}.mp4"
                video_info = render_reel(
                    audio_path=audio_info["audio_path"],
                    ass_path=audio_info["ass_path"],
                    duration=audio_info["duration"],
                    output_filename=out_filename,
                    niche=niche,
                    script_keywords=data.get("title"),
                    custom_bg=req.custom_bg,
                    custom_music=req.custom_music,
                    scene_images=scene_images
                )

                rendered_videos.append({
                    "part": p_num,
                    "title": f"{data.get('title', 'Series')} (Part {p_num})",
                    "filename": out_filename,
                    "url": video_info["url"],
                    "duration": video_info["duration"],
                    "file_size_mb": video_info["file_size_mb"],
                    "caption": f"Part {p_num}: {data.get('caption', '')}\n\n{' '.join(data.get('hashtags', []))}",
                    "has_ai_visuals": video_info.get("has_ai_visuals", False),
                    "scene_images": [
                        {"scene": s["scene_index"], "url": s.get("image_url")}
                        for s in (scene_images or []) if s.get("image_url")
                    ]
                })

        return {"success": True, "videos": rendered_videos}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/publish")
def api_publish_reel(req: PublishRequest):
    res = publish_reel(
        video_filename=req.filename,
        caption=req.caption,
        public_video_url=req.public_url
    )
    return res

@app.get("/api/history")
def api_get_history():
    return {"history": load_history()}

@app.get("/api/autopilot")
def api_get_autopilot():
    return get_scheduler_status()

@app.post("/api/autopilot")
def api_post_autopilot(req: AutopilotRequest):
    configure_autopilot(
        enabled=req.enabled,
        interval_hours=req.interval_hours,
        niche=req.niche,
        voice=req.voice,
        is_multipart=req.is_multipart
    )
    return {"success": True, "status": get_scheduler_status()}

@app.get("/api/settings")
def api_get_settings():
    creds = check_credentials()
    return {
        "llm_provider": LLM_PROVIDER,
        "ollama_model": OLLAMA_MODEL,
        "instagram": creds
    }

if __name__ == "__main__":
    from app.config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
