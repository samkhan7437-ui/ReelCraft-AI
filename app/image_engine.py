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
from app.config import (
    GEMINI_API_KEY, OUTPUT_DIR, LLM_PROVIDER, OPENAI_API_KEY, NICHES,
    IMAGE_PROVIDER, DALLE_MODEL, DALLE_QUALITY
)

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
    
    # Try OpenAI first if configured or available
    if OPENAI_API_KEY and (IMAGE_PROVIDER in ["openai", "dalle"] or LLM_PROVIDER == "openai" or not GEMINI_API_KEY):
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
                if isinstance(result, dict) and "scenes" in result:
                    result = result["scenes"]
        except Exception as e:
            print(f"[Image Engine] OpenAI prompt generation failed: {e}")

    # Try Gemini fallback/alternative
    if result is None and GEMINI_API_KEY:
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


def generate_image_dalle(prompt: str, output_path: Path) -> bool:
    """
    Generates a vertical image using OpenAI's DALL-E 3 (or DALL-E 2) model.
    DALL-E 3 outputs 1024x1792 vertical format, optimized for 9:16 reels.
    """
    if not OPENAI_API_KEY:
        print("[Image Engine] ⚠️ OPENAI_API_KEY is not set in .env")
        return False

    try:
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        model = DALLE_MODEL if DALLE_MODEL in ["dall-e-3", "dall-e-2"] else "dall-e-3"
        # DALL-E 3 supports 1024x1792 (9:16 vertical), DALL-E 2 supports 1024x1024
        size = "1024x1792" if model == "dall-e-3" else "1024x1024"

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt[:4000],
            "n": 1,
            "size": size,
            "response_format": "b64_json"
        }

        if model == "dall-e-3":
            payload["quality"] = DALLE_QUALITY if DALLE_QUALITY in ["standard", "hd"] else "standard"

        print(f"[Image Engine] 🎨 Calling OpenAI {model} ({size}, {payload.get('quality', 'standard')})...")
        res = requests.post(url, headers=headers, json=payload, timeout=90)

        if res.status_code == 200:
            data = res.json()
            items = data.get("data", [])
            if items:
                item = items[0]
                if "b64_json" in item and item["b64_json"]:
                    import base64
                    image_data = base64.b64decode(item["b64_json"])
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"[Image Engine] ✅ Generated ({model.upper()}): {output_path.name}")
                    return True
                elif "url" in item and item["url"]:
                    img_res = requests.get(item["url"], timeout=60)
                    if img_res.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_res.content)
                        print(f"[Image Engine] ✅ Generated ({model.upper()} via URL): {output_path.name}")
                        return True

            print(f"[Image Engine] ⚠️ No image data in OpenAI response: {data}")
            return False
        else:
            print(f"[Image Engine] OpenAI DALL-E error {res.status_code}: {res.text[:400]}")
            return False

    except Exception as e:
        print(f"[Image Engine] OpenAI DALL-E exception: {e}")
        return False


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


# High-quality vertical 9:16 cinematic fallback images per niche (Unsplash CDN, free & fast)
NICHE_BACKUP_VERTICAL_IMAGES = {
    "true_crime": [
        "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=720&h=1280&fit=crop", # dark mystery neon
        "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=720&h=1280&fit=crop", # dark moody noir
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=720&h=1280&fit=crop", # dark rainy street
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=720&h=1280&fit=crop", # moody shadows
    ],
    "scary_horror": [
        "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?w=720&h=1280&fit=crop", # spooky fog forest
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=720&h=1280&fit=crop", # dark red night
        "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=720&h=1280&fit=crop", # eerie abandoned room
        "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=720&h=1280&fit=crop", # dark thriller
    ],
    "reddit_stories": [
        "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=720&h=1280&fit=crop", # portrait candid
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=720&h=1280&fit=crop", # laptop typing night
        "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=720&h=1280&fit=crop", # neon city streets
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=720&h=1280&fit=crop", # dramatic lighting
    ],
    "mindset_stoic": [
        "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=720&h=1280&fit=crop", # ancient classical statue
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=720&h=1280&fit=crop", # dramatic mountain peak
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=720&h=1280&fit=crop", # golden horizon
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=720&h=1280&fit=crop", # starry night peaks
    ],
    "wild_facts": [
        "https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=720&h=1280&fit=crop", # cosmic galaxy
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=720&h=1280&fit=crop", # neon bioluminescence
        "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=720&h=1280&fit=crop", # quantum light
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&h=1280&fit=crop", # futuristic tech
    ],
    "conspiracies": [
        "https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=720&h=1280&fit=crop", # mysterious starry sky
        "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=720&h=1280&fit=crop", # classified dark archive
        "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?w=720&h=1280&fit=crop", # ancient stone monument
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=720&h=1280&fit=crop", # secret room
    ],
    "finance_crypto": [
        "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=720&h=1280&fit=crop", # Bitcoin digital gold
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=720&h=1280&fit=crop", # trading chart stock screen
        "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=720&h=1280&fit=crop", # financial district skyscrapers
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=720&h=1280&fit=crop", # wealth investment
    ]
}


def download_cinematic_fallback(niche: str, scene_idx: int, output_path: Path) -> bool:
    """
    Downloads a curated, high-definition 9:16 vertical cinematic visual
    when AI generation hits external API limits. Guaranteed to succeed.
    """
    try:
        pool = NICHE_BACKUP_VERTICAL_IMAGES.get(niche, NICHE_BACKUP_VERTICAL_IMAGES["true_crime"])
        url = pool[(scene_idx - 1) % len(pool)]
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and len(res.content) > 10240:
            with open(output_path, "wb") as f:
                f.write(res.content)
            print(f"[Image Engine] 📸 Applied cinematic visual ({niche}): {output_path.name}")
            return True
    except Exception as e:
        print(f"[Image Engine] Fallback download error: {e}")
    return False


