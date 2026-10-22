/* ==========================================================================
   ReelCraft AI Studio — Interactive Client Logic
   ========================================================================== */

let appState = {
  niches: {},
  languages: [],
  voices: [],
  speeds: [],
  selectedLanguage: "en",
  selectedNiche: "true_crime",
  selectedVoice: "en-US-ChristopherNeural",
  selectedSpeed: "-10%",
  format: "single", // "single" or "multi"
  partsCount: 2,
  currentScriptData: null,
  activePartIndex: 0,
  renderedVideos: [],
  currentVideoIndex: 0,
  enableAiVisuals: true,
  numScenes: 4,
  previewedScenes: null
};

const NICHE_ICONS = {
  true_crime: "🔍",
  scary_horror: "👻",
  reddit_stories: "💬",
  mindset_stoic: "🏛️",
  wild_facts: "🤯",
  conspiracies: "🕵️",
  finance_crypto: "💰"
};

const THEME_NAMES = {
  true_crime: "Abyss Blue",
  scary_horror: "Blood Darkness",
  reddit_stories: "Neon Grid",
  mindset_stoic: "Golden Slate",
  wild_facts: "Cosmic Cyan",
  conspiracies: "Sepia Archive",
  finance_crypto: "Emerald Matrix"
};

// DOM Elements
const langSelect = document.getElementById("lang-select");
const nicheThemeBadge = document.getElementById("niche-theme-badge");
const nicheSelector = document.getElementById("niche-selector");
const customTopicInput = document.getElementById("custom-topic");
const btnFormatSingle = document.getElementById("btn-format-single");
const btnFormatMulti = document.getElementById("btn-format-multi");
const partsSelectorGroup = document.getElementById("parts-selector-group");
const partsCountSelect = document.getElementById("parts-count");
const voiceSelect = document.getElementById("voice-select");
const speedSelect = document.getElementById("speed-select");
const bgSelect = document.getElementById("bg-select");
const btnGenerateScript = document.getElementById("btn-generate-script");

const scriptTitle = document.getElementById("script-title");
const multipartTabs = document.getElementById("multipart-tabs");
const scriptContent = document.getElementById("script-content");
const scriptCaption = document.getElementById("script-caption");
const btnRenderVideo = document.getElementById("btn-render-video");
const renderProgress = document.getElementById("render-progress");
const progressStatus = document.getElementById("progress-status");

const player = document.getElementById("player");
const metaDuration = document.getElementById("meta-duration");
const metaSize = document.getElementById("meta-size");
const metaAiVisuals = document.getElementById("meta-ai-visuals");
const multiVideoSelector = document.getElementById("multi-video-selector");
const btnPublishInstagram = document.getElementById("btn-publish-instagram");
const btnDownloadMp4 = document.getElementById("btn-download-mp4");
const btnCopyCaption = document.getElementById("btn-copy-caption");
const historyTbody = document.getElementById("history-tbody");
const btnRefreshHistory = document.getElementById("btn-refresh-history");

// AI Visuals Elements
const aiVisualsSwitch = document.getElementById("ai-visuals-switch");
const sceneCountGroup = document.getElementById("scene-count-group");
const sceneCountSelect = document.getElementById("scene-count");
const sceneStoryboard = document.getElementById("scene-storyboard");
const storyboardCount = document.getElementById("storyboard-count");
const sceneGrid = document.getElementById("scene-grid");
const btnPreviewScenes = document.getElementById("btn-preview-scenes");
const renderedScenesStrip = document.getElementById("rendered-scenes-strip");

// Modals
const btnOpenAutopilot = document.getElementById("btn-open-autopilot");
const modalAutopilot = document.getElementById("modal-autopilot");
const btnCloseAutopilot = document.getElementById("btn-close-autopilot");
const btnCancelAutopilot = document.getElementById("btn-cancel-autopilot");
const btnSaveAutopilot = document.getElementById("btn-save-autopilot");
const autopilotBadge = document.getElementById("autopilot-badge");
const autopilotEnableSwitch = document.getElementById("autopilot-enable-switch");
const autopilotInterval = document.getElementById("autopilot-interval");
const autopilotNiche = document.getElementById("autopilot-niche");
const autoStatusText = document.getElementById("auto-status-text");
const autoNextRun = document.getElementById("auto-next-run");
const autoTotalCount = document.getElementById("auto-total-count");

