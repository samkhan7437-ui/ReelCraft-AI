import json
import random
import os
import requests
from typing import Dict, Any, List, Optional
from app.config import (
    NICHES, LANGUAGES, LLM_PROVIDER, OLLAMA_HOST, OLLAMA_MODEL, GEMINI_API_KEY, OPENAI_API_KEY
)

# Multi-lingual Curated Stories Fallback Pool
BUILTIN_STORIES = {
    "true_crime": [
        {
            "title": "The Knock at 8,000 Feet",
            "title_hi": "समुद्र के 8,000 फीट नीचे रहस्यमयी दस्तक",
            "title_es": "El Golpe a 8,000 Pies de Profundidad",
            "single": "In 1974, deep-sea diver Robert Shaw was stationed inside an underwater capsule 8,000 feet beneath the Pacific. At 2:14 AM, the communications went dead. Total silence. Then, from the outside of the titanium hull, he heard three deliberate, rhythmic knocks. Shaw checked the sonar: nothing was within miles. When his capsule was finally brought to the surface, engineers found three deep indentations on the steel hatch... perfectly matching the shape of a human hand. Shaw resigned the next morning and never looked at the ocean again. What do you think knocked on that door? Follow for more mysteries.",
            "single_hi": "१९७४ में गहरे समुद्र के गोताखोर रॉबर्ट शॉ प्रशांत महासागर में आठ हजार फीट नीचे एक कैप्सूल में बंद थे। रात के दो बजकर चौदह मिनट पर उनका संपर्क टूट गया। सन्नाटा छा गया। तभी टाइटेनियम की दीवार के बाहर से उन्हें तीन लगातार खटखटाने की आवाजें सुनाई दीं। जैसे कोई लोहे पर उंगलियों से दस्तक दे रहा हो। सोनार पर पचास मील तक कोई जीव नहीं था। जब कैप्सूल ऊपर लाया गया, तो स्टील के गेट पर इंसान की उंगलियों के तीन गहरे निशान मिले। रॉबर्ट ने अगली सुबह नौकरी छोड़ दी और फिर कभी समुद्र की तरफ नहीं देखा। आपको क्या लगता है वह क्या था? फॉलो करें ऐसी ही अनसुलझी कहानियों के लिए।",
            "single_es": "En 1974, el buzo Robert Shaw estaba dentro de una cápsula a ocho mil pies bajo el Pacífico. A las 2:14 AM, las comunicaciones se cortaron por completo. Silencio total. De pronto, desde el exterior del casco de titanio, escuchó tres golpes lentos y deliberados. Nudillos humanos contra el metal. El sonar no detectó nada a kilómetros. Cuando finalmente subieron la cápsula a la superficie, los ingenieros encontraron tres marcas profundas en la compuerta de acero... que coincidían exactamente con la forma de dedos humanos. Shaw renunció a la mañana siguiente. ¿Qué crees que golpeó esa puerta? Síguenos para más misterios.",
            "parts": [
                {
                    "part": 1,
                    "text": "In 1974, deep-sea diver Robert Shaw was stationed inside a pressurized research capsule eight thousand feet beneath the Pacific Ocean. At 2:14 AM, communications went dead. Complete darkness. Then, from the outside of the titanium hull, he heard three deliberate, heavy knocks. He checked the radar, but there was nothing within fifty miles. But what he saw when he turned on the external floodlights will chill you to your core. Follow for Part 2 to see what was waiting outside.",
                    "text_hi": "१९७४ में गोताखोर रॉबर्ट शॉ प्रशांत महासागर में आठ हजार फीट नीचे एक रिसर्च कैप्सूल में अकेले थे। रात के २:१४ बजे सभी संचार बंद हो गए। घना अंधेरा। तभी बाहर से तीन भारी दस्तकें सुनाई दीं। रडार पर पचास मील तक कुछ नहीं था। लेकिन जब उन्होंने बाहर की लाइट जलाई, तो जो दिखा वो आपकी रूह कंपा देगा। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 1974, el buzo Robert Shaw estaba dentro de una cápsula de investigación a ocho mil pies bajo el Pacífico. A las 2:14 AM, las comunicaciones se cortaron. Oscuridad total. De repente, desde el exterior del casco, escuchó tres golpes pesados. El radar no marcaba nada a cincuenta millas. Pero lo que vio al encender los reflectores te dejará sin aliento. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "When Robert turned on the external floodlights outside the submarine hatch, the water was pitch black. But pressed directly against the thick glass was a pale, humanoid shape staring back with no eyes. And right as the backup alarms began screaming, the object vanished into the abyss. When his capsule was finally brought to the surface, the engineers found three fresh indentations on the steel hatch. Exactly the size of human fingers. Follow for more unsolved mysteries.",
                    "text_hi": "जब रॉबर्ट ने बाहर की फ्लडलाइट जलाई, तो कांच के ठीक सामने एक बिना आंखों वाली पीली इंसानी आकृति घूर रही थी। अलार्म बजते ही वह काली गहराइयों में गायब हो गई। सतह पर आने पर इंजीनियरों को स्टील पर तीन ताजा उंगलियों के निशान मिले। आपको क्या लगता है वह क्या था? कमेंट करें।",
                    "text_es": "Cuando Robert encendió los reflectores, el agua estaba negra como la tinta. Pero pegada al cristal había una figura humanoide pálida mirando fijamente sin ojos. Y cuando saltaron las alarmas, desapareció en el abismo. Al llegar a la superficie, encontraron tres marcas profundas en el acero, del tamaño exacto de dedos humanos. ¿Qué opinas? Comenta abajo."
                }
            ]
        }
    ],
    "scary_horror": [
        {
            "title": "The Midnight Whistler",
            "title_hi": "आधी रात की खौफनाक सीटी",
            "title_es": "El Silbido de la Medianoche",
            "single": "If you ever wake up at 3:00 AM and hear someone softly whistling a lullaby right outside your bedroom door, whatever you do, do not open your eyes. In 2021, an audio recording from an Appalachian cabin went viral. A solo hiker recorded 14 minutes of rhythmic whistling circling his tent. When park rangers inspected the site the next day, they found no footprints in the mud... only scrape marks in the branches 20 feet in the air. The locals have a name for it, and they say if you answer the whistle, it never leaves. Have you ever heard something unexplained at night?",
            "single_hi": "अगर आप कभी रात के तीन बजे जागें और अपने कमरे के ठीक बाहर किसी को धीमी सीटी बजाते सुनें, तो अपनी आंखें मत खोलना। २०२१ में एक अकेले हाइकर ने अपने तंबू के चारों ओर चौदह मिनट तक सीटी की खौफनाक आवाज रिकॉर्ड की। अगली सुबह जब रेंजर पहुंचे, तो जमीन पर कोई निशान नहीं थे... लेकिन बीस फीट ऊंचे पेड़ों की डालियों पर पंजों के खुरचने के निशान थे। स्थानीय लोग कहते हैं कि अगर आपने उस सीटी का जवाब दिया, तो वह कभी वापस नहीं जाता। क्या आपने कभी रात में ऐसा कुछ सुना है?",
            "single_es": "Si alguna vez te despiertas a las 3:00 AM y escuchas a alguien silbando suavemente frente a tu puerta, pase lo que pase, no abras los ojos. En 2021, un excursionista grabó 14 minutos de un silbido rítmico rodeando su tienda. Al día siguiente, los guardabosques no encontraron huellas en el barro... solo marcas de garras en las ramas a 6 metros de altura. Los lugareños dicen que si respondes al silbido, nunca se va. ¿Has oído algo inexplicable por la noche?",
            "parts": [
                {
                    "part": 1,
                    "text": "If you wake up at 3:00 AM and hear whistling outside your door, do not make a sound. In 2021, a solo hiker in the Appalachian Mountains recorded something so disturbing that park rangers refused to release the full audio to the public. For twenty minutes, a voice whispered his childhood nickname from outside his tent. But the hiker lived alone and had never told anyone his name. Follow for Part 2 to hear the rest of the recording.",
                    "text_hi": "अगर रात के तीन बजे आपको बाहर सीटी सुनाई दे, तो एक शब्द भी मत बोलना। २०२१ में पहाड़ों में एक हाइकर ने कुछ ऐसा रिकॉर्ड किया जिसे अधिकारियों ने छिपा लिया। बीस मिनट तक कोई उसके बचपन का नाम पुकारता रहा, जबकि वो वहां बिल्कुल अकेला था। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Si te despiertas a las 3:00 AM y escuchas un silbido afuera, no hagas ruido. En 2021, un senderista grabó algo tan aterrador que las autoridades no quisieron publicar el audio completo. Una voz susurraba su apodo de la infancia fuera de su tienda. Pero él estaba solo y nadie sabía su nombre. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "As the hiker clutched his flashlight, the whispers stopped, replaced by the sound of heavy footsteps circling the tent. When morning broke and the hiker finally dashed to his truck, rangers found zero footprints on the ground. Instead, twenty feet up in the surrounding pine trees, the bark had been peeled off by what looked like giant claws. He sold his hiking gear that week. Would you spend one night in those woods? Drop your thoughts below.",
                    "text_hi": "जैसे ही उसने टॉर्च पकड़ी, कदमों की भारी आवाजें तंबू के इर्द-गिर्द घूमने लगीं। सुबह जब वो भागा, तो जमीन पर कोई पैरों के निशान नहीं थे, बल्कि बीस फीट ऊंचे पेड़ों की छाल विशाल पंजों से उखड़ी हुई थी। क्या आप उस जंगल में एक रात बिताने की हिम्मत करेंगे? कमेंट करें।",
                    "text_es": "Mientras sostenía su linterna, los susurros cesaron y comenzaron pasos pesados alrededor de la tienda. Al amanecer, no había huellas en el suelo. En cambio, a seis metros de altura en los pinos, la corteza había sido arrancada por garras gigantescas. Vendió todo su equipo esa misma semana. ¿Pasarías una noche allí? Comenta abajo."
                }
            ]
        }
    ],
    "mindset_stoic": [
        {
            "title": "The Stoic Law of Silence",
            "title_hi": "मौन की शक्ति और स्टोइक नियम",
            "title_es": "La Ley Estoica del Silencio",
            "single": "Marcus Aurelius wrote: 'Waste no more time arguing what a good man should be. Be one.' Most men fail in life because they announce their goals before they even take the first step. They crave the cheap dopamine of praise for things they haven't achieved. In ancient Sparta, soldiers were taught to answer complex questions in a single, sharp sentence. If you want respect, master the art of silence. Let your discipline speak so loud that you never have to raise your voice. Double tap if you needed this reminder today.",
            "single_hi": "मार्कस ऑरेलियस ने लिखा था: एक अच्छा इंसान कैसा होना चाहिए, इस पर बहस करने में वक्त बर्बाद मत करो। बस अच्छे बनो। निन्यानवे प्रतिशत लोग इसलिए असफल होते हैं क्योंकि वो काम शुरू करने से पहले ही ढिंढोरा पीट देते हैं। वो उन चीजों की तारीफ चाहते हैं जो उन्होंने अभी पाई ही नहीं। अगर सम्मान पाना चाहते हो, तो शांत रहकर काम करने की कला सीखो। अपनी मेहनत का शोर इतना बुलंद रखो कि तुम्हें अपनी आवाज उठाने की जरूरत न पड़े। अगर बात सही लगी तो डबल टैप करें।",
            "single_es": "Marco Aurelio escribió: 'No pierdas más tiempo discutiendo lo que debe ser un hombre bueno. Sé uno.' La mayoría fracasa porque anuncia sus metas antes de dar el primer paso. Buscan la dopamina fácil del elogio por cosas que no han logrado. Si quieres respeto, domina el silencio. Que tu disciplina hable tan alto que nunca tengas que levantar la voz. Dale dos toques a la pantalla si necesitabas recordar esto hoy.",
            "parts": [
                {
                    "part": 1,
                    "text": "Marcus Aurelius wrote: Waste no more time arguing what a good man should be. Be one. The single biggest reason ninety-nine percent of people fail to hit their goals is because they brag about their plans before doing the work. They chase the cheap dopamine of validation from people who do not even matter. Follow for Part 2 on the Spartan rule that changes everything.",
                    "text_hi": "मार्कस ऑरेलियस ने कहा था: एक अच्छे इंसान बनने पर बहस मत करो, बस बनो। लोग असफल इसलिए होते हैं क्योंकि वो काम करने से पहले ही डींगें हांकने लगते हैं। पार्ट २ के लिए अभी फॉलो करें उस नियम को जानने के लिए जो सब बदल देगा।",
                    "text_es": "Marco Aurelio dijo: No pierdas tiempo discutiendo qué es ser un hombre bueno. Sé uno. El 99% fracasa porque presume de sus planes antes de actuar. Síguenos para la Parte 2 sobre la regla que lo cambia todo."
                },
                {
                    "part": 2,
                    "text": "In ancient Sparta, if a man spoke empty words without backing them with actions, he was publicly shamed. True strength is quiet. Let your results produce the noise while your habits remain completely silent. Start waking up earlier, training harder, and cutting out toxic distractions. Save this reel to rewatch when you feel like quitting.",
                    "text_hi": "प्राचीन स्पार्टा में खोखले शब्दों का कोई मोल नहीं था। असली ताकत खामोश होती है। अपने नतीजों को शोर मचाने दो जबकि तुम्हारी आदतें शांत रहें। सुबह जल्दी उठो, मेहनत करो और रुकावटों को मिटा दो। इस रील को सेव कर लो।",
                    "text_es": "En la antigua Esparta, las palabras vacías eran castigadas. La verdadera fuerza es silenciosa. Deja que tus resultados hagan el ruido mientras tus hábitos permanecen en silencio. Entrena duro y elimina distracciones. Guarda este reel para cuando quieras rendirte."
                }
            ]
        }
    ]
}

