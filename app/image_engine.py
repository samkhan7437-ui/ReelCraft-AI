"""
ReelCraft AI — Scene-by-Scene AI Image Generator
Analyzes scripts, splits them into visual scenes, generates cinematic
illustrations via Gemini Imagen, and returns them for slideshow-based video rendering.
"""

import os
import re
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import GEMINI_API_KEY, OUTPUT_DIR, LLM_PROVIDER, OPENAI_API_KEY, NICHES

IMAGES_OUTPUT_DIR = OUTPUT_DIR / "images"
IMAGES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Visual style presets per niche for cinematic scene generation
NICHE_VISUAL_STYLES = {
    "true_crime": "dark cinematic noir photography, dramatic shadows, cold blue tones, atmospheric fog, film grain, moody crime scene aesthetic",
    "scary_horror": "dark horror illustration, eerie atmosphere, deep red and black tones, volumetric fog, unsettling shadows, nightmare aesthetic, cinematic horror lighting",
    "reddit_stories": "modern digital illustration, warm indoor lighting, realistic everyday scenes, soft natural colors, relatable slice-of-life aesthetic",
    "mindset_stoic": "epic cinematic photography, golden hour lighting, ancient Greek marble statues, dramatic clouds, stoic philosophy aesthetic, dark and gold tones",
    "wild_facts": "vibrant scientific illustration, cosmic colors, detailed macro photography style, electric blue and cyan tones, futuristic infographic aesthetic",
    "conspiracies": "vintage classified document aesthetic, sepia tones, grainy film photography, redacted stamps, mysterious archive room lighting, cold war era",
    "finance_crypto": "sleek futuristic trading floor, neon green matrix code, dark backgrounds, holographic charts, premium financial aesthetic, cyber-wealth",
}

# Maximum number of scenes to generate per script
MAX_SCENES = 5
MIN_SCENES = 3