const btnOpenSettings = document.getElementById("btn-open-settings");
const modalSettings = document.getElementById("modal-settings");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnCancelSettings = document.getElementById("btn-cancel-settings");
const btnSaveSettings = document.getElementById("btn-save-settings");
const setIgAccount = document.getElementById("set-ig-account");
const setIgToken = document.getElementById("set-ig-token");
const setImageProvider = document.getElementById("set-image-provider");
const setOpenaiKey = document.getElementById("set-openai-key");

const toast = document.getElementById("toast");

// Initialize Application
async function init() {
  await Promise.all([
    loadLanguages(),
    loadNiches(),
    loadVoices(),
    loadAssets(),
    loadAutopilotStatus(),
    loadHistory(),
    loadSettings()
  ]);
  setupEventListeners();
}

// Fetch Languages
async function loadLanguages() {
  try {
    const res = await fetch("/api/languages");
    const data = await res.json();
    appState.languages = data.languages;
    langSelect.innerHTML = "";
    appState.languages.forEach(l => {
      const opt = document.createElement("option");
      opt.value = l.code;
      opt.textContent = `${l.flag} ${l.name}`;
      langSelect.appendChild(opt);
    });
    langSelect.value = appState.selectedLanguage;
  } catch (err) {
    console.error("Failed to load languages:", err);
  }
}

// Fetch Niches
async function loadNiches() {
  try {
    const res = await fetch("/api/niches");
    const data = await res.json();
    appState.niches = data.niches;
    renderNicheList();
    updateThemeBadge(appState.selectedNiche);
  } catch (err) {
    console.error("Failed to load niches:", err);
  }
}

function renderNicheList() {
  nicheSelector.innerHTML = "";
  autopilotNiche.innerHTML = "";

  Object.entries(appState.niches).forEach(([key, info]) => {
    const icon = NICHE_ICONS[key] || "✨";
    const card = document.createElement("div");
    card.className = `niche-card ${key === appState.selectedNiche ? "selected" : ""}`;
    card.dataset.niche = key;
    card.innerHTML = `
      <span class="niche-icon">${icon}</span>
      <div class="niche-info">
        <span class="niche-name">${info.name}</span>
        <span class="niche-desc">${info.description}</span>
      </div>
    `;
    card.addEventListener("click", () => selectNiche(key));
    nicheSelector.appendChild(card);

    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = `${icon} ${info.name}`;
    autopilotNiche.appendChild(opt);
  });
}

function updateThemeBadge(nicheKey) {
  const name = THEME_NAMES[nicheKey] || "Niche Visuals";
  nicheThemeBadge.textContent = `Visual: ${name}`;
}

function selectNiche(nicheKey) {
  appState.selectedNiche = nicheKey;
  updateThemeBadge(nicheKey);

  document.querySelectorAll(".niche-card").forEach(el => {
    el.classList.toggle("selected", el.dataset.niche === nicheKey);
  });

  // Only auto-switch voice if current language is English
  if (appState.selectedLanguage === "en") {
    const nicheInfo = appState.niches[nicheKey];
    if (nicheInfo && nicheInfo.default_voice) {
      voiceSelect.value = nicheInfo.default_voice;
      appState.selectedVoice = nicheInfo.default_voice;
    }
  }

  // Reset scene previews when niche changes
  appState.previewedScenes = null;
  clearSceneGrid();
}

// Fetch Voices (Filtered by Language)
async function loadVoices(langCode = "en") {
  try {
    const res = await fetch(`/api/voices?lang=${langCode}`);
    const data = await res.json();
    appState.voices = data.voices;
    voiceSelect.innerHTML = "";

    appState.voices.forEach(v => {
      const opt = document.createElement("option");
      opt.value = v.id;
      opt.textContent = `${v.name} — ${v.style}`;
      voiceSelect.appendChild(opt);
    });

    if (appState.voices.length > 0) {
      voiceSelect.value = appState.voices[0].id;
      appState.selectedVoice = appState.voices[0].id;
    }
  } catch (err) {
    console.error("Failed to load voices:", err);
  }
}