def get_language_name(code: str) -> str:
    for lang in LANGUAGES:
        if lang["code"] == code:
            return lang["name"]
    return "English"

def generate_script_prompt(niche: str, topic: Optional[str], is_multipart: bool, parts_count: int, language: str = "en") -> str:
    niche_info = NICHES.get(niche, NICHES["true_crime"])
    lang_name = get_language_name(language)
    style_guide = f"Niche: {niche_info['name']}. Tone: {niche_info['tone']}."
    
    lang_instruction = f"CRITICAL REQUIREMENT: The entire output, including title, caption, hashtags, and spoken script MUST BE FULLY WRITTEN IN {lang_name.upper()}."

    if not is_multipart:
        return f"""You are a master viral TikTok and Instagram Reels scriptwriter.
{style_guide}
{lang_instruction}
Topic: {topic or 'A shocking, highly engaging story or mystery in this niche'}

Write a complete 40-50 second viral Reel script (110-140 words).
Structure:
- Hook (first 3 seconds): Irresistible curiosity gap, shocking statement or question.
- Narrative: Fast-paced, concise storytelling, high emotional tension.
- Climax / Twist: Sudden turn or shocking revelation.
- Call to Action: Engaging question asking the viewer to comment and follow.

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Punchy Title in {lang_name}",
  "caption": "Instagram post caption with hook in {lang_name}",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "script": "The spoken words only in {lang_name}. No stage directions, no narrator labels."
}}"""
    else:
        return f"""You are a master viral episodic story creator for Instagram Reels and TikTok.
{style_guide}
{lang_instruction}
Topic: {topic or 'A multi-part gripping mystery or high-tension narrative'}
Create a {parts_count}-part series. Each part must be approximately 40-45 seconds (100-130 spoken words).

Rules:
- Part 1 must end on an intense cliffhanger asking viewers to follow for Part 2.
- Subsequent parts must maintain the tension and end with the next cliffhanger.
- The final part must deliver the shocking climax and call to action.

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Series Title in {lang_name}",
  "caption": "Instagram series caption in {lang_name}",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "parts": [
    {{
      "part": 1,
      "hook": "Hook for part 1 in {lang_name}",
      "script": "Spoken words for part 1 only in {lang_name}. End with cliffhanger to follow for Part 2."
    }},
    {{
      "part": 2,
      "hook": "Hook for part 2 in {lang_name}",
      "script": "Spoken words for part 2 only in {lang_name}."
    }}
  ]
}}"""

