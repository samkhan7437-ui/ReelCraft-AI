import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import (
    INSTAGRAM_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN, BASE_DIR, VIDEO_OUTPUT_DIR
)

HISTORY_FILE = BASE_DIR / "output" / "posts_history.json"

def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_to_history(post_entry: Dict[str, Any]):
    history = load_history()
    history.insert(0, post_entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:100], f, indent=2)

def check_credentials() -> Dict[str, Any]:
    """Checks if Instagram Graph API credentials are configured in .env."""
    has_account = bool(INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCOUNT_ID.strip())
    has_token = bool(INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCESS_TOKEN.strip())
    return {
        "configured": has_account and has_token,
        "has_account_id": has_account,
        "has_token": has_token,
        "account_id": INSTAGRAM_ACCOUNT_ID if has_account else ""
    }

def publish_reel(
    video_filename: str,
    caption: str,
    public_video_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publishes a video to Instagram Reels via the official Instagram Graph API.
    If credentials are missing or video is local without a public tunnel,
    stores in queue and returns clear setup guidance.
    """
    video_path = VIDEO_OUTPUT_DIR / video_filename
    if not video_path.exists():
        return {"success": False, "error": f"Video file not found: {video_filename}"}

    creds = check_credentials()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # If credentials are not yet configured in .env
    if not creds["configured"]:
        entry = {
            "id": f"sim_{int(time.time())}",
            "filename": video_filename,
            "caption": caption,
            "status": "Ready for Publish (API Setup Required)",
            "timestamp": timestamp,
            "platform": "Instagram Reels",
            "notes": "Configure INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN in Settings / .env to post live to Instagram."
        }
        save_to_history(entry)
        return {
            "success": True,
            "mode": "simulation",
            "message": "Video rendered and queued! To push live to Instagram, enter your Meta Graph API Token in Settings.",
            "post_id": entry["id"]
        }

    # Live Meta Graph API Flow
    try:
        # Note: Instagram Graph API requires a publicly reachable URL for the video container
        # e.g., via ngrok, localtunnel, Cloudflare tunnel, or cloud bucket
        if not public_video_url:
            return {
                "success": False,
                "error": "Instagram Graph API requires a publicly accessible URL for the video. Enable localtunnel/ngrok or enter your media URL."
            }

        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
        params = {
            "media_type": "REELS",
            "video_url": public_video_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        res = requests.post(container_url, data=params, timeout=30)
        data = res.json()
        if "id" not in data:
            return {"success": False, "error": f"Failed to create media container: {data}"}
        
        container_id = data["id"]

        # Step 2: Poll container status until FINISHED
        status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={INSTAGRAM_ACCESS_TOKEN}"
        for _ in range(20):
            time.sleep(3)
            s_res = requests.get(status_url, timeout=15)
            s_data = s_res.json()
            status = s_data.get("status_code")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                return {"success": False, "error": f"Instagram video processing failed: {s_data}"}

        # Step 3: Publish media
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        pub_params = {
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        pub_res = requests.post(publish_url, data=pub_params, timeout=30)
        pub_data = pub_res.json()

        if "id" in pub_data:
            entry = {
                "id": pub_data["id"],
                "filename": video_filename,
                "caption": caption,
                "status": "Published Live",
                "timestamp": timestamp,
                "platform": "Instagram Reels",
                "url": f"https://www.instagram.com/reel/{pub_data['id']}/"
            }
            save_to_history(entry)
            return {"success": True, "published_id": pub_data["id"], "mode": "live"}
        else:
            return {"success": False, "error": f"Publish failed: {pub_data}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