// Fetch Assets
async function loadAssets() {
  try {
    const res = await fetch("/api/assets");
    const data = await res.json();
    if (data.backgrounds && data.backgrounds.length > 0) {
      bgSelect.innerHTML = `<option value="">Auto: Dynamic Niche-Themed Visuals</option>`;
      data.backgrounds.forEach(bg => {
        const opt = document.createElement("option");
        opt.value = bg;
        opt.textContent = `Custom: ${bg}`;
        bgSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Failed to load assets:", err);
  }
}

// Event Listeners
function setupEventListeners() {
  // Language Change Listener
  langSelect.addEventListener("change", async (e) => {
    appState.selectedLanguage = e.target.value;
    await loadVoices(appState.selectedLanguage);
    showToast(`Language switched to ${langSelect.options[langSelect.selectedIndex].text}! 🌐`);
  });

  // Format Toggles
  btnFormatSingle.addEventListener("click", () => {
    appState.format = "single";
    btnFormatSingle.classList.add("active");
    btnFormatMulti.classList.remove("active");
    partsSelectorGroup.classList.add("hidden");
    multipartTabs.classList.add("hidden");
  });

  btnFormatMulti.addEventListener("click", () => {
    appState.format = "multi";
    btnFormatMulti.classList.add("active");
    btnFormatSingle.classList.remove("active");
    partsSelectorGroup.classList.remove("hidden");
  });

  partsCountSelect.addEventListener("change", (e) => {
    appState.partsCount = parseInt(e.target.value, 10);
  });

  voiceSelect.addEventListener("change", (e) => {
    appState.selectedVoice = e.target.value;
  });

  speedSelect.addEventListener("change", (e) => {
    appState.selectedSpeed = e.target.value;
  });

  // AI Visuals Toggle
  aiVisualsSwitch.addEventListener("change", (e) => {
    appState.enableAiVisuals = e.target.checked;
    sceneCountGroup.style.opacity = e.target.checked ? "1" : "0.4";
    sceneCountGroup.style.pointerEvents = e.target.checked ? "auto" : "none";
    
    if (e.target.checked) {
      showToast("🎨 AI Scene Visuals enabled — cinematic images will be generated for each scene!");
    } else {
      showToast("AI Scene Visuals disabled — will use procedural/video backgrounds.");
    }
  });

  sceneCountSelect.addEventListener("change", (e) => {
    appState.numScenes = parseInt(e.target.value, 10);
  });

  // Scene Preview Button
  btnPreviewScenes.addEventListener("click", handlePreviewScenes);

  // Generate Script Action
  btnGenerateScript.addEventListener("click", handleGenerateScript);

  // Render Video Action
  btnRenderVideo.addEventListener("click", handleRenderVideo);

  // Publish & Share Actions
  btnPublishInstagram.addEventListener("click", handlePublishInstagram);
  btnCopyCaption.addEventListener("click", () => {
    navigator.clipboard.writeText(scriptCaption.value);
    showToast("Caption & Hashtags copied to clipboard! 📋");
  });
  btnRefreshHistory.addEventListener("click", loadHistory);

  // Autopilot Modal
  btnOpenAutopilot.addEventListener("click", () => {
    modalAutopilot.classList.remove("hidden");
    loadAutopilotStatus();
  });
  btnCloseAutopilot.addEventListener("click", () => modalAutopilot.classList.add("hidden"));
  btnCancelAutopilot.addEventListener("click", () => modalAutopilot.classList.add("hidden"));
  btnSaveAutopilot.addEventListener("click", handleSaveAutopilot);

  // Settings Modal
  btnOpenSettings.addEventListener("click", () => modalSettings.classList.remove("hidden"));
  btnCloseSettings.addEventListener("click", () => modalSettings.classList.add("hidden"));
  btnCancelSettings.addEventListener("click", () => modalSettings.classList.add("hidden"));
  btnSaveSettings.addEventListener("click", handleSaveSettings);
}

// Generate Script Handler
async function handleGenerateScript() {
  btnGenerateScript.disabled = true;
  btnGenerateScript.innerHTML = `<span class="btn-icon">⏳</span> Generating Story...`;

  const payload = {
    niche: appState.selectedNiche,
    topic: customTopicInput.value.trim() || null,
    is_multipart: appState.format === "multi",
    parts_count: appState.partsCount,
    language: appState.selectedLanguage
  };

  try {
    const res = await fetch("/api/generate-script", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    
    if (result.success && result.data) {
      appState.currentScriptData = result.data;
      appState.previewedScenes = null;
      displayGeneratedScript(result.data);
      btnRenderVideo.disabled = false;
      
      // Show the storyboard section if AI visuals are enabled
      if (appState.enableAiVisuals) {
        showSceneStoryboard();
      }
      
      showToast("Script generated successfully! Review and click Render. ✨");
    } else {
      showToast("Failed to generate script: " + (result.detail || "Unknown error"));
    }
  } catch (err) {
    showToast("Error generating script: " + err.message);
  } finally {
    btnGenerateScript.disabled = false;
    btnGenerateScript.innerHTML = `<span class="btn-icon">✨</span> Generate Script & Story`;
  }
}

function displayGeneratedScript(data) {
  scriptTitle.value = data.title || "Viral Reel Story";
  const tags = data.hashtags ? data.hashtags.join(" ") : "";
  scriptCaption.value = `${data.caption || ""}\n\n${tags}`;

  if (!data.is_multipart) {
    multipartTabs.classList.add("hidden");
    scriptContent.value = data.script || "";
  } else {
    multipartTabs.classList.remove("hidden");
    multipartTabs.innerHTML = "";
    const parts = data.parts || [];
    appState.activePartIndex = 0;

    parts.forEach((p, idx) => {
      const tab = document.createElement("button");
      tab.className = `part-tab-btn ${idx === 0 ? "active" : ""}`;
      tab.textContent = `Part ${p.part}`;
      tab.addEventListener("click", () => {
        if (data.parts[appState.activePartIndex]) {
          data.parts[appState.activePartIndex].script = scriptContent.value;
        }
        appState.activePartIndex = idx;
        document.querySelectorAll(".part-tab-btn").forEach((b, i) => {
          b.classList.toggle("active", i === idx);
        });
        scriptContent.value = p.script || "";
      });
      multipartTabs.appendChild(tab);
    });

    if (parts.length > 0) {
      scriptContent.value = parts[0].script || "";
    }
  }
}

// =====================================================
// AI Scene Visuals — Storyboard & Preview
// =====================================================

function showSceneStoryboard() {
  sceneStoryboard.classList.remove("hidden");
  clearSceneGrid();
  
  // Show placeholder loading cards
  const numScenes = appState.numScenes;
  storyboardCount.textContent = numScenes;
  
  for (let i = 0; i < numScenes; i++) {
    const card = document.createElement("div");
    card.className = "scene-card-loading";
    card.innerHTML = `<span class="loading-icon">🎨</span>`;
    sceneGrid.appendChild(card);
  }
}

function clearSceneGrid() {
  sceneGrid.innerHTML = "";
  storyboardCount.textContent = "0";
}

function renderSceneImages(scenes) {
  sceneGrid.innerHTML = "";
  storyboardCount.textContent = scenes.length;
  
  scenes.forEach(scene => {
    const card = document.createElement("div");
    card.className = "scene-card";
    
    if (scene.image_url || scene.url) {
      const imgUrl = scene.image_url || scene.url;
      card.innerHTML = `
        <img src="${imgUrl}" alt="Scene ${scene.scene_index || scene.scene}" loading="lazy">
        <div class="scene-card-overlay">
          <span class="scene-number">Scene ${scene.scene_index || scene.scene}</span>
          <span class="scene-status-icon">✅</span>
        </div>
      `;
      // Lightbox on click
      card.addEventListener("click", () => openSceneLightbox(imgUrl));
    } else {
      card.innerHTML = `
        <div class="scene-card-overlay" style="inset: 0; display: flex; align-items: center; justify-content: center; background: var(--bg-surface);">
          <span style="font-size: 1.5rem;">⚠️</span>
        </div>
        <div class="scene-card-overlay">
          <span class="scene-number">Scene ${scene.scene_index || scene.scene}</span>
          <span class="scene-status-icon">❌</span>
        </div>
      `;
    }
    
    sceneGrid.appendChild(card);
  });
}

function openSceneLightbox(imageUrl) {
  const lightbox = document.createElement("div");
  lightbox.className = "scene-lightbox";
  lightbox.innerHTML = `<img src="${imageUrl}" alt="Scene Preview">`;
  lightbox.addEventListener("click", () => lightbox.remove());
  document.body.appendChild(lightbox);
}

async function handlePreviewScenes() {
  const scriptText = scriptContent.value.trim();
  if (!scriptText) {
    showToast("Please generate or write a script first!");
    return;
  }
  
  btnPreviewScenes.disabled = true;
  btnPreviewScenes.textContent = "⏳ Generating...";
  showSceneStoryboard();
  
  try {
    const res = await fetch("/api/generate-images", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        script_text: scriptText,
        niche: appState.selectedNiche,
        num_scenes: appState.numScenes
      })
    });
    const result = await res.json();
    
    if (result.success && result.data && result.data.scenes) {
      appState.previewedScenes = result.data.scenes;
      renderSceneImages(result.data.scenes);
      showToast(`🎨 ${result.data.images_generated} scene images generated! Click to preview.`);
    } else {
      clearSceneGrid();
      showToast("Failed to generate scene images: " + (result.detail || "Check API key settings"));
    }
  } catch (err) {
    clearSceneGrid();
    showToast("Scene preview error: " + err.message);
  } finally {
    btnPreviewScenes.disabled = false;
    btnPreviewScenes.textContent = "🎨 Preview Scenes";
  }
}

// =====================================================
// Render Video Handler (Updated with AI Visuals)
// =====================================================

async function handleRenderVideo() {
  if (!appState.currentScriptData) return;

  if (!appState.currentScriptData.is_multipart) {
    appState.currentScriptData.script = scriptContent.value;
  } else {
    if (appState.currentScriptData.parts[appState.activePartIndex]) {
      appState.currentScriptData.parts[appState.activePartIndex].script = scriptContent.value;
    }
  }
  appState.currentScriptData.title = scriptTitle.value;

  btnRenderVideo.disabled = true;
  renderProgress.classList.remove("hidden");
  
  if (appState.enableAiVisuals) {
    progressStatus.textContent = `🎨 Generating AI scene visuals for ${appState.niches[appState.selectedNiche]?.name || "Niche"}...`;
  } else {
    progressStatus.textContent = `Synthesizing neural voiceover (${speedSelect.options[speedSelect.selectedIndex].text})...`;
  }

  const payload = {
    script_data: appState.currentScriptData,
    voice: appState.selectedVoice,
    speech_speed: speedSelect.value,
    language: appState.selectedLanguage,
    custom_bg: bgSelect.value ? `assets/backgrounds/${bgSelect.value}` : null,
    enable_ai_visuals: appState.enableAiVisuals,
    num_scenes: appState.numScenes,
    previewed_scenes: appState.previewedScenes
  };

  try {
    // Update progress text after a delay
    setTimeout(() => {
      if (!renderProgress.classList.contains("hidden")) {
        progressStatus.textContent = `🎬 Rendering cinematic video with ${appState.enableAiVisuals ? 'AI scene visuals' : 'niche-themed backgrounds'}...`;
      }
    }, 5000);
    
    setTimeout(() => {
      if (!renderProgress.classList.contains("hidden")) {
        progressStatus.textContent = `🔊 Mixing voiceover audio & background music...`;
      }
    }, 12000);

    const res = await fetch("/api/render-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.success && result.videos) {
      appState.renderedVideos = result.videos;
      appState.currentVideoIndex = 0;
      updateVideoPlayer(result.videos[0]);
      setupMultiVideoSwitcher(result.videos);
      
      // Show scene images in storyboard if they were generated
      const firstVideo = result.videos[0];
      if (firstVideo.scene_images && firstVideo.scene_images.length > 0) {
        sceneStoryboard.classList.remove("hidden");
        renderSceneImages(firstVideo.scene_images);
        showRenderedScenesStrip(firstVideo.scene_images);
      }
      
      showToast("🎉 Video successfully rendered! Watch the preview on the right.");
      loadHistory();
    } else {
      showToast("Render failed: " + (result.detail || "Unknown error"));
    }
  } catch (err) {
    showToast("Render error: " + err.message);
  } finally {
    btnRenderVideo.disabled = false;
    renderProgress.classList.add("hidden");
  }
}

function updateVideoPlayer(video) {
  player.src = video.url;
  player.load();
  player.play().catch(() => {});

  metaDuration.textContent = `⏱️ ${video.duration}s`;
  metaSize.textContent = `💾 ${video.file_size_mb} MB`;
  btnDownloadMp4.href = video.url;
  btnDownloadMp4.download = video.filename;
  
  // Show AI Visuals badge
  if (video.has_ai_visuals) {
    metaAiVisuals.classList.remove("hidden");
  } else {
    metaAiVisuals.classList.add("hidden");
  }

  if (video.caption) {
    scriptCaption.value = video.caption;
  }
}

function showRenderedScenesStrip(sceneImages) {
  renderedScenesStrip.innerHTML = "";
  
  const validScenes = sceneImages.filter(s => s.url);
  if (validScenes.length === 0) {
    renderedScenesStrip.classList.add("hidden");
    return;
  }
  
  renderedScenesStrip.classList.remove("hidden");
  
  validScenes.forEach(scene => {
    const thumb = document.createElement("div");
    thumb.className = "rendered-scene-thumb";
    thumb.innerHTML = `<img src="${scene.url}" alt="Scene ${scene.scene}">`;
    thumb.addEventListener("click", () => openSceneLightbox(scene.url));
    renderedScenesStrip.appendChild(thumb);
  });
}

function setupMultiVideoSwitcher(videos) {
  multiVideoSelector.innerHTML = "";
  if (videos.length <= 1) {
    multiVideoSelector.classList.add("hidden");
    return;
  }

  multiVideoSelector.classList.remove("hidden");
  videos.forEach((v, idx) => {
    const btn = document.createElement("button");
    btn.className = `btn btn-sm btn-outline ${idx === 0 ? "active" : ""}`;
    btn.textContent = `Part ${v.part}`;
    btn.addEventListener("click", () => {
      appState.currentVideoIndex = idx;
      updateVideoPlayer(v);
      document.querySelectorAll("#multi-video-selector button").forEach((b, i) => {
        b.classList.toggle("active", i === idx);
      });
      
      // Update scene strip for this part
      if (v.scene_images && v.scene_images.length > 0) {
        showRenderedScenesStrip(v.scene_images);
      }
    });
    multiVideoSelector.appendChild(btn);
  });
}

// Publish to Instagram
async function handlePublishInstagram() {
  const currentVideo = appState.renderedVideos[appState.currentVideoIndex] || {
    filename: "reel_1792479772.mp4",
    caption: scriptCaption.value
  };

  btnPublishInstagram.disabled = true;
  btnPublishInstagram.innerHTML = `<span class="btn-icon">⏳</span> Publishing to Instagram...`;

  try {
    const res = await fetch("/api/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: currentVideo.filename,
        caption: scriptCaption.value
      })
    });
    const result = await res.json();

    if (result.success) {
      if (result.mode === "live") {
        showToast("🚀 Reel published live to Instagram!");
      } else {
        showToast("✅ Reel queued! (Add Meta API Token in Settings to post directly to your live account)");
      }
      loadHistory();
    } else {
      showToast("Publish status: " + (result.error || "Failed to publish"));
    }
  } catch (err) {
    showToast("Publish error: " + err.message);
  } finally {
    btnPublishInstagram.disabled = false;
    btnPublishInstagram.innerHTML = `<span class="btn-icon">🚀</span> Post to Instagram Reels`;
  }
}