def split_script_into_scenes(script_text: str, niche: str = "true_crime", num_scenes: int = 4) -> List[Dict[str, Any]]:
    """
    Splits a script into visual scenes by breaking it into roughly equal narrative chunks.
    Each scene gets a descriptive visual prompt for image generation.
    """
    # Clean up the text
    clean_text = re.sub(r'[*_#~`]', '', script_text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    # Clamp scene count
    num_scenes = max(MIN_SCENES, min(num_scenes, MAX_SCENES, len(sentences)))

    # Distribute sentences across scenes
    scenes = []
    chunk_size = max(1, len(sentences) // num_scenes)
    
    for i in range(num_scenes):
        start_idx = i * chunk_size
        if i == num_scenes - 1:
            # Last scene gets all remaining sentences
            end_idx = len(sentences)
        else:
            end_idx = start_idx + chunk_size
        
        scene_text = " ".join(sentences[start_idx:end_idx])
        if not scene_text:
            continue
            
        scenes.append({
            "scene_index": i + 1,
            "text": scene_text,
            "prompt": None,  # Will be generated
        })

    return scenes


def generate_scene_prompts(scenes: List[Dict[str, Any]], niche: str = "true_crime") -> List[Dict[str, Any]]:
    """
    Creates detailed image generation prompts for each scene based on the narrative text.
    Uses the niche visual style to maintain consistent aesthetic.
    """
    niche_style = NICHE_VISUAL_STYLES.get(niche, NICHE_VISUAL_STYLES["true_crime"])

    for scene in scenes:
        text = scene["text"]
        
        # Extract key visual elements from the text
        # Take the first ~80 chars of the scene as the subject description
        subject = text[:120].strip()
        if len(text) > 120:
            subject = subject.rsplit(' ', 1)[0] + "..."
        
        # Build a cinematic prompt
        prompt = (
            f"Cinematic illustration for a vertical social media reel. "
            f"Scene depicts: {subject} "
            f"Style: {niche_style}. "
            f"Aspect ratio 9:16 vertical, high quality, no text or words in the image, "
            f"photorealistic cinematic lighting, 4K detail."
        )
        scene["prompt"] = prompt

    return scenes


def generate_scene_prompts_with_llm(script_text: str, scenes: List[Dict[str, Any]], niche: str = "true_crime") -> List[Dict[str, Any]]:
    """
    Uses Gemini or OpenAI to generate intelligent, contextual image prompts
    for each scene. Falls back to basic prompt generation if LLM fails.
    """
    niche_style = NICHE_VISUAL_STYLES.get(niche, NICHE_VISUAL_STYLES["true_crime"])
    
    scene_descriptions = []
    for s in scenes:
        scene_descriptions.append(f"Scene {s['scene_index']}: \"{s['text']}\"")
    
    llm_prompt = f"""You are a cinematic storyboard artist for viral Instagram Reels.
Given the following script scenes, generate a detailed image generation prompt for each scene.

Full Script Context: "{script_text[:500]}"

Scenes:
{chr(10).join(scene_descriptions)}

Niche Visual Style: {niche_style}

Rules:
- Each prompt should describe a VISUAL SCENE, not text. Never include any text/words/letters in the image.
- Make each scene visually distinct but maintaining a consistent cinematic style.
- Focus on mood, lighting, composition, and subject matter.
- Each prompt should be 1-2 sentences, under 200 characters.
- Format: 9:16 vertical, photorealistic cinematic style.

Return ONLY a valid JSON array with this exact structure:
[
  {{"scene": 1, "prompt": "Detailed visual prompt for scene 1..."}},
  {{"scene": 2, "prompt": "Detailed visual prompt for scene 2..."}}
]"""

    result = None
    
    # Try Gemini
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": llm_prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(raw_text)
        except Exception as e:
            print(f"[Image Engine] Gemini prompt generation failed: {e}")

    # Try OpenAI fallback
    if result is None and OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a cinematic storyboard artist. Output only valid JSON arrays."},
                    {"role": "user", "content": llm_prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                result = json.loads(data["choices"][0]["message"]["content"])
                # Handle if wrapped in an object
                if isinstance(result, dict) and "scenes" in result:
                    result = result["scenes"]
        except Exception as e:
            print(f"[Image Engine] OpenAI prompt generation failed: {e}")

    # Apply LLM-generated prompts to scenes
    if result and isinstance(result, list):
        for item in result:
            scene_num = item.get("scene", 0)
            prompt = item.get("prompt", "")
            if prompt:
                for scene in scenes:
                    if scene["scene_index"] == scene_num:
                        scene["prompt"] = (
                            f"{prompt} "
                            f"Style: {niche_style}. "
                            f"9:16 vertical aspect ratio, no text or words in the image, "
                            f"cinematic lighting, 4K."
                        )
                        break

    # Fill in any scenes that didn't get LLM prompts
    for scene in scenes:
        if not scene.get("prompt"):
            text = scene["text"][:120].strip()
            scene["prompt"] = (
                f"Cinematic illustration: {text}. "
                f"Style: {niche_style}. "
                f"9:16 vertical, no text in image, cinematic lighting, 4K."
            )

    return scenes


def generate_image_gemini(prompt: str, output_path: Path) -> bool:
    """
    Generates an image using Gemini's Imagen model via the Gemini API.
    """
    if not GEMINI_API_KEY:
        return False

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }
        
        res = requests.post(url, json=payload, timeout=60)
        
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        import base64
                        image_data = base64.b64decode(part["inlineData"]["data"])
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        print(f"[Image Engine] ✅ Generated: {output_path.name}")
                        return True
            
            print(f"[Image Engine] ⚠️ No image in Gemini response")
            return False
        else:
            print(f"[Image Engine] Gemini Imagen API error {res.status_code}: {res.text[:300]}")
            return False
            
    except Exception as e:
        print(f"[Image Engine] Gemini Imagen error: {e}")
        return False


def generate_image_pollinations(prompt: str, output_path: Path) -> bool:
    """
    Free fallback: Uses Pollinations.ai API for image generation (no API key needed).
    """
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        # Pollinations.ai free image API - 9:16 vertical
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={int(time.time())}&nologo=true"
        
        res = requests.get(url, timeout=60, stream=True)
        if res.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file is valid (at least 10KB)
            if output_path.stat().st_size > 10240:
                print(f"[Image Engine] ✅ Generated (Pollinations): {output_path.name}")
                return True
            else:
                output_path.unlink(missing_ok=True)
                return False
        
        return False
    except Exception as e:
        print(f"[Image Engine] Pollinations error: {e}")
        return False


def generate_scene_images(
    script_text: str,
    niche: str = "true_crime",
    base_id: str = None,
    num_scenes: int = 4
) -> Dict[str, Any]:
    """
    Main pipeline: Splits script into scenes, generates visual prompts,
    creates AI images for each scene, returns scene data with image paths.
    
    Returns:
        {
            "success": True/False,
            "scenes": [
                {
                    "scene_index": 1,
                    "text": "...",
                    "prompt": "...",
                    "image_path": "/path/to/image.png",
                    "image_url": "/media/images/scene_xxx.png"
                },
                ...
            ],
            "total_scenes": 4,
            "images_generated": 3
        }
    """
    if not base_id:
        base_id = f"scene_{int(time.time())}"

    print(f"[Image Engine] 🎨 Starting scene image generation for '{niche}' niche...")
    
    # Step 1: Split script into scenes
    scenes = split_script_into_scenes(script_text, niche, num_scenes)
    if not scenes:
        return {"success": False, "scenes": [], "total_scenes": 0, "images_generated": 0, "error": "Could not split script into scenes"}

    # Step 2: Generate intelligent visual prompts
    if GEMINI_API_KEY or OPENAI_API_KEY:
        scenes = generate_scene_prompts_with_llm(script_text, scenes, niche)
    else:
        scenes = generate_scene_prompts(scenes, niche)

    # Step 3: Generate images for each scene
    images_generated = 0
    
    for scene in scenes:
        img_filename = f"{base_id}_s{scene['scene_index']}.png"
        img_path = IMAGES_OUTPUT_DIR / img_filename
        
        # Check cache - skip if already generated
        if img_path.exists() and img_path.stat().st_size > 10240:
            scene["image_path"] = str(img_path)
            scene["image_url"] = f"/media/images/{img_filename}"
            images_generated += 1
            continue
        
        success = False
        
        # Try Gemini Imagen first
        if GEMINI_API_KEY:
            success = generate_image_gemini(scene["prompt"], img_path)
        
        # Fallback to Pollinations (free)
        if not success:
            success = generate_image_pollinations(scene["prompt"], img_path)
        
        if success:
            scene["image_path"] = str(img_path)
            scene["image_url"] = f"/media/images/{img_filename}"
            images_generated += 1
        else:
            scene["image_path"] = None
            scene["image_url"] = None
            print(f"[Image Engine] ⚠️ Failed to generate image for scene {scene['scene_index']}")

    print(f"[Image Engine] 🎬 Generated {images_generated}/{len(scenes)} scene images")
    
    return {
        "success": images_generated > 0,
        "scenes": scenes,
        "total_scenes": len(scenes),
        "images_generated": images_generated
    }
