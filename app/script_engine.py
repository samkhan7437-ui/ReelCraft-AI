import json
import random
import os
import requests
from typing import Dict, Any, List, Optional
from app.config import (
    NICHES, LANGUAGES, LLM_PROVIDER, OLLAMA_HOST, OLLAMA_MODEL, GEMINI_API_KEY, OPENAI_API_KEY
)

# Rotation tracker so consecutive generations for a niche never return the same story
_LAST_STORY_INDICES: Dict[str, int] = {}

# Comprehensive multi-lingual story library for all 7 niches (English, Hindi, Spanish)
BUILTIN_STORIES = {
    "true_crime": [
        {
            "title": "The Knock at 8,000 Feet",
            "title_hi": "समुद्र के 8,000 फीट नीचे रहस्यमयी दस्तक",
            "title_es": "El Golpe a 8,000 Pies de Profundidad",
            "single": "In 1974, deep-sea diver Robert Shaw was stationed inside an underwater capsule 8,000 feet beneath the Pacific. At 2:14 AM, the communications went dead. Total silence. Then, from the outside of the titanium hull, he heard three deliberate, rhythmic knocks. Shaw checked the sonar: nothing was within miles. When his capsule was finally brought to the surface, engineers found three deep indentations on the steel hatch... perfectly matching the shape of a human hand. Shaw resigned the next morning and never looked at the ocean again. What do you think knocked on that door? Follow for more mysteries.",
            "single_hi": "१९७४ में गहरे समुद्र के गोताखोर रॉबर्ट शॉ प्रशांत महासागर में आठ हजार फीट नीचे एक कैप्सूल में बंद थे। रात के दो बजकर चौदह मिनट पर उनका संपर्क टूट गया। सन्नाटा छा गया। तभी टाइटेनियम की दीवार के बाहर से उन्हें तीन लगातार खटखटाने की आवाजें सुनाई दीं। जैसे कोई लोहे पर उंगलियों से दस्तक दे रहा हो। सोनार पर पचास मील तक कोई जीव नहीं था। जब कैप्सूल ऊपर लाया गया, तो स्टील के गेट पर इंसान की उंगलियों के तीन गहरे निशान मिले। रॉबर्ट ने अगली सुबह नौकरी छोड़ दी और फिर कभी समुद्र की तरफ नहीं देखा। आपको क्या लगता है वह क्या था? फॉलो करें ऐसी ही अनसुलझी कहानियों के लिए।",
            "single_es": "En 1974, el buzo Robert Shaw estaba dentro de una cápsula a ocho mil pies bajo el Pacífico. A las 2:14 AM, las comunicaciones se cortaron por completo. Silencio total. De pronto, desde el exterior del casco de titanio, escuchó tres golpes lentos y deliberados. El sonar no detectó nada a kilómetros. Cuando subieron la cápsula, encontraron tres marcas profundas en el acero coincidentes con dedos humanos. Shaw renunció al día siguiente. ¿Qué crees que golpeó esa puerta? Síguenos.",
            "parts": [
                {
                    "part": 1,
                    "text": "In 1974, deep-sea diver Robert Shaw was stationed inside a pressurized research capsule eight thousand feet beneath the Pacific Ocean. At 2:14 AM, communications went dead. Complete darkness. Then, from the outside of the titanium hull, he heard three deliberate, heavy knocks. He checked the radar, but there was nothing within fifty miles. Follow for Part 2 to see what was waiting outside.",
                    "text_hi": "१९७४ में गोताखोर रॉबर्ट शॉ प्रशांत महासागर में आठ हजार फीट नीचे एक रिसर्च कैप्सूल में अकेले थे। रात के २:१४ बजे सभी संचार बंद हो गए। घना अंधेरा। तभी बाहर से तीन भारी दस्तकें सुनाई दीं। रडार पर पचास मील तक कुछ नहीं था। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 1974, el buzo Robert Shaw estaba a ocho mil pies bajo el Pacífico. A las 2:14 AM, las comunicaciones se cortaron. De repente, escuchó tres golpes en el casco exterior. El radar no marcaba nada a 50 millas. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "When Robert turned on the external floodlights outside the submarine hatch, pressed directly against the thick glass was a pale, humanoid shape staring back with no eyes. And right as the alarms screamed, it vanished into the abyss. Engineers later found human-shaped finger dents in the steel. Follow for more mysteries.",
                    "text_hi": "जब रॉबर्ट ने बाहर की फ्लडलाइट जलाई, तो कांच के ठीक सामने एक बिना आंखों वाली पीली आकृति घूर रही थी। अलार्म बजते ही वह काली गहराइयों में गायब हो गई। सतह पर आने पर इंजीनियरों को स्टील पर उंगलियों के निशान मिले। कमेंट करें अपनी राय।",
                    "text_es": "Al encender los reflectores, una figura pálida humanoide sin ojos estaba pegada al cristal. Desapareció en el abismo al sonar las alarmas. Hallaron marcas de dedos en el acero. Comenta abajo."
                }
            ]
        },
        {
            "title": "The Vanishing of Flight 19",
            "title_hi": "फ्लाइट 19 का रहस्यमयी गायब होना",
            "title_es": "La Desaparición del Vuelo 19",
            "single": "On December 5, 1945, five US Navy bombers took off from Florida on a routine training mission. Two hours later, the flight leader's voice crackled over the radio: 'Both my compasses are dead. The ocean looks strange. We don't know where west is.' Then static. A giant rescue plane carrying 13 crew members was immediately sent to find them. Within 20 minutes, that rescue plane vanished from radar too. Neither wreckage, nor bodies, nor a single drop of fuel was ever recovered. To this day, the US Navy lists the incident as 'Cause Unknown'. What really happened in the Bermuda Triangle? Drop your theory in the comments.",
            "single_hi": "५ दिसंबर १९४५ को अमेरिकी नौसेना के पांच बमवर्षक विमानों ने फ्लोरिडा से उड़ान भरी। दो घंटे बाद रेडियो पर पायलट की घबराई आवाज गूंजी: 'हमारे दोनों कंपास खराब हो चुके हैं। समुद्र का रंग अजीब लग रहा है। हमें नहीं पता पश्चिम दिशा कहां है।' इसके बाद सिर्फ सन्नाटा। उन्हें ढूंढने के लिए १३ क्रू मेंबर्स के साथ एक बड़ा रेस्क्यू विमान भेजा गया। हैरान करने वाली बात यह थी कि २० मिनट के अंदर वह रेस्क्यू प्लेन भी हमेशा के लिए गायब हो गया। आज तक न कोई मलबा मिला, न कोई शव। आपको क्या लगता है, बरमूडा ट्रायंगल में उस दिन क्या हुआ था? कमेंट में बताएं।",
            "single_es": "El 5 de diciembre de 1945, cinco bombarderos de la Marina despegaron de Florida. Dos horas después, el líder dijo por radio: 'Las brújulas no funcionan. El océano se ve extraño.' Luego, silencio total. Un hidroavión de rescate con 13 tripulantes despegó de inmediato y a los 20 minutos también desapareció sin dejar rastro. ¿Qué crees que ocurrió en el Triángulo de las Bermudas?",
            "parts": [
                {
                    "part": 1,
                    "text": "In 1945, five military bombers entered the Bermuda Triangle on a clear sunny day. At 3:40 PM, the squadron leader reported: 'We cannot see land. Everything is wrong, even the ocean looks alien.' Follow for Part 2 to hear the final recording.",
                    "text_hi": "१९४५ में पांच बमवर्षक विमानों ने साफ मौसम में उड़ान भरी। दोपहर ३:४० बजे कमांडर ने कहा: 'हमें जमीन नहीं दिख रही, सब कुछ गलत हो रहा है, समुद्र भी अजीब लग रहा है।' पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 1945, cinco bombarderos volaban sobre el Triángulo de las Bermudas. A las 3:40 PM, el comandante reportó que nada parecía normal y que el océano se veía alienígena. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Moments after the flight vanished, a giant rescue plane sent to save them also disappeared in under twenty minutes. Zero debris was ever found across thousands of square miles. The official Navy verdict was: 'Vanished as if they flew to Mars.' Follow for more unsolved cases.",
                    "text_hi": "विमानों के गायब होने के कुछ मिनट बाद भेजा गया रेस्क्यू प्लेन भी बीस मिनट में गायब हो गया। हजारों मील तक कभी कोई मलबा नहीं मिला। नेवी का आधिकारिक बयान था: जैसे वो सीधे मंगल ग्रह पर चले गए हों। फॉलो करें ऐसी ही कहानियों के लिए।",
                    "text_es": "El avión de rescate enviado también desapareció en 20 minutos. Jamás se halló un solo rastro. La marina dijo que fue como si hubieran volado a Marte. Síguenos para más."
                }
            ]
        },
        {
            "title": "The Locked Room of Paris Attic",
            "title_hi": "पेरिस के अटारी का ७० साल पुराना बंद कमरा",
            "title_es": "La Habitación Oculta del Ático de París",
            "single": "In 1942, Madame de Florian fled her luxurious Parisian apartment ahead of Nazi soldiers. She locked the heavy oak door and kept paying rent for seventy years until she died at age 91 without ever returning. When her heirs finally unlocked the door in 2010, they entered a time capsule untouched for seven decades. Dust covered crystal chandeliers, silk dresses, and vintage perfumes. But hidden behind a false wall, they found a lost painting of a beautiful woman in pink silk, signed by Italian master Giovanni Boldini. It sold at auction for 3 million dollars. But why did she abandon it and never speak a word? Follow for true historical mysteries.",
            "single_hi": "१९४२ में द्वितीय विश्व युद्ध के दौरान मैडम डी फ्लोरियन अपने पेरिस के आलीशान अपार्टमेंट को छोड़कर भाग गईं। उन्होंने दरवाजे पर भारी ताला लगाया और अगले ७० सालों तक हर महीने किराया भेजती रहीं, लेकिन कभी वापस नहीं लौटीं। २०१० में जब ९१ वर्ष की आयु में उनकी मौत हुई, तब उनके वारिसों ने ताला तोड़ा। अंदर ७० साल पुराना समय मानो जम चुका था। धूल से सने झूमर, पुराने परफ्यूम और सिल्क के गाउन। लेकिन एक गुप्त दीवार के पीछे उन्हें गुलाबी सिल्क वाली एक महिला की दुर्लभ पेंटिंग मिली, जो नीलामी में ३० लाख डॉलर में बिकी। आखिर उन्होंने यह घर क्यों छिपाकर रखा? फॉलो करें ऐसे ही रहस्यों के लिए।",
            "single_es": "En 1942, una mujer abandonó su apartamento en París huyendo de la guerra. Cerró con llave y pagó el alquiler durante 70 años sin volver jamás. Al abrirlo en 2010, hallaron una cápsula del tiempo intacta y una pintura oculta valorada en 3 millones de dólares. ¿Por qué guardó el secreto toda su vida? Síguenos.",
            "parts": [
                {
                    "part": 1,
                    "text": "In 1942, a Parisian socialite locked her luxury apartment and never returned, yet paid rent every month for seventy straight years. When her descendants finally broke the lock in 2010, what was inside shocked the world. Follow for Part 2.",
                    "text_hi": "१९४२ में एक पेरिस की महिला ने अपने घर पर ताला लगाया और ७० साल तक किराया देती रही, पर कभी वापस नहीं आई। २०१० में जब ताला टूटा, तो अंदर जो मिला उसने दुनिया को चौंका दिया। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 1942, una mujer cerró su apartamento en París y pagó la renta durante 70 años sin regresar. En 2010 abrieron la puerta y lo que hallaron asombró a todos. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Inside was an untouched 1940s dream: crystal glasses, stuffed ostriches, and a hidden masterpiece painting worth over $3,000,000. She took the secret of why she left it to her grave. Follow for more hidden history.",
                    "text_hi": "अंदर १९४० का अछूता जमाना था: दुर्लभ सामान और गुप्त दीवार के पीछे ३० लाख डॉलर की अनमोल पेंटिंग। वो औरत यह राज अपने साथ कब्र में ले गई। फॉलो करें ऐसे ही रहस्यों के लिए।",
                    "text_es": "Adentro había un tesoro intacto de 1942 y una obra de arte oculta de 3 millones de dólares. Murió sin revelar su secreto. Síguenos para más misterios."
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
            "single_es": "Si alguna vez te despiertas a las 3:00 AM y escuchas a alguien silbando frente a tu puerta, no abras los ojos. Un excursionista grabó 14 minutos de un silbido rodeando su tienda. Al día siguiente no había huellas en el suelo, solo marcas de garras en las ramas a 6 metros de altura. ¿Has oído algo inexplicable por la noche?",
            "parts": [
                {
                    "part": 1,
                    "text": "If you wake up at 3:00 AM and hear whistling outside your door, do not make a sound. In 2021, a solo hiker recorded something so disturbing park rangers refused to release the full audio. Follow for Part 2.",
                    "text_hi": "अगर रात के तीन बजे आपको बाहर सीटी सुनाई दे, तो एक शब्द भी मत बोलना। २०२१ में पहाड़ों में एक हाइकर ने कुछ ऐसा रिकॉर्ड किया जिसे अधिकारियों ने छिपा लिया। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Si te despiertas a las 3:00 AM y escuchas un silbido afuera, quédate inmóvil. Un excursionista grabó un audio aterrador que guardabosques no quisieron publicar. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "When morning broke, rangers found zero footprints on the ground. Instead, twenty feet up in the pine trees, giant claw marks tore the bark clean off. If you hear the whistle, never whistle back. Follow for more true horror.",
                    "text_hi": "सुबह जमीन पर पैरों के निशान नहीं थे, बल्कि बीस फीट ऊंचे पेड़ों पर विशाल पंजों के खुरचने के निशान थे। अगर कभी सीटी सुनाई दे, तो कभी जवाब मत देना। फॉलो करें हॉरर कहानियों के लिए।",
                    "text_es": "Al amanecer no había pisadas en la tierra, sino garras enormes a 6 metros de altura en los pinos. Nunca silbes de vuelta. Síguenos para más horror."
                }
            ]
        },
        {
            "title": "The Lagging Hotel Mirror",
            "title_hi": "होटल के शीशे का डरावना सच",
            "title_es": "El Espejo con Retraso del Hotel",
            "single": "In 2018, a traveler checked into an old Victorian hotel in Savannah. While brushing his teeth at midnight, he dropped his toothbrush. When he stood back up, his reflection was still looking down at the sink. He froze. Two seconds later, the reflection slowly lifted its head, smiled directly at him, and blinked. He ran out of the room leaving all his luggage behind. Hotel records later revealed that in 1923, an antique mirror was installed in Room 312 after a guest died inside the bathroom under mysterious circumstances. Check your mirror tonight... does your reflection always move with you?",
            "single_hi": "२०१८ में एक यात्री ने एक पुराने ऐतिहासिक होटल के कमरा नंबर ३१२ में चेक-इन किया। आधी रात को जब वह वॉशबेसिन के सामने ब्रश कर रहा था, उसका ब्रश नीचे गिर गया। जब वह दोबारा सीधा हुआ, तो शीशे में उसकी परछाई अभी भी नीचे की तरफ ही देख रही थी। उसके रोंगटे खड़े हो गए। दो सेकंड बाद शीशे वाली परछाई ने धीरे से अपना सिर उठाया, उसकी आंखों में देखा और एक अजीब मुस्कान दी। वह अपना सारा सामान छोड़कर होटल से भाग निकला। पुराने रिकॉर्ड बताते हैं कि १९२३ में उस बाथरूम में एक रहस्यमयी मौत हुई थी। आज रात अपना आईना ध्यान से देखना... क्या आपकी परछाई बिल्कुल आपके साथ चलती है?",
            "single_es": "En 2018, un huésped en un hotel antiguo se agachó a recoger su cepillo de dientes frente al espejo. Al levantarse, su reflejo seguía mirando hacia abajo. Dos segundos después, el reflejo levantó la cabeza lentamente y le sonrió. Salió corriendo del hotel. Revisa tu espejo esta noche... ¿tu reflejo se mueve siempre contigo?",
            "parts": [
                {
                    "part": 1,
                    "text": "In a Savannah hotel room, a man looked up at the bathroom mirror and noticed something terrifying: his reflection wasn't moving when he moved. It was watching him. Follow for Part 2.",
                    "text_hi": "एक पुराने होटल के बाथरूम में जब उस आदमी ने शीशे में देखा, तो उसे एहसास हुआ कि उसकी परछाई उसके साथ नहीं हिल रही थी। वो उसे घूर रही थी। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En un hotel antiguo, un hombre miró al espejo y notó algo espeluznante: su reflejo no se movía cuando él lo hacía. Lo estaba observando. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Two seconds later, the reflection lifted its head on its own and smiled. The man bolted into the hallway in terror. The room has been bolted shut ever since. Follow for more spine-chilling stories.",
                    "text_hi": "दो सेकंड बाद परछाई ने खुद सिर उठाया और मुस्कुरा दी। वह चीखता हुआ कमरे से भाग निकला। उस कमरे को आज भी बंद रखा गया है। फॉलो करें डरावनी सच्ची घटनाओं के लिए।",
                    "text_es": "El reflejo sonrió por cuenta propia. El hombre huyó aterrorizado dejando todo su equipaje. La habitación permanece sellada. Síguenos para más horror."
                }
            ]
        }
    ],

    "reddit_stories": [
        {
            "title": "My Boss Stole My $2 Million Deal",
            "title_hi": "बॉस ने चुराई मेरी करोड़ों की डील",
            "title_es": "Mi Jefe me Robó un Negocio Millonario",
            "single": "I spent six months working 80-hour weeks closing a $2.4 million client deal for our tech startup. The day of the signing, my manager removed my name from the pitch deck and told the CEO he did it all himself. He got a $100,000 bonus and a promotion to VP. I didn't yell. I didn't complain. Instead, I waited until annual audit week. When the client called asking why key security protocols were missing, I forwarded the original emails with my manager's signature rejecting those exact protocols to save budget. The client cancelled the contract on the spot, citing managerial incompetence. My boss was fired by 2 PM and his bonus was revoked. Pro revenge at its finest. Follow for daily drama.",
            "single_hi": "मैंने लगातार छह महीने दिन-रात एक करके २ करोड़ रुपये की एक बड़ी क्लाइंट डील पक्की की। लेकिन साइन होने वाले दिन मेरे मैनेजर ने मेरा नाम हटा दिया और मालिक से कहा कि यह पूरी मेहनत उसकी है। उसे प्रमोशन और भारी बोनस मिला। मैं चिल्लाया नहीं, न ही मैंने कोई शिकायत की। मैंने सही वक्त का इंतजार किया। जब सालाना ऑडिट में क्लाइंट ने पूछा कि सिक्योरिटी फीचर्स क्यों छूटे हैं, मैंने मैनेजर के वो पुराने ईमेल फॉरवर्ड कर दिए जिसमें उसने बजट बचाने के लिए फीचर्स हटाने का आदेश दिया था। क्लाइंट ने डील तुरंत कैंसिल कर दी। दोपहर दो बजे तक मेरा बॉस नौकरी से निकाल दिया गया और उसका बोनस भी जब्त हो गया। बदला हमेशा ठंडे दिमाग से लिया जाता है। फॉलो करें ऐसी ही कहानियों के लिए।",
            "single_es": "Pasé seis meses cerrando un contrato de 2.4 millones para la empresa. Mi jefe borró mi nombre y le dijo al director que lo hizo solo, llevándose un ascenso y bono enorme. No me quejé. Esperé a la auditoría y reenvié los correos donde él cancelaba las medidas de seguridad para ahorrar dinero. El cliente canceló el contrato y despidieron a mi jefe antes de las dos de la tarde. Síguenos para más historias.",
            "parts": [
                {
                    "part": 1,
                    "text": "My manager stole credit for my $2.4 million client deal and got promoted to VP while taking my bonus. But he forgot I had the original paper trail. Follow for Part 2 to see the revenge.",
                    "text_hi": "मेरे मैनेजर ने मेरी २ करोड़ की डील का क्रेडिट चुरा लिया और प्रमोशन ले लिया। लेकिन वो भूल गया कि सारे ओरिजिनल ईमेल मेरे पास थे। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Mi jefe se robó mi contrato de 2.4 millones y se llevó el ascenso. Pero olvidó que yo tenía todos los correos guardados. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "During the audit, I forwarded his emails showing he cut client security to pocket budget. The client pulled out, and he was marched out of the building by security that afternoon. Revenge is sweet. Follow for more.",
                    "text_hi": "ऑडिट के दौरान मैंने उसके पुराने ईमेल सीधे बोर्ड को भेज दिए। क्लाइंट ने डील रद्द कर दी और उसी दोपहर गार्ड्स ने उसे ऑफिस से बाहर फेंक दिया। फॉलो करें ऐसी कहानियों के लिए।",
                    "text_es": "Reenvié sus correos a la directiva y la seguridad del edificio lo sacó escoltado esa misma tarde. Venganza perfecta. Síguenos para más."
                }
            ]
        },
        {
            "title": "The Neighbor Who Stole My Packages",
            "title_hi": "पार्सल चोर पड़ोसी को मिला करारा सबक",
            "title_es": "El Vecino que Robaba mis Paquetes",
            "single": "For three months, every Amazon package delivered to my front porch vanished within an hour. The police said without proof, they couldn't do anything. So I bought a high-definition doorbell camera and engineered the ultimate surprise. I packed a fresh Amazon box with a pressurized glitter bomb and ultra-stinky fart spray, rigged to trigger when opened. Twenty minutes after delivery, my neighbor across the street walked over, snatched the box, and ran inside. Ten seconds later, I heard a scream so loud car alarms went off. When police arrived, he opened the door completely covered in hot pink micro-glitter and smelling like raw sewage. He was arrested on the spot and had to explain the pink glitter to his employer. Follow for satisfying revenge stories.",
            "single_hi": "पिछले तीन महीनों से मेरे दरवाजे पर आने वाला हर पार्सल एक घंटे के अंदर चोरी हो जाता था। पुलिस ने कहा कि सबूत के बिना वो कुछ नहीं कर सकते। तो मैंने एक सीक्रेट डोरबेल कैमरा लगाया और एक शानदार प्लान बनाया। मैंने एक अमेज़न के खाली डिब्बे में ग्लिटर बॉम्ब और दुनिया का सबसे बदबूदार स्प्रे फिट किया, जो डिब्बा खोलते ही फूटने वाला था। डिलीवरी के बीस मिनट बाद सामने वाला पड़ोसी आया, डिब्बा चुराया और अपने घर भाग गया। दस सेकंड बाद उसके घर से ऐसी भयानक चीख आई कि आसपास की गाड़ियां बजने लगीं। जब पुलिस पहुंची, तो पड़ोसी सिर से पैर तक चमकीले पिंक ग्लिटर से ढका हुआ था और बदबू से बेहाल था। उसे रंगे हाथों गिरफ्तार कर लिया गया। फॉलो करें मजेदार कहानियों के लिए।",
            "single_es": "Durante tres meses, mi vecino se robaba todos mis paquetes de la puerta. Preparé una caja trampa con bomba de purpurina rosa y spray fétido que explotaba al abrirla. Se la robó y a los diez segundos se escuchó un grito ensordecedor. Cuando llegó la policía, abrió la puerta completamente cubierto de brillo rosa brillante. Quedó arrestado de inmediato. Síguenos para más.",
            "parts": [
                {
                    "part": 1,
                    "text": "My neighbor kept stealing all my delivered packages. So I prepared a fake Amazon box rigged with a pressurized glitter bomb and motion-activated fart spray. Follow for Part 2 to see the aftermath.",
                    "text_hi": "मेरा पड़ोसी मेरे सारे पार्सल चुरा लेता था। तो मैंने अमेज़न के बॉक्स में ग्लिटर बॉम्ब और बदबूदार स्प्रे का ट्रैप लगाया। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Mi vecino no paraba de robar mis paquetes. Así que preparé una caja trampa con purpurina a presión y spray fétido. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "He stole it, opened it in his living room, and was completely coated in permanent hot pink glitter and sewage smell when the police arrested him. Drop a like if he deserved it!",
                    "text_hi": "उसने बॉक्स अपने लिविंग रूम में खोला और पूरे शरीर पर चिपचिपा पिंक ग्लिटर लग गया। पुलिस ने उसे रंगे हाथों पकड़ा। अगर सबक सही लगा तो लाइक करें!",
                    "text_es": "Abrió la caja en su sala y quedó bañado en brillantina rosa y peste inmunda cuando la policía se lo llevó detenido. Dale like si se lo merecía."
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
            "single_es": "Marco Aurelio escribió: 'No pierdas más tiempo discutiendo lo que debe ser un hombre bueno. Sé uno.' La mayoría fracasa porque anuncia sus metas antes de dar el primer paso. Si quieres respeto, domina el silencio. Que tu disciplina hable tan alto que nunca tengas que levantar la voz. Síguenos.",
            "parts": [
                {
                    "part": 1,
                    "text": "Marcus Aurelius wrote: Waste no more time arguing what a good man should be. Be one. The single biggest reason ninety-nine percent of people fail to hit their goals is because they brag about their plans before doing the work. Follow for Part 2 on the Spartan rule.",
                    "text_hi": "मार्कस ऑरेलियस ने कहा था: एक अच्छे इंसान बनने पर बहस मत करो, बस बनो। लोग असफल इसलिए होते हैं क्योंकि वो काम करने से पहले ही डींगें हांकने लगते हैं। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Marco Aurelio dijo: No pierdas tiempo discutiendo qué es ser un hombre bueno. Sé uno. El 99% fracasa porque presume sus planes antes de actuar. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "In ancient Sparta, empty words were publicly shamed. True strength is quiet. Let your results produce the noise while your habits remain completely silent. Start waking up earlier and working harder. Save this reel.",
                    "text_hi": "प्राचीन स्पार्टा में खोखले शब्दों का कोई मोल नहीं था। असली ताकत खामोश होती है। अपने नतीजों को शोर मचाने दो जबकि तुम्हारी आदतें शांत रहें। सुबह जल्दी उठो, मेहनत करो। इस रील को सेव कर लो।",
                    "text_es": "En la antigua Esparta las palabras vacías eran castigadas. La verdadera fuerza es silenciosa. Que tus resultados hagan el ruido. Guarda este reel."
                }
            ]
        },
        {
            "title": "The 48-Hour Emotional Rule",
            "title_hi": "गुस्से को काबू करने का ४८ घंटे का नियम",
            "title_es": "La Regla de las 48 Horas de Séneca",
            "single": "Seneca, the billionaire Roman philosopher, once said: 'Delay is the greatest remedy for anger.' When someone insults you, disrespects you, or betrays you, your animal brain wants to react immediately. But reacting in anger gives your power away to the enemy. High-value individuals practice the 48-hour rule. When emotionally triggered, they say nothing, send no messages, and make zero decisions for two full days. By hour 48, the emotional cloud clears, and what is left is cold, calculated strategy. Power is not about who yells the loudest; it's about who stays calm when everyone else loses their mind. Save this rule for when you need it.",
            "single_hi": "महान दार्शनिक सेनेका ने कहा था: 'गुस्से की सबसे बड़ी दवा है थोड़ा ठहर जाना।' जब कोई आपका अपमान करता है या आपको धोखा देता है, तो आपका मन तुरंत पलटवार करना चाहता है। लेकिन गुस्से में जवाब देने का मतलब है कि आपने अपनी ताकत उस इंसान के हाथों में सौंप दी। ताकतवर लोग ४८ घंटे के नियम का पालन करते हैं। जब भी कोई उन्हें भड़काता है, वे दो दिन तक न कोई जवाब देते हैं, न कोई फैसला लेते हैं। ४८ घंटे बाद जब दिमाग शांत होता है, तब वे ऐसा कदम उठाते हैं जो सामने वाले को हमेशा के लिए चुप करा देता है। ताकतवर वो नहीं जो सबसे तेज चिल्लाए, बल्कि वो है जो हर तूफान में शांत रहे। इस रील को सेव कर लें।",
            "single_es": "Séneca dijo: 'La demora es el mejor remedio para la ira.' Cuando alguien te ofende, reaccionar de inmediato es entregarle tu poder. Los sabios aplican la regla de las 48 horas: cuando se sienten enojados, no envían mensajes ni toman decisiones durante dos días. Cuando pasa la emoción, queda la estrategia fría. Guarda este video.",
            "parts": [
                {
                    "part": 1,
                    "text": "Seneca said delay is the greatest remedy for anger. The moment someone disrespects you, if you react instantly, they control you. Follow for Part 2 on the 48-hour rule.",
                    "text_hi": "सेनेका ने कहा था कि गुस्से की सबसे बड़ी दवा देरी है। अगर किसी के अपमान पर आप तुरंत भड़कते हैं, तो वो आपको नियंत्रित कर रहा है। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Séneca afirmó que la demora es el mejor remedio para la ira. Si reaccionas al instante ante una falta de respeto, le das el control. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Wait forty-eight hours before saying a single word. When the emotion fades, your response will be cold, precise, and undefeated. Master your temper, master your life. Follow for daily stoic wisdom.",
                    "text_hi": "जवाब देने से पहले ४८ घंटे रुकें। जब गुस्सा शांत होगा, आपका जवाब इतना सटीक होगा कि कोई टिक नहीं पाएगा। अपने गुस्से पर काबू पाएं, जिंदगी जीतें। फॉलो करें।",
                    "text_es": "Espera 48 horas antes de decir una palabra. Tu respuesta será fría, precisa e imparable. Domina tus emociones, domina tu destino. Síguenos."
                }
            ]
        }
    ],

    "wild_facts": [
        {
            "title": "The Immortal Creature in Our Oceans",
            "title_hi": "समुद्र का अमर जीव: जो कभी नहीं मरता",
            "title_es": "La Criatura Inmortal de Nuestros Océanos",
            "single": "Did you know there is a creature on Earth that is biologically immortal? The Turritopsis dohrnii jellyfish can reset its cellular age back to a baby polyp whenever it gets sick, injured, or old. Imagine being 80 years old and simply deciding to turn your body back into a six-year-old child whenever you want. Scientists have studied these creatures for decades, trying to unlock the genetic code that reverses cellular aging. In theory, a single jellyfish could live forever unless eaten by a predator. Could this tiny sea creature hold the secret to human immortality? Share your thoughts below.",
            "single_hi": "क्या आप जानते हैं कि हमारी पृथ्वी पर एक ऐसा जीव मौजूद है जो कभी बूढ़ा होकर नहीं मरता? टुरिटोप्सिस डोहर्नी नाम की यह जेलीफ़िश जब भी बीमार या बूढ़ी होती है, तो यह अपनी कोशिकाओं को रिवर्स करके वापस एक नन्हे बच्चे के रूप में बदल लेती है। यह बिल्कुल वैसा है जैसे कोई ८० साल का इंसान बूढ़ा होने पर दोबारा ६ साल का बच्चा बन जाए। वैज्ञानिक दशकों से इसके डीएनए पर रिसर्च कर रहे हैं ताकि इंसानों में बढ़ती उम्र को रोका जा सके। जब तक कोई दूसरा जीव इसे खा न जाए, यह अमर है। क्या यह छोटा सा जीव इंसानों को हमेशा जवान रखने का राज़ जानता है? कमेंट में बताएं।",
            "single_es": "¿Sabías que existe un ser biológicamente inmortal en la Tierra? La medusa Turritopsis dohrnii puede revertir sus células a su etapa de pólipo bebé cuando enferma o envejece. Podría vivir eternamente a menos que un depredador se la coma. ¿Podría tener la clave de la longevidad humana? Comenta abajo.",
            "parts": [
                {
                    "part": 1,
                    "text": "There is a creature swimming in our oceans right now that is biologically immortal. Whenever it gets old or injured, it reverses its age completely. Follow for Part 2 to learn how.",
                    "text_hi": "हमारे समुद्रों में एक ऐसा जीव तैर रहा है जो कभी बूढ़ा होकर नहीं मरता। बूढ़ा होने पर यह अपनी उम्र को उल्टा कर लेता है। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Hay un animal en el océano que es biológicamente inmortal. Cuando envejece, revierte su edad por completo. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "The immortal jellyfish transforms its cells back into infant cells, repeating this cycle indefinitely. Scientists are studying its DNA to slow human aging. Follow for mind-blowing science facts.",
                    "text_hi": "अमर जेलीफ़िश अपनी कोशिकाओं को दोबारा शिशु अवस्था में बदल देती है। वैज्ञानिक इसके डीएनए की मदद से इंसानों की उम्र बढ़ाने पर काम कर रहे हैं। फॉलो करें ऐसे ही चमत्कारों के लिए।",
                    "text_es": "Esta medusa reinicia su ciclo celular indefinidamente. La ciencia analiza su genética para frenar el envejecimiento humano. Síguenos para más ciencia fascinante."
                }
            ]
        },
        {
            "title": "It Rains Liquid Diamonds on Neptune",
            "title_hi": "नेप्च्यून पर हीरों की बारिश का सच",
            "title_es": "Lluvia de Diamantes en Neptuno",
            "single": "If you think Earth has extreme weather, wait until you hear about Neptune and Uranus. Deep inside these ice giants, the atmospheric pressure is over 200,000 times greater than on Earth, and temperatures reach thousands of degrees. Under these extreme conditions, methane gas molecules are crushed, splitting carbon atoms from hydrogen. The intense pressure squeezes those carbon atoms into solid, sparkling diamonds. Millions of carats of diamonds literally rain down toward the planet's core, creating oceans of liquid carbon with floating diamond icebergs. A single storm on Neptune holds more diamonds than all of Earth's mines combined. Follow for mind-bending space facts.",
            "single_hi": "अगर आपको लगता है कि पृथ्वी का मौसम अजीब है, तो नेप्च्यून और यूरेनस ग्रह के बारे में जानकर आपके होश उड़ जाएंगे। इन बर्फीले ग्रहों की गहराइयों में वायुमंडलीय दबाव पृथ्वी से दो लाख गुना ज्यादा है। इतने भारी दबाव और गर्मी के कारण वहां मौजूद मीथेन गैस टूट जाती है और कार्बन के कण आपस में दबकर शुद्ध हीरे बन जाते हैं। जी हां, वहां आसमान से पानी की नहीं बल्कि लाखों कैरेट हीरों की बारिश होती है, जो नीचे जाकर हीरों के विशाल महासागर बनाती है। नेप्च्यून के सिर्फ एक तूफान में पृथ्वी की सारी खदानों से ज्यादा हीरे गिरते हैं। फॉलो करें अंतरिक्ष के हैरान करने वाले रहस्यों के लिए।",
            "single_es": "En planetas como Neptuno y Urano, la presión extrema aplasta las moléculas de metano, separando los átomos de carbono y convirtiéndolos en diamantes sólidos. Literalmente llueven millones de quilates de diamantes hacia el núcleo. Una sola tormenta contiene más gemas que todas las minas de la Tierra. Síguenos para más espacio.",
            "parts": [
                {
                    "part": 1,
                    "text": "Deep inside Neptune and Uranus, temperatures and pressure are so intense that the sky doesn't rain water. It rains literal sparkling diamonds. Follow for Part 2 to see how.",
                    "text_hi": "नेप्च्यून और यूरेनस की गहराइयों में इतना जबरदस्त दबाव है कि वहां बादलों से पानी नहीं, बल्कि असली हीरों की बारिश होती है। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En Neptuno y Urano la presión atmosférica es tan colosal que del cielo no cae agua, sino auténticos diamantes brillantes. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "The pressure crushes methane into pure carbon crystals that plunge through the atmosphere like hail, forming diamond oceans thousands of miles deep. Follow for more wild space discoveries.",
                    "text_hi": "भारी दबाव मीथेन को हीरों में बदल देता है जो ओलों की तरह बरसते हैं और हीरों के गहरे महासागर बनाते हैं। फॉलो करें अंतरिक्ष के रहस्यों के लिए।",
                    "text_es": "Esa presión convierte el metano en cristales de carbono que caen como granizo hacia el núcleo del planeta. Síguenos para más misterios del universo."
                }
            ]
        }
    ],

    "conspiracies": [
        {
            "title": "The Titanic Was Never Sunk",
            "title_hi": "टाइटैनिक कभी डूबा ही नहीं था?",
            "title_es": "El Titanic Nunca se Hundió",
            "single": "What if the ship that sank on April 15, 1912 wasn't the Titanic at all? Just months before the disaster, Titanic's identical twin sister ship, the Olympic, suffered severe hull damage in a collision. The insurance company refused to pay, leaving the White Star Line near bankruptcy. Conspiracy theorists point to compelling evidence: in the dark of night in Belfast, the owners secretly swapped the nameplates, furnishings, and registration of the damaged Olympic and the brand new Titanic. The plan was to stage an accident, sink the damaged Olympic under Titanic's name, and collect the massive insurance payout. Several wealthy tycoons, including J.P. Morgan himself, cancelled their tickets hours before departure. Coincidence or the greatest insurance fraud in human history? Drop your thoughts below.",
            "single_hi": "क्या होगा अगर आपको पता चले कि १५ अप्रैल १९१२ को जो जहाज डूबा, वो टाइटैनिक था ही नहीं? इस हादसे से कुछ महीने पहले टाइटैनिक का जुड़वां जहाज 'ओलंपिक' एक बड़े हादसे में बुरी तरह क्षतिग्रस्त हो गया था। बीमा कंपनी ने हर्जाना देने से मना कर दिया जिससे कंपनी दिवालिया होने की कगार पर पहुंच गई। माना जाता है कि बेलफास्ट में रात के अंधेरे में दोनों जहाजों के नाम और बोर्ड आपस में बदल दिए गए। प्लान यह था कि खराब जहाज को टाइटैनिक के नाम से डुबोकर बीमा का मोटा पैसा वसूला जाए। सबसे अजीब बात यह थी कि जे.पी. मॉर्गन जैसे कई बड़े अरबपतियों ने जहाज रवाना होने से कुछ घंटे पहले अपने टिकट अचानक कैंसिल कर दिए थे। क्या यह इत्तेफाक था या इतिहास का सबसे बड़ा घोटाला? कमेंट करें।",
            "single_es": "¿Y si el barco que se hundió en 1912 no fue el Titanic? Su barco gemelo, el Olympic, sufrió graves daños antes del viaje y el seguro no quiso pagar. La teoría sostiene que intercambiaron los nombres de ambos barcos para hundir el dañado a propósito y cobrar una fortuna. Banqueros millonarios cancelaron su viaje horas antes. ¿Tú qué crees? Comenta abajo.",
            "parts": [
                {
                    "part": 1,
                    "text": "Evidence suggests the Titanic never actually sank. Months before the voyage, its damaged twin sister ship, the Olympic, was allegedly swapped in a massive insurance fraud scheme. Follow for Part 2.",
                    "text_hi": "सबूत इशारा करते हैं कि टाइटैनिक कभी डूबा ही नहीं था। सफर से पहले उसके खराब जुड़वां जहाज ओलंपिक को बीमा घोटाले के तहत चुपके से बदल दिया गया था। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Muchos historiadores sospechan que el Titanic jamás se hundió, sino que su barco gemelo dañado fue intercambiado en un fraude millonario. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Billionaire owner J.P. Morgan suddenly cancelled his ticket hours before sailing, claiming illness, yet was seen healthy hours later. Was the iceberg accident staged? Follow for more secret history.",
                    "text_hi": "मालिक जे.पी. मॉर्गन ने बीमारी का बहाना बनाकर रवाना होने से ठीक पहले अपनी यात्रा रद्द कर दी थी। क्या बर्फ की चट्टान से टकराना पहले से तय था? फॉलो करें ऐसे ही रहस्यों के लिए।",
                    "text_es": "El dueño J.P. Morgan canceló su boleto horas antes diciendo estar enfermo, pero lo vieron de fiesta ese mismo día. Síguenos para más secretos históricos."
                }
            ]
        },
        {
            "title": "The Hidden Chamber Beneath the Sphinx",
            "title_hi": "स्फ़िंक्स के नीचे छुपा रहस्यमयी कमरा",
            "title_es": "La Cámara Oculta Bajo la Esfinge",
            "single": "In 1998, seismologists conducted ground-penetrating radar scans beneath the Great Sphinx of Giza. What they discovered shocked the archaeological community: a massive rectangular hollow chamber, 40 feet beneath the Sphinx's front paws, connected by a network of underground tunnels. Ancient texts dating back thousands of years refer to this chamber as the 'Hall of Records'—a legendary vault said to contain the lost technological knowledge and astronomy scrolls of a civilization that existed long before the Egyptian pharaohs. Shortly after the scan results were published, the Egyptian Antiquities Ministry banned all independent radar exploration and blocked further excavations. What are they hiding under the sand? Follow for classified secrets.",
            "single_hi": "१९९८ में जब वैज्ञानिकों ने गीज़ा के विशाल स्फ़िंक्स के नीचे रडार से जांच की, तो उनके होश उड़ गए। स्फ़िंक्स के पंजों के ठीक ४० फीट नीचे जमीन में एक बहुत बड़ा खोखला कमरा मिला, जो कई सुरंगों से जुड़ा हुआ था। प्राचीन मिस्र के ग्रंथों में इसे 'हॉल ऑफ रिकॉर्ड्स' कहा गया है—एक ऐसा गुप्त कमरा जिसमें प्राचीन सभ्यता के खोए हुए ज्ञान और तकनीकों के ग्रंथ दबे होने की बात कही गई है। लेकिन जैसे ही यह रिपोर्ट बाहर आई, मिस्र के पुरातत्व विभाग ने वहां किसी भी तरह की खुदाई पर हमेशा के लिए प्रतिबंध लगा दिया। क्या वे जमीन के नीचे कोई ऐसा सच छिपा रहे हैं जो इतिहास की किताबों को हमेशा के लिए बदल देगा? फॉलो करें।",
            "single_es": "En 1998, radares detectaron una enorme cámara subterránea a 12 metros bajo las patas de la Gran Esfinge de Giza. Textos antiguos la llaman el 'Salón de los Registros', con el conocimiento de una civilización olvidada. Las autoridades egipcias prohibieron excavar allí. ¿Qué ocultan bajo la arena? Síguenos.",
            "parts": [
                {
                    "part": 1,
                    "text": "Ground radar beneath the Great Sphinx revealed a massive rectangular chamber forty feet underground, but governments immediately shut down excavations. Follow for Part 2.",
                    "text_hi": "गीज़ा के स्फ़िंक्स के नीचे रडार ने ४० फीट गहरा विशाल गुप्त कमरा खोज निकाला, लेकिन सरकारों ने तुरंत सारी खुदाई पर रोक लगा दी। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "Radares bajo la Esfinge descubrieron una cámara subterránea a 12 metros de profundidad, pero las excavaciones fueron prohibidas de inmediato. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "Ancient papyri call it the Hall of Records, containing secrets from a civilization older than Egypt. Why are cameras forbidden from filming there today? Follow for more ancient mysteries.",
                    "text_hi": "प्राचीन ग्रंथों में इसे हॉल ऑफ रिकॉर्ड्स कहा गया है, जिसमें मिस्र से भी पुरानी सभ्यता का ज्ञान छिपा है। आज भी वहां कैमरा ले जाना मना क्यों है? फॉलो करें।",
                    "text_es": "Papiros antiguos dicen que guarda los secretos de una civilización anterior a los faraones. ¿Por qué prohíben filmar allí hoy? Síguenos para más misterios."
                }
            ]
        }
    ],

    "finance_crypto": [
        {
            "title": "The $700 Million Hard Drive in a Dump",
            "title_hi": "कचरे में फेंकी गई ७०० मिलियन डॉलर की हार्ड ड्राइव",
            "title_es": "El Disco Duro de 700 Millones en la Basura",
            "single": "In 2013, a Welsh IT worker named James Howells was cleaning out his desk. He accidentally tossed an old laptop hard drive into the trash. That hard drive held the private cryptographic keys to 8,000 Bitcoins. At the time, they were worth around a few thousand dollars. Today, those 8,000 Bitcoins are worth over 700 million dollars. For the past decade, James has been begging the local city council for permission to dig through 100,000 tons of garbage at the local landfill using AI scanners and robot dogs. But the council repeatedly rejected his plan due to environmental concerns. Imagine knowing that 700 million dollars is buried in a pile of garbage, but you're not legally allowed to touch it. What would you do? Drop your thoughts below.",
            "single_hi": "२०१३ में जेम्स हॉवेल्स नाम का एक आईटी कर्मचारी अपना कमरा साफ कर रहा था। गलती से उसने एक पुरानी हार्ड ड्राइव कचरे के डिब्बे में फेंक दी। उस हार्ड ड्राइव में ८,००० बिटकॉइन्स की प्राइवेट कीज़ मौजूद थीं। उस समय उनकी कीमत कुछ हजार डॉलर थी। लेकिन आज उन ८,००० बिटकॉइन्स की कीमत ७०० मिलियन डॉलर यानी करीब ६,००० करोड़ रुपये है! पिछले दस सालों से जेम्स अपनी स्थानीय नगर पालिका से गुहार लगा रहा है कि उसे कचरे के विशाल ढेर में एआई स्कैनर्स की मदद से खुदाई करने दी जाए। लेकिन प्रशासन ने पर्यावरण के नियमों का हवाला देकर हर बार मना कर दिया। सोचिए, आपको पता हो कि आपकी ६,००० करोड़ की दौलत कचरे के नीचे दबी है, लेकिन आप उसे छू भी नहीं सकते। अगर आप उसकी जगह होते तो क्या करते? कमेंट करें।",
            "single_es": "En 2013, James tiró a la basura un viejo disco duro que contenía las claves de 8,000 Bitcoins. Hoy valen más de 700 millones de dólares. Lleva diez años pidiendo permiso para buscarlo en el vertedero con inteligencia artificial, pero el gobierno local no lo autoriza. ¿Qué harías tú en su lugar? Comenta abajo.",
            "parts": [
                {
                    "part": 1,
                    "text": "In 2013, an IT worker accidentally threw away an old hard drive. Today, that small piece of metal sitting in a municipal landfill is worth over $700 million. Follow for Part 2.",
                    "text_hi": "२०१३ में एक शख्स ने गलती से एक पुरानी हार्ड ड्राइव कचरे में फेंक दी। आज कचरे के ढेर में पड़ी उस छोटी सी ड्राइव की कीमत ६,००० करोड़ रुपये से ज्यादा है। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 2013, un informático tiró un disco duro a la basura por error. Hoy vale más de 700 millones de dólares en un vertedero. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "It contains 8,000 Bitcoins, but the city council refuses to let him dig, threatening arrest if he steps near the site. $700 million locked in trash forever. Follow for insane wealth stories.",
                    "text_hi": "उसमें ८,००० बिटकॉइन हैं, लेकिन प्रशासन ने वहां जाने पर गिरफ्तारी की चेतावनी दे रखी है। ६,००० करोड़ हमेशा के लिए कचरे में दफन हो गए। फॉलो करें ऐसी ही दिलचस्प कहानियों के लिए।",
                    "text_es": "Contiene 8,000 Bitcoins, pero el ayuntamiento amenaza con arrestarlo si intenta excavar. Fortuna enterrada para siempre. Síguenos para más finanzas."
                }
            ]
        },
        {
            "title": "The 10,000 Bitcoin Pizza Lesson",
            "title_hi": "१०,००० बिटकॉइन का पिज्जा और वित्तीय सबक",
            "title_es": "La Pizza de los 10,000 Bitcoins",
            "single": "On May 22, 2010, programmer Laszlo Hanyecz posted on an online forum offering 10,000 Bitcoins to anyone who would order and deliver two large Papa John's pizzas to his house. At the time, Bitcoin was worth less than half a cent. A fellow user accepted the offer, bought the two pizzas for $41, and took the 10,000 coins. Today, those two pizzas cost over 800 million dollars, making it the most expensive meal in human history. But here is the lesson most people miss: Laszlo proved Bitcoin actually worked as a real-world currency. Without that first transaction, crypto might have died right there. Never mock the early pioneers. Double tap if you would have eaten those pizzas!",
            "single_hi": "२२ मई २०१० को लास्ज़लो हानयेक नाम के एक कंप्यूटर प्रोग्रामर ने ऑनलाइन फोरम पर लिखा कि जो कोई उसके घर दो बड़े पापा जॉन्स पिज्जा डिलीवर करवाएगा, वह उसे १०,००० बिटकॉइन देगा। उस समय एक बिटकॉइन की कीमत आधे सेंट से भी कम थी। एक लड़के ने ४१ डॉलर में दो पिज्जा मंगवाए और बदले में १०,००० बिटकॉइन ले लिए। आज उन दो पिज्जा की कीमत ८०० मिलियन डॉलर यानी करीब ७,००० करोड़ रुपये है! यह मानव इतिहास का सबसे महंगा खाना बन गया। लेकिन सीखने वाली बात यह है कि लास्ज़लो ने साबित किया था कि बिटकॉइन से सच में चीजें खरीदी जा सकती हैं। अगर वो यह न करता, तो शायद आज क्रिप्टो का कोई नाम भी न जानता। इस रील को लाइक और शेयर करें!",
            "single_es": "En 2010, un programador pagó 10,000 Bitcoins por dos pizzas de Papa John's que costaban 41 dólares. Hoy esas pizzas valen más de 800 millones de dólares: la comida más cara de la historia. Demostró que el Bitcoin servía como dinero real. Dale like si te pareció increíble.",
            "parts": [
                {
                    "part": 1,
                    "text": "On May 22, 2010, a man spent 10,000 Bitcoins to buy two pepperoni pizzas. Today, those two pizzas are worth nearly one billion dollars. Follow for Part 2.",
                    "text_hi": "२२ मई २०१० को एक व्यक्ति ने दो पिज्जा खरीदने के लिए १०,००० बिटकॉइन खर्च किए। आज उन दो पिज्जा की कीमत करीब सात हजार करोड़ रुपये है। पार्ट २ के लिए अभी फॉलो करें।",
                    "text_es": "En 2010, un programador pagó 10,000 Bitcoins por dos pizzas. Hoy valen cerca de mil millones de dólares. Síguenos para la Parte 2."
                },
                {
                    "part": 2,
                    "text": "He never regretted it because that single purchase proved cryptocurrency could be used in the real world. May 22nd is now celebrated as Bitcoin Pizza Day worldwide. Follow for daily crypto stories.",
                    "text_hi": "उसे कभी अफसोस नहीं हुआ क्योंकि उस पहली खरीद ने साबित किया कि डिजिटल करेंसी सच में काम करती है। हर साल २२ मई को बिटकॉइन पिज्जा डे मनाया जाता है। फॉलो करें।",
                    "text_es": "Nunca se arrepintió, pues demostró la utilidad real de las criptomonedas. Cada 22 de mayo se celebra el Bitcoin Pizza Day. Síguenos para más historias de riqueza."
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
    
    if language == "hi":
        lang_instruction = "CRITICAL REQUIREMENT: Output MUST be entirely written in natural, fluent Hindi (हिंदी/देवनागरी लिपि). Do not use English script for the spoken words."
    else:
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


def generate_topic_script_fallback(niche_key: str, topic: str, is_multipart: bool, parts_count: int, lang: str) -> Dict[str, Any]:
    """
    Intelligently generates a custom script when the user supplies their own topic
    and no external LLM API is available. Formatted for the selected language.
    """
    niche_info = NICHES.get(niche_key, NICHES["true_crime"])
    clean_topic = topic.strip()

    if lang == "hi":
        title = f"{clean_topic}: अनसुलझा रहस्य"
        script = (
            f"क्या आप जानते हैं कि {clean_topic} के पीछे की असली कहानी क्या है? "
            f"इतिहास के पन्नों में इसे एक सामान्य घटना बताया गया, लेकिन असलियत इससे कहीं ज्यादा चौंकाने वाली है। "
            f"हाल ही में सामने आए दस्तावेजों से पता चला है कि {clean_topic} के बारे में जो हमें बताया गया, "
            f"वह सिर्फ आधा सच था। जब विशेषज्ञों ने गहराई से जांच की, तो उन्हें ऐसे सुराग मिले जिन्होंने सबको हैरान कर दिया। "
            f"क्या आपको लगता है कि {clean_topic} का सच दुनिया से छिपाया गया है? अपनी राय कमेंट में जरूर बताएं और फॉलो करें।"
        )
        caption = f"😱 {clean_topic} का चौंकाने वाला सच! क्या आप जानते थे?"
        part1 = (
            f"क्या आप जानते हैं कि {clean_topic} के पीछे एक ऐसा रहस्य छिपा है जिसे आज तक कोई सुलझा नहीं पाया? "
            f"शुरुआत में सब कुछ सामान्य लगा, लेकिन जब सच्चाई सामने आई तो सबके होश उड़ गए। "
            f"पार्ट २ में जानिए कि वास्तव में वहां क्या हुआ था! अभी फॉलो करें।"
        )
        part2 = (
            f"जब जांचकर्ताओं ने {clean_topic} की गहराई से पड़ताल की, तो उन्हें ऐसे साक्ष्य मिले जिन्हें सार्वजनिक नहीं किया गया। "
            f"आज भी इस पर रहस्य का पर्दा पड़ा हुआ है। आपको क्या लगता है? अपनी राय कमेंट में बताएं और फॉलो करें।"
        )
    elif lang == "es":
        title = f"El Secreto Oculto de {clean_topic}"
        script = (
            f"¿Sabías lo que realmente se oculta detrás de {clean_topic}? "
            f"Durante años nos contaron una versión oficial, pero la verdad es mucho más inquietante. "
            f"Investigadores descubrieron que sobre {clean_topic} se ocultaron pruebas clave. "
            f"¿Crees que nos dijeron toda la verdad? Comenta abajo y síguenos para más revelaciones."
        )
        caption = f"😱 La verdad oculta sobre {clean_topic}. ¡Increíble!"
        part1 = f"¿Conoces el misterio detrás de {clean_topic}? Lo que descubrieron te dejará sin palabras. Síguenos para la Parte 2."
        part2 = f"Las pruebas finales sobre {clean_topic} cambiaron la historia para siempre. ¿Qué opinas? Comenta abajo y síguenos."
    else:
        title = f"The Untold Truth of {clean_topic}"
        script = (
            f"What if everything you thought you knew about {clean_topic} was completely wrong? "
            f"For decades, the official story seemed airtight. But freshly uncovered files tell a far darker tale. "
            f"When researchers dug beneath the surface of {clean_topic}, they found inconsistencies that challenge modern history. "
            f"Do you believe the truth was intentionally buried? Drop your thoughts in the comments and hit follow for more."
        )
        caption = f"😱 The shocking reality behind {clean_topic}! Did you know this?"
        part1 = f"What really happened with {clean_topic}? The official story leaves out the most shocking detail. Follow for Part 2."
        part2 = f"When the full truth about {clean_topic} surfaced, it changed everything. What do you think really happened? Follow for more."

    if not is_multipart:
        return {
            "title": title,
            "niche": niche_key,
            "language": lang,
            "is_multipart": False,
            "caption": caption,
            "hashtags": niche_info["hashtags"],
            "script": script
        }
    else:
        return {
            "title": title,
            "niche": niche_key,
            "language": lang,
            "is_multipart": True,
            "caption": caption,
            "hashtags": niche_info["hashtags"],
            "parts": [
                {"part": 1, "hook": f"Part 1: {clean_topic}", "script": part1},
                {"part": 2, "hook": f"Part 2: {clean_topic}", "script": part2}
            ]
        }


def generate_script(
    niche: str,
    topic: Optional[str] = None,
    is_multipart: bool = False,
    parts_count: int = 2,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generates a viral reel script based on the chosen niche, topic, format, and language.
    Priority:
    1. OpenAI GPT-4o-mini (if OPENAI_API_KEY is configured)
    2. Google Gemini (if GEMINI_API_KEY is configured)
    3. Ollama (if running locally)
    4. Topic-Aware Custom Fallback (if user typed a specific topic)
    5. Non-Repeating Rotating Multi-lingual Curated Stories
    """
    niche_key = niche if niche in NICHES else "true_crime"
    niche_info = NICHES[niche_key]
    lang = language or "en"
    
    # Check if an external LLM should be used
    prompt = generate_script_prompt(niche_key, topic, is_multipart, parts_count, lang)
    result = None

    # Priority 1: OpenAI
    if OPENAI_API_KEY and (LLM_PROVIDER in ["openai", "builtin"] or not GEMINI_API_KEY):
        result = call_openai(prompt)
    # Priority 2: Gemini
    elif GEMINI_API_KEY and (LLM_PROVIDER in ["gemini", "builtin"]):
        result = call_gemini(prompt)
    # Priority 3: Ollama
    elif LLM_PROVIDER == "ollama":
        result = call_ollama(prompt)

    if result:
        result["niche"] = niche_key
        result["is_multipart"] = is_multipart
        result["language"] = lang
        return result

    # If the user typed a specific custom topic, build a dedicated story for that topic
    if topic and topic.strip():
        return generate_topic_script_fallback(niche_key, topic.strip(), is_multipart, parts_count, lang)

    # Builtin Curated Multi-lingual Story Engine (Guaranteed non-repeating)
    pool = BUILTIN_STORIES.get(niche_key)
    if not pool:
        pool = BUILTIN_STORIES["true_crime"]

    # Rotate through stories so consecutive requests NEVER give the same story
    last_idx = _LAST_STORY_INDICES.get(niche_key, -1)
    available_indices = [i for i in range(len(pool)) if i != last_idx]
    if not available_indices:
        available_indices = list(range(len(pool)))
    
    chosen_idx = random.choice(available_indices)
    _LAST_STORY_INDICES[niche_key] = chosen_idx
    selected_story = pool[chosen_idx]

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
        parts_data = selected_story.get("parts", [])
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