// Load Post History
async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    historyTbody.innerHTML = "";

    const list = data.history || [];
    if (list.length === 0) {
      historyTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-subtle);">No reels generated yet. Click 'Generate Script' and 'Render Video' above!</td></tr>`;
      return;
    }

    list.forEach(item => {
      const tr = document.createElement("tr");
      const isLive = item.status === "Published Live";
      const statusClass = isLive ? "published" : "queued";
      const captionPreview = (item.caption || "").slice(0, 55) + "...";

      tr.innerHTML = `
        <td style="color: var(--text-muted); font-size: 0.78rem;">${item.timestamp || "Just now"}</td>
        <td><code>${item.filename || ""}</code></td>
        <td style="color: var(--text-muted);">${captionPreview}</td>
        <td><span class="status-badge ${statusClass}">${item.status || "Ready"}</span></td>
        <td>
          <a href="/media/videos/${item.filename}" target="_blank" class="btn btn-sm btn-outline">▶ Play</a>
        </td>
      `;
      historyTbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

// Autopilot Management
async function loadAutopilotStatus() {
  try {
    const res = await fetch("/api/autopilot");
    const data = await res.json();
    
    autopilotEnableSwitch.checked = data.is_active;
    autopilotInterval.value = data.interval_hours || 12;
    if (data.niche) autopilotNiche.value = data.niche;

    autopilotBadge.textContent = data.is_active ? "ON" : "OFF";
    autopilotBadge.classList.toggle("active", data.is_active);

    autoStatusText.textContent = data.is_active ? "🟢 Running in background" : "⚪ Disabled";
    autoNextRun.textContent = data.next_run || "None";
    autoTotalCount.textContent = data.total_generated || 0;
  } catch (err) {
    console.error("Failed to load autopilot status:", err);
  }
}

async function handleSaveAutopilot() {
  const payload = {
    enabled: autopilotEnableSwitch.checked,
    interval_hours: parseInt(autopilotInterval.value, 10),
    niche: autopilotNiche.value,
    voice: appState.selectedVoice,
    is_multipart: appState.format === "multi"
  };

  try {
    const res = await fetch("/api/autopilot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      showToast(payload.enabled ? "🤖 Autopilot enabled! Generating reels automatically on schedule." : "Autopilot disabled.");
      modalAutopilot.classList.add("hidden");
      loadAutopilotStatus();
    }
  } catch (err) {
    showToast("Failed to save autopilot: " + err.message);
  }
}

// Settings Management
async function loadSettings() {
  try {
    const res = await fetch("/api/settings");
    const data = await res.json();
    if (data.image_provider && setImageProvider) {
      setImageProvider.value = data.image_provider;
    }
    if (data.has_openai_key && setOpenaiKey) {
      setOpenaiKey.placeholder = "sk-•••••••••••••••• (API Key Configured)";
    }
    if (data.instagram && data.instagram.account_id && setIgAccount) {
      setIgAccount.value = data.instagram.account_id;
    }
  } catch (err) {
    console.error("Failed to load settings:", err);
  }
}

async function handleSaveSettings() {
  btnSaveSettings.disabled = true;
  btnSaveSettings.textContent = "Saving...";

  const payload = {
    image_provider: setImageProvider ? setImageProvider.value : "openai",
    openai_api_key: setOpenaiKey && setOpenaiKey.value.trim() ? setOpenaiKey.value.trim() : null,
    instagram_account_id: setIgAccount ? setIgAccount.value.trim() : null,
    instagram_access_token: setIgToken ? setIgToken.value.trim() : null
  };

  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      showToast("Settings saved to studio environment! ⚙️✨");
      modalSettings.classList.add("hidden");
      await loadSettings();
    } else {
      showToast("Error saving settings: " + (result.detail || "Unknown error"));
    }
  } catch (err) {
    showToast("Failed to save settings: " + err.message);
  } finally {
    btnSaveSettings.disabled = false;
    btnSaveSettings.textContent = "Save Settings";
  }
}

// Toast Helper
function showToast(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4500);
}

// Launch on DOM ready
document.addEventListener("DOMContentLoaded", init);