def call_ollama(prompt: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        res = requests.post(url, json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            return json.loads(data.get("response", "{}"))
    except Exception as e:
        print(f"[Ollama Error] {e}")
    return None

def call_gemini(prompt: str) -> Optional[Dict[str, Any]]:
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
    except Exception as e:
        print(f"[Gemini Error] {e}")
    return None

def call_openai(prompt: str) -> Optional[Dict[str, Any]]:
    if not OPENAI_API_KEY:
        return None
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a viral social media scriptwriter. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            return json.loads(data["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"[OpenAI Error] {e}")
    return None

def generate_script(
    niche: str,
    topic: Optional[str] = None,
    is_multipart: bool = False,
    parts_count: int = 2,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generates a viral reel script based on the chosen niche, topic, format, and language.
    Tries configured LLMs; falls back smoothly to built-in multi-lingual viral stories.
    """
    niche_key = niche if niche in NICHES else "true_crime"
    niche_info = NICHES[niche_key]
    lang = language or "en"
    
    # Try External LLMs if configured
    prompt = generate_script_prompt(niche_key, topic, is_multipart, parts_count, lang)
    result = None

    if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
        result = call_gemini(prompt)
    elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        result = call_openai(prompt)
    elif LLM_PROVIDER == "ollama":
        result = call_ollama(prompt)

    if result:
        result["niche"] = niche_key
        result["is_multipart"] = is_multipart
        result["language"] = lang
        return result

    # Fallback to Builtin Multi-lingual Curated Stories
    pool = BUILTIN_STORIES.get(niche_key, BUILTIN_STORIES.get("true_crime", []))
    if not pool:
        pool = BUILTIN_STORIES["true_crime"]
        
    selected_story = random.choice(pool)

    # Pick text matching language
    title_key = f"title_{lang}" if f"title_{lang}" in selected_story else "title"
    single_key = f"single_{lang}" if f"single_{lang}" in selected_story else "single"
    
    story_title = selected_story.get(title_key, selected_story["title"])
    story_script = selected_story.get(single_key, selected_story["single"])

    if not is_multipart:
        return {
            "title": story_title,
            "niche": niche_key,
            "language": lang,
            "is_multipart": False,
            "caption": f"😱 {story_title}",
            "hashtags": niche_info["hashtags"],
            "script": story_script
        }
    else:
        parts_data = selected_story["parts"]
        rendered_parts = []
        for p in parts_data[:parts_count]:
            text_k = f"text_{lang}" if f"text_{lang}" in p else "text"
            rendered_parts.append({
                "part": p["part"],
                "hook": f"Part {p['part']}",
                "script": p.get(text_k, p["text"])
            })
        return {
            "title": story_title,
            "niche": niche_key,
            "language": lang,
            "is_multipart": True,
            "caption": f"Part 1: {story_title}",
            "hashtags": niche_info["hashtags"],
            "parts": rendered_parts
        }
