import time
import asyncio
import threading
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from app.script_engine import generate_script
from app.audio_engine import generate_speech_and_subtitles
from app.video_engine import render_reel
from app.instagram_engine import publish_reel
from app.config import NICHES

scheduler = BackgroundScheduler()
scheduler_state = {
    "enabled": False,
    "interval_hours": 12,
    "niche": "true_crime",
    "is_multipart": False,
    "voice": "en-US-ChristopherNeural",
    "last_run": None,
    "total_generated": 0
}

def autopilot_job():
    """Autonomous job that produces and queues a reel on schedule."""
    if not scheduler_state["enabled"]:
        return
    
    niche = scheduler_state["niche"]
    voice = scheduler_state["voice"]
    is_multipart = scheduler_state["is_multipart"]
    print(f"[Autopilot Triggered] Generating reel for niche: {niche} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. Generate Script
        script_data = generate_script(niche=niche, is_multipart=is_multipart, parts_count=2)
        
        # 2. Audio & Video Render
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if not is_multipart:
            base_id = f"auto_{int(time.time())}"
            audio_info = loop.run_until_complete(
                generate_speech_and_subtitles(
                    text=script_data["script"],
                    voice=voice,
                    output_basename=base_id
                )
            )
            video_info = render_reel(
                audio_path=audio_info["audio_path"],
                ass_path=audio_info["ass_path"],
                duration=audio_info["duration"],
                output_filename=f"{base_id}.mp4",
                niche=niche
            )
            # 3. Queue / Publish
            caption = f"{script_data.get('caption', '')}\n\n{' '.join(script_data.get('hashtags', []))}"
            publish_reel(video_info["filename"], caption=caption)
        else:
            # Multi-part
            parts = script_data.get("parts", [])
            for p in parts:
                base_id = f"auto_{int(time.time())}_part{p['part']}"
                audio_info = loop.run_until_complete(
                    generate_speech_and_subtitles(
                        text=p["script"],
                        voice=voice,
                        output_basename=base_id,
                        part_number=p["part"],
                        total_parts=len(parts)
                    )
                )
                video_info = render_reel(
                    audio_path=audio_info["audio_path"],
                    ass_path=audio_info["ass_path"],
                    duration=audio_info["duration"],
                    output_filename=f"{base_id}.mp4",
                    niche=niche
                )
                caption = f"Part {p['part']}: {script_data.get('caption', '')}\n\n{' '.join(script_data.get('hashtags', []))}"
                publish_reel(video_info["filename"], caption=caption)

        scheduler_state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        scheduler_state["total_generated"] += 1
        print("[Autopilot Success] New Reel produced and queued successfully.")

    except Exception as e:
        print(f"[Autopilot Error] {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def configure_autopilot(enabled: bool, interval_hours: int = 12, niche: str = "true_crime", voice: str = "en-US-ChristopherNeural", is_multipart: bool = False):
    scheduler_state["enabled"] = enabled
    scheduler_state["interval_hours"] = interval_hours
    scheduler_state["niche"] = niche
    scheduler_state["voice"] = voice
    scheduler_state["is_multipart"] = is_multipart

    # Remove existing autopilot job if any
    try:
        scheduler.remove_job("autopilot_job")
    except Exception:
        pass

    if enabled:
        scheduler.add_job(
            autopilot_job,
            "interval",
            hours=interval_hours,
            id="autopilot_job",
            replace_existing=True
        )
        print(f"[Scheduler] Autopilot started: Every {interval_hours} hours for niche '{niche}'.")

def get_scheduler_status() -> Dict[str, Any]:
    next_run = None
    job = scheduler.get_job("autopilot_job")
    if job and job.next_run_time:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        **scheduler_state,
        "is_active": scheduler_state["enabled"],
        "next_run": next_run
    }