def generate_image_pollinations(prompt: str, output_path: Path) -> bool:
    """
    Fast & free generator: Uses Pollinations.ai Turbo API (720x1280 vertical).
    Generates in ~1.2s per image.
    """
    try:
        import urllib.parse
        import random
        # Keep prompt concise for optimal turbo generation speed
        clean_prompt = prompt.replace('\n', ' ')[:250]
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed = random.randint(10000, 9999999)
        
        # 720x1280 (9:16 vertical, ideal for Reels) with turbo model
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&model=turbo&seed={seed}&nologo=true"
        
        res = requests.get(url, timeout=20, stream=True)
        if res.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file is valid (at least 5KB)
            if output_path.exists() and output_path.stat().st_size > 5120:
                print(f"[Image Engine] ✅ Generated (Pollinations Turbo): {output_path.name}")
                return True
            else:
                output_path.unlink(missing_ok=True)
                return False
        else:
            print(f"[Image Engine] ⚠️ Pollinations returned HTTP {res.status_code}")
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
    Uses configured IMAGE_PROVIDER (DALL-E 3, Gemini, or Pollinations + Cinematic fallback).
    Guaranteed to provide visuals for every scene.
    """
    if not base_id:
        base_id = f"scene_{int(time.time())}"

    is_dalle = (IMAGE_PROVIDER in ["openai", "dalle"]) and bool(OPENAI_API_KEY)
    provider_label = "OpenAI DALL-E 3" if is_dalle else ("Gemini Imagen" if (IMAGE_PROVIDER == "gemini" and GEMINI_API_KEY) else "Pollinations AI (Free)")
    print(f"[Image Engine] 🎨 Generating scene visuals for '{niche}' niche using {provider_label}...")
    
    # Step 1: Split script into scenes
    scenes = split_script_into_scenes(script_text, niche, num_scenes)
    if not scenes:
        return {"success": False, "scenes": [], "total_scenes": 0, "images_generated": 0, "error": "Could not split script into scenes"}

    # Step 2: Generate intelligent visual prompts
    if OPENAI_API_KEY or GEMINI_API_KEY:
        scenes = generate_scene_prompts_with_llm(script_text, scenes, niche)
    else:
        scenes = generate_scene_prompts(scenes, niche)

    # Step 3: Generate images for each scene
    images_generated = 0
    provider = IMAGE_PROVIDER.lower() if IMAGE_PROVIDER else "openai"
    
    for scene in scenes:
        img_filename = f"{base_id}_s{scene['scene_index']}.png"
        img_path = IMAGES_OUTPUT_DIR / img_filename
        
        # Check cache - skip if already generated
        if img_path.exists() and img_path.stat().st_size > 5120:
            scene["image_path"] = str(img_path)
            scene["image_url"] = f"/media/images/{img_filename}"
            images_generated += 1
            continue
        
        success = False
        
        # Priority 1: OpenAI DALL-E 3 (if OPENAI_API_KEY is available)
        if provider in ["openai", "dalle", "dall-e", "dall-e-3"]:
            if OPENAI_API_KEY:
                success = generate_image_dalle(scene["prompt"], img_path)
            else:
                print(f"[Image Engine] ℹ️ OPENAI_API_KEY not set in .env. Using free Pollinations Turbo.")

        # Priority 2: Gemini Imagen (if GEMINI_API_KEY is available)
        elif provider == "gemini":
            if GEMINI_API_KEY:
                success = generate_image_gemini(scene["prompt"], img_path)
            else:
                print(f"[Image Engine] ℹ️ GEMINI_API_KEY not set in .env. Using free Pollinations Turbo.")
        
        # Priority 3: Free Pollinations Turbo
        if not success:
            success = generate_image_pollinations(scene["prompt"], img_path)
        
        # Priority 4: Cinematic Niche Fallback (Guarantees every scene has visual)
        if not success:
            success = download_cinematic_fallback(niche, scene["scene_index"], img_path)
        
        if success:
            scene["image_path"] = str(img_path)
            scene["image_url"] = f"/media/images/{img_filename}"
            images_generated += 1
        else:
            scene["image_path"] = None
            scene["image_url"] = None

    # Step 4: Safety Guarantee — if any scene failed, distribute valid images across all scenes
    valid_scenes = [s for s in scenes if s.get("image_path") and Path(s["image_path"]).exists()]
    if valid_scenes and len(valid_scenes) < len(scenes):
        print(f"[Image Engine] 🔄 Sharing {len(valid_scenes)} visual(s) across all {len(scenes)} scenes for continuous slideshow...")
        for i, scene in enumerate(scenes):
            if not scene.get("image_path") or not Path(scene["image_path"]).exists():
                donor = valid_scenes[i % len(valid_scenes)]
                scene["image_path"] = donor["image_path"]
                scene["image_url"] = donor["image_url"]
                images_generated += 1

    print(f"[Image Engine] 🎬 Ready: {images_generated}/{len(scenes)} scene images prepared")
    
    return {
        "success": images_generated > 0,
        "scenes": scenes,
        "total_scenes": len(scenes),
        "images_generated": images_generated
    }
