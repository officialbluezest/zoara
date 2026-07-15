const API = "/api";
let STATE = {
  brandId: localStorage.getItem("zoara_brand_id") || null,
  brand: null,
  formats: [],
  platforms: [],
  strategyQuestions: [],
  currentRoom: "hooks",
  selectedFormatsForBuild: [],
  researchPollTimer: null,
};

const ROOMS = [
  { id: "hooks", label: "Hooks & Openers" },
  { id: "visual_style", label: "Visual Style" },
  { id: "storytelling", label: "Storytelling / Structure" },
  { id: "offers_ctas", label: "Offers & CTAs" },
  { id: "tone_personality", label: "Tone & Personality" },
];

// ---------------- Utility ----------------

function showConnBanner(msg) {
  let el = document.getElementById("connBanner");
  if (!el) {
    el = document.createElement("div");
    el.id = "connBanner";
    el.style.cssText = "position:fixed;top:0;left:0;right:0;background:#FFF6E0;color:#8A5D00;text-align:center;padding:8px;font-size:13px;font-weight:600;z-index:200;border-bottom:1px solid #E6A800;";
    document.body.prepend(el);
  }
  el.textContent = msg;
  el.style.display = "block";
}
function hideConnBanner() {
  const el = document.getElementById("connBanner");
  if (el) el.style.display = "none";
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

// Retries on network failure / cold-start-style errors (502/503/504) with
// backoff, since Render's free tier can take 20-60s to wake from sleep.
async function api(path, opts = {}, attempt = 1) {
  const MAX_ATTEMPTS = 5;
  try {
    const res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if ([502, 503, 504].includes(res.status) && attempt < MAX_ATTEMPTS) {
      showConnBanner("Waking up Zoara's server — this can take up to a minute on the free tier...");
      await sleep(attempt * 2000);
      return api(path, opts, attempt + 1);
    }
    hideConnBanner();
    if (!res.ok) {
      let msg = res.statusText;
      try { const j = await res.json(); msg = j.detail || msg; } catch (e) {}
      throw new Error(msg);
    }
    return res.json();
  } catch (err) {
    if (attempt < MAX_ATTEMPTS) {
      showConnBanner("Waking up Zoara's server — this can take up to a minute on the free tier...");
      await sleep(attempt * 2000);
      return api(path, opts, attempt + 1);
    }
    hideConnBanner();
    throw err;
  }
}

// Runs a render/load function without letting its failure block any other
// tab from loading — each section fails independently. If a containerId is
// given and the section fails, it shows a visible retry link there instead
// of leaving a silent blank tab.
async function safeRun(fn, label, containerId) {
  try {
    await fn();
  } catch (err) {
    console.error(`Zoara: "${label}" failed to load:`, err);
    if (containerId) {
      const el = document.getElementById(containerId);
      if (el) {
        el.innerHTML = `<p class="hint" style="color:var(--danger);">Couldn't load ${esc(label)} (${esc(err.message || "connection issue")}).
          <a href="#" data-retry style="color:var(--navy);font-weight:600;">Retry</a></p>`;
        const retryLink = el.querySelector("[data-retry]");
        if (retryLink) retryLink.onclick = (e) => { e.preventDefault(); safeRun(fn, label, containerId); };
      }
    }
  }
}

function setStatus(elId, msg, type = "") {
  const el = document.getElementById(elId);
  el.textContent = msg;
  el.className = "status-line" + (type ? " " + type : "");
}

function esc(str) {
  return (str || "").toString().replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// ---------------- Tabs ----------------

function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
  });
}

// ---------------- Brand management ----------------

async function loadBrandList() {
  const brands = await api("/brands");
  const sel = document.getElementById("brandSelector");
  sel.innerHTML = "";
  if (brands.length === 0) {
    sel.innerHTML = `<option value="">No brands yet — create one</option>`;
    return;
  }
  brands.forEach((b) => {
    const opt = document.createElement("option");
    opt.value = b.id;
    opt.textContent = b.name;
    sel.appendChild(opt);
  });
  if (STATE.brandId && brands.find((b) => b.id === STATE.brandId)) {
    sel.value = STATE.brandId;
  } else {
    STATE.brandId = brands[0].id;
    localStorage.setItem("zoara_brand_id", STATE.brandId);
    sel.value = STATE.brandId;
  }
  sel.onchange = () => {
    STATE.brandId = sel.value;
    localStorage.setItem("zoara_brand_id", STATE.brandId);
    loadEverythingForBrand();
  };
}

function openModal(id) { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }

function wireNewBrandModal() {
  document.getElementById("newBrandBtn").onclick = () => openModal("newBrandModal");
  document.getElementById("cancelNewBrand").onclick = () => closeModal("newBrandModal");
  document.getElementById("confirmNewBrand").onclick = async () => {
    const name = document.getElementById("newBrandNameInput").value.trim();
    if (!name) return;
    const brand = await api("/brands", { method: "POST", body: JSON.stringify({ name }) });
    STATE.brandId = brand.id;
    localStorage.setItem("zoara_brand_id", brand.id);
    document.getElementById("newBrandNameInput").value = "";
    closeModal("newBrandModal");
    await loadBrandList();
    await loadEverythingForBrand();
  };
}

function wireReadinessModal() {
  document.getElementById("readinessBtn").onclick = async () => {
    if (!STATE.brandId) return;
    const result = await api(`/brands/${STATE.brandId}/completeness`);
    const area = document.getElementById("readinessResult");
    if (result.complete) {
      area.innerHTML = `<div class="complete-banner">✓ Everything required is filled in. You're ready to run research and generate content.</div>`;
    } else {
      area.innerHTML = `<p>A few required things are still missing:</p><ul class="missing-list">${result.missing
        .map((m) => `<li>${esc(m)}</li>`)
        .join("")}</ul>`;
    }
    openModal("readinessModal");
  };
  document.getElementById("closeReadinessModal").onclick = () => closeModal("readinessModal");
}

// ---------------- Tab 1: Strategy ----------------

async function renderStrategyQuestions() {
  if (!STATE.strategyQuestions || !STATE.strategyQuestions.length) {
    STATE.strategyQuestions = await api("/meta/strategy-questions");
  }
  const container = document.getElementById("strategyQuestionsList");
  const answers = (STATE.brand && STATE.brand.strategy_answers) || {};
  const required = ["offer", "transformation", "anti_audience", "business_goal"];
  container.innerHTML = STATE.strategyQuestions
    .map(
      (q) => `
    <div class="q-item">
      <div class="q-question">${esc(q.question)}${required.includes(q.id) ? '<span class="q-required-star">*</span>' : ""}</div>
      <div class="q-why">${esc(q.why)}</div>
      <textarea class="text-area" data-qid="${q.id}" rows="2">${esc(answers[q.id] || "")}</textarea>
    </div>`
    )
    .join("");
}

function wireStrategyTab() {
  document.getElementById("saveBrandNameBtn").onclick = async () => {
    const name = document.getElementById("brandNameInput").value.trim();
    if (!name || !STATE.brandId) return;
    await api(`/brands/${STATE.brandId}`, { method: "PATCH", body: JSON.stringify({ name }) });
    await loadBrandList();
    setStatus("docUploadStatus", "");
  };

  document.getElementById("uploadDocBtn").onclick = async () => {
    const fileInput = document.getElementById("strategyDocInput");
    if (!fileInput.files.length || !STATE.brandId) {
      setStatus("docUploadStatus", "Choose a file first.", "error");
      return;
    }
    setStatus("docUploadStatus", "Reading and analyzing your document...");
    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    try {
      const res = await fetch(`${API}/brands/${STATE.brandId}/strategy-doc`, { method: "POST", body: fd });
      if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
      STATE.brand = await res.json();
      renderStrategyQuestions();
      setStatus("docUploadStatus", "Document analyzed — answers below were pre-filled where possible.", "success");
    } catch (e) {
      setStatus("docUploadStatus", e.message, "error");
    }
  };

  document.getElementById("saveStrategyBtn").onclick = async () => {
    const answers = {};
    document.querySelectorAll("#strategyQuestionsList textarea").forEach((t) => {
      answers[t.dataset.qid] = t.value;
    });
    const merged = { ...(STATE.brand.strategy_answers || {}), ...answers };
    STATE.brand = await api(`/brands/${STATE.brandId}`, {
      method: "PATCH",
      body: JSON.stringify({ strategy_answers: merged }),
    });
    setStatus("strategySaveStatus", "Saved.", "success");
  };
}

// ---------------- Tab 2: Competitors ----------------

async function loadCompetitors() {
  const list = await api(`/brands/${STATE.brandId}/competitors`);
  const el = document.getElementById("competitorsList");
  if (!list.length) {
    el.innerHTML = `<p class="hint">No competitors added yet.</p>`;
    return;
  }
  el.innerHTML = list
    .map(
      (c) => `
    <div class="item-card">
      <div class="item-title">${esc(c.label || c.url)}</div>
      <div class="item-meta">${esc(c.url)} · <span class="tag ${c.status === "analyzed" ? "approved" : c.status === "failed" ? "rejected" : ""}">${esc(c.status)}</span></div>
      <div class="item-body">${esc(c.extracted_summary || "(no summary yet)")}</div>
    </div>`
    )
    .join("");
}

function wireCompetitorsTab() {
  document.getElementById("addCompetitorBtn").onclick = async () => {
    const url = document.getElementById("competitorUrlInput").value.trim();
    const label = document.getElementById("competitorLabelInput").value.trim();
    if (!url) return;
    setStatus("competitorAddStatus", "Reading and summarizing...");
    try {
      await api(`/brands/${STATE.brandId}/competitors`, { method: "POST", body: JSON.stringify({ url, label }) });
      document.getElementById("competitorUrlInput").value = "";
      document.getElementById("competitorLabelInput").value = "";
      setStatus("competitorAddStatus", "Added.", "success");
      await loadCompetitors();
    } catch (e) {
      setStatus("competitorAddStatus", e.message, "error");
    }
  };
}

// ---------------- Tab 3: Format & Platform ----------------

async function renderFormatPlatformPills() {
  if (!STATE.formats || !STATE.formats.length) STATE.formats = await api("/meta/formats");
  if (!STATE.platforms || !STATE.platforms.length) STATE.platforms = await api("/meta/platforms");
  const selectedFormats = new Set((STATE.brand && STATE.brand.formats) || []);
  const selectedPlatforms = new Set((STATE.brand && STATE.brand.platforms) || []);

  document.getElementById("formatPills").innerHTML = STATE.formats
    .map(
      (f) => `<button class="pill ${selectedFormats.has(f.id) ? "selected" : ""}" data-format="${f.id}">${esc(f.name)}</button>`
    )
    .join("");
  document.getElementById("platformPills").innerHTML = STATE.platforms
    .map(
      (p) => `<button class="pill ${selectedPlatforms.has(p.id) ? "selected" : ""}" data-platform="${p.id}">${esc(p.name)}</button>`
    )
    .join("");

  document.querySelectorAll("#formatPills .pill").forEach((btn) => {
    btn.onclick = () => btn.classList.toggle("selected");
  });
  document.querySelectorAll("#platformPills .pill").forEach((btn) => {
    btn.onclick = () => btn.classList.toggle("selected");
  });
}

function wireFormatPlatformTab() {
  document.getElementById("saveFormatsPlatformsBtn").onclick = async () => {
    const formats = [...document.querySelectorAll("#formatPills .pill.selected")].map((b) => b.dataset.format);
    const platforms = [...document.querySelectorAll("#platformPills .pill.selected")].map((b) => b.dataset.platform);
    STATE.brand = await api(`/brands/${STATE.brandId}`, {
      method: "PATCH",
      body: JSON.stringify({ formats, platforms }),
    });
    setStatus("formatsPlatformsStatus", "Saved. Inspiration, Build & Length, and Content Studio are now conditioned on this.", "success");
    renderInspoDropdowns();
    renderBuildSpecArea();
    populateGenSelectors();
  };
}

// ---------------- Tab 4: Inspiration ----------------

function renderRoomTabs() {
  document.getElementById("roomTabs").innerHTML = ROOMS.map(
    (r) => `<button class="room-tab-btn ${r.id === STATE.currentRoom ? "active" : ""}" data-room="${r.id}">${esc(r.label)}</button>`
  ).join("");
  document.querySelectorAll(".room-tab-btn").forEach((btn) => {
    btn.onclick = () => {
      STATE.currentRoom = btn.dataset.room;
      renderRoomTabs();
      renderInspoDropdowns();
      loadInspoList();
    };
  });
}

async function renderInspoDropdowns() {
  const area = document.getElementById("inspoDropdownArea");
  const formats = (STATE.brand && STATE.brand.formats) || [];
  if (!formats.length) {
    area.innerHTML = `<p class="hint">Select at least one format in Tab 3 to unlock format-specific dropdown guides here.</p>`;
    return;
  }
  // pull dropdown option sets from each selected format's module, relevant to current room
  const roomToKey = { hooks: "hooks", storytelling: "storytelling_frameworks", offers_ctas: "ctas" };
  const relevantKey = roomToKey[STATE.currentRoom];
  let html = "";
  for (const fid of formats) {
    const fmt = await api(`/meta/formats/${fid}`);
    const dd = fmt.inspiration_dropdowns || {};
    if (relevantKey && dd[relevantKey]) {
      html += `<label class="field-label">${esc(fmt.name)} — ${STATE.currentRoom === "hooks" ? "hook types" : STATE.currentRoom === "storytelling" ? "storytelling frameworks" : "CTA types"}</label>
        <select class="text-input inspo-tag-select" data-format="${fid}" style="margin-bottom:12px;">
          <option value="">— none selected —</option>
          ${dd[relevantKey].map((opt) => `<option value="${esc(opt)}">${esc(opt)}</option>`).join("")}
        </select>`;
    }
    if (dd.extra) {
      html += `<label class="field-label">${esc(fmt.name)} — ${esc(dd.extra.label)}</label>
        <select class="text-input inspo-tag-select" data-format="${fid}" style="margin-bottom:12px;">
          <option value="">— none selected —</option>
          ${dd.extra.options.map((opt) => `<option value="${esc(opt)}">${esc(opt)}</option>`).join("")}
        </select>`;
    }
  }
  area.innerHTML = html || `<p class="hint">No specific dropdown guide for this room with the current formats — just add the link and your note below.</p>`;
}

async function loadInspoList() {
  const list = await api(`/brands/${STATE.brandId}/inspo?room=${STATE.currentRoom}`);
  const el = document.getElementById("inspoList");
  if (!list.length) {
    el.innerHTML = `<p class="hint">Nothing added to this room yet.</p>`;
    return;
  }
  el.innerHTML = list
    .map(
      (i) => `
    <div class="item-card">
      <div class="item-title"><a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(i.url)}</a></div>
      <div class="item-meta"><span class="tag ${i.status === "analyzed" ? "approved" : i.status === "manual_needed" ? "rejected" : ""}">${esc(i.status)}</span></div>
      <div class="item-body"><strong>You liked:</strong> ${esc(i.user_note)}</div>
      ${i.extracted_pattern ? `<div class="item-body" style="margin-top:6px;"><strong>Zoara's takeaway:</strong> ${esc(i.extracted_pattern)}</div>` : ""}
    </div>`
    )
    .join("");
}

function wireInspoTab() {
  document.getElementById("addInspoBtn").onclick = async () => {
    const url = document.getElementById("inspoUrlInput").value.trim();
    let note = document.getElementById("inspoNoteInput").value.trim();
    if (!url || !note) {
      setStatus("inspoAddStatus", "A link and your reason for liking it are both required.", "error");
      return;
    }
    // fold any dropdown tag selections into the note for context
    const tags = [...document.querySelectorAll(".inspo-tag-select")]
      .filter((s) => s.value)
      .map((s) => `[${s.value}]`)
      .join(" ");
    if (tags) note = `${tags} ${note}`;

    setStatus("inspoAddStatus", "Reading the link and extracting the pattern...");
    try {
      await api(`/brands/${STATE.brandId}/inspo`, {
        method: "POST",
        body: JSON.stringify({ room: STATE.currentRoom, url, user_note: note }),
      });
      document.getElementById("inspoUrlInput").value = "";
      document.getElementById("inspoNoteInput").value = "";
      setStatus("inspoAddStatus", "Added.", "success");
      await loadInspoList();
    } catch (e) {
      setStatus("inspoAddStatus", e.message, "error");
    }
  };
}

// ---------------- Tab 5: Goals ----------------

const GOAL_OPTIONS = [
  { id: "awareness", label: "Awareness" },
  { id: "leads", label: "Lead Gen" },
  { id: "sales", label: "Sales / Conversion" },
  { id: "authority", label: "Authority / Trust" },
  { id: "community", label: "Community / Engagement" },
];
const PERIOD_OPTIONS = [
  { id: "1_week", label: "1 week" },
  { id: "2_weeks", label: "2 weeks" },
  { id: "1_month", label: "1 month" },
  { id: "custom", label: "Custom" },
];

function renderGoalsTab() {
  const goals = (STATE.brand && STATE.brand.goals) || {};
  document.getElementById("goalPills").innerHTML = GOAL_OPTIONS.map(
    (g) => `<button class="pill ${goals.primary_goal === g.id ? "selected" : ""}" data-goal="${g.id}">${esc(g.label)}</button>`
  ).join("");
  document.getElementById("periodPills").innerHTML = PERIOD_OPTIONS.map(
    (p) => `<button class="pill ${goals.calendar_period === p.id ? "selected" : ""}" data-period="${p.id}">${esc(p.label)}</button>`
  ).join("");

  document.querySelectorAll("#goalPills .pill").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll("#goalPills .pill").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
    };
  });
  document.querySelectorAll("#periodPills .pill").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll("#periodPills .pill").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
    };
  });
}

function wireGoalsTab() {
  document.getElementById("saveGoalsBtn").onclick = async () => {
    const goalBtn = document.querySelector("#goalPills .pill.selected");
    const periodBtn = document.querySelector("#periodPills .pill.selected");
    const goals = {
      primary_goal: goalBtn ? goalBtn.dataset.goal : "",
      calendar_period: periodBtn ? periodBtn.dataset.period : "",
    };
    STATE.brand = await api(`/brands/${STATE.brandId}`, { method: "PATCH", body: JSON.stringify({ goals }) });
    setStatus("goalsStatus", "Saved.", "success");
  };
}

// ---------------- Tab 6: Build & Length ----------------

async function renderBuildSpecArea() {
  const area = document.getElementById("buildSpecArea");
  const formats = (STATE.brand && STATE.brand.formats) || [];
  const existing = (STATE.brand && STATE.brand.build_specs) || {};
  if (!formats.length) {
    area.innerHTML = `<p class="hint">Select formats in Tab 3 first — length and build options are entirely format-specific.</p>`;
    return;
  }
  let html = "";
  for (const fid of formats) {
    const fmt = await api(`/meta/formats/${fid}`);
    const spec = existing[fid] || {};
    html += `<div class="card" data-buildcard="${fid}">
      <label class="field-label">${esc(fmt.name)} — length</label>
      <div class="pill-grid build-length-pills" data-format="${fid}">
        ${fmt.length_options
          .map(
            (o) =>
              `<button class="pill ${spec.length === o.value ? "selected" : ""}" data-length="${esc(o.value)}">${esc(o.label)}</button>`
          )
          .join("")}
      </div>`;
    if (fmt.inspiration_dropdowns && fmt.inspiration_dropdowns.extra) {
      const extra = fmt.inspiration_dropdowns.extra;
      html += `<label class="field-label" style="margin-top:12px;">${esc(extra.label)}</label>
      <select class="text-input build-extra-select" data-format="${fid}">
        <option value="">— none —</option>
        ${extra.options.map((o) => `<option value="${esc(o)}" ${spec.extra === o ? "selected" : ""}>${esc(o)}</option>`).join("")}
      </select>`;
    }
    html += `</div>`;
  }
  area.innerHTML = html;
  document.querySelectorAll(".build-length-pills .pill").forEach((btn) => {
    btn.onclick = () => {
      btn.parentElement.querySelectorAll(".pill").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
    };
  });
}

function wireBuildTab() {
  document.getElementById("saveBuildSpecBtn").onclick = async () => {
    const build_specs = {};
    document.querySelectorAll("[data-buildcard]").forEach((card) => {
      const fid = card.dataset.buildcard;
      const lengthBtn = card.querySelector(".build-length-pills .pill.selected");
      const extraSel = card.querySelector(".build-extra-select");
      build_specs[fid] = {
        length: lengthBtn ? lengthBtn.dataset.length : "",
        extra: extraSel ? extraSel.value : "",
      };
    });
    STATE.brand = await api(`/brands/${STATE.brandId}`, { method: "PATCH", body: JSON.stringify({ build_specs }) });
    setStatus("buildSpecStatus", "Saved.", "success");
  };
}

// ---------------- Tab 7: Creative Angle ----------------

function renderAngleTab() {
  const angle = (STATE.brand && STATE.brand.creative_angles) || {};
  document.querySelectorAll("#anglePills .pill").forEach((btn) => {
    btn.classList.toggle("selected", btn.dataset.angle === angle.structure);
  });
  document.getElementById("angleNameInput").value = angle.name || "";
}

function wireAngleTab() {
  document.querySelectorAll("#anglePills .pill").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll("#anglePills .pill").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
    };
  });
  document.getElementById("saveAngleBtn").onclick = async () => {
    const sel = document.querySelector("#anglePills .pill.selected");
    const creative_angles = {
      structure: sel ? sel.dataset.angle : "standalone",
      name: document.getElementById("angleNameInput").value.trim(),
    };
    STATE.brand = await api(`/brands/${STATE.brandId}`, { method: "PATCH", body: JSON.stringify({ creative_angles }) });
    setStatus("angleStatus", "Saved.", "success");
  };
}

// ---------------- Tab 8: Research ----------------

function wireResearchTab() {
  document.getElementById("startResearchBtn").onclick = async () => {
    const result = await api(`/brands/${STATE.brandId}/research/start`, {
      method: "POST",
      body: JSON.stringify({ count: 30 }),
    });
    setStatus("researchJobStatus", "Running in the background — feel free to switch tabs.", "");
    pollResearchJob(result.job_id);
  };

  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      loadIdeas(btn.dataset.status);
    };
  });
}

function pollResearchJob(jobId) {
  if (STATE.researchPollTimer) clearInterval(STATE.researchPollTimer);
  STATE.researchPollTimer = setInterval(async () => {
    const job = await api(`/brands/${STATE.brandId}/research/status/${jobId}`);
    if (job.status === "complete") {
      clearInterval(STATE.researchPollTimer);
      setStatus("researchJobStatus", "Research complete — 30 ideas ready below.", "success");
      loadIdeas("");
      populateGenSelectors();
    } else if (job.status === "failed") {
      clearInterval(STATE.researchPollTimer);
      setStatus("researchJobStatus", "Research failed: " + job.error, "error");
    }
  }, 3000);
}

async function loadIdeas(status) {
  const q = status ? `?status=${status}` : "";
  const ideas = await api(`/brands/${STATE.brandId}/research/ideas${q}`);
  const el = document.getElementById("ideasList");
  if (!ideas.length) {
    el.innerHTML = `<p class="hint">No ideas yet — run research above.</p>`;
    return;
  }
  el.innerHTML = ideas
    .map(
      (idea) => `
    <div class="item-card" data-idea="${idea.id}">
      <div class="item-title">${esc(idea.topic)}</div>
      <div class="item-meta"><span class="tag ${idea.status === "approved" ? "approved" : idea.status === "rejected" ? "rejected" : ""}">${esc(idea.status)}</span> · Source: ${esc(idea.source_pattern)}</div>
      <div class="item-body">${esc(idea.suggested_angle)}</div>
      ${idea.tweak_comment ? `<div class="item-body" style="margin-top:6px;"><strong>Tweak note:</strong> ${esc(idea.tweak_comment)}</div>` : ""}
      <div class="item-actions">
        <button class="btn btn-small btn-success" data-action="approve">✅ Approve</button>
        <button class="btn btn-small btn-danger" data-action="reject">❌ Reject</button>
        <button class="btn btn-small btn-ghost" data-action="tweak" style="color:var(--navy);border-color:var(--border);">✏️ Tweak</button>
      </div>
    </div>`
    )
    .join("");

  el.querySelectorAll(".item-card").forEach((card) => {
    const ideaId = card.dataset.idea;
    card.querySelector('[data-action="approve"]').onclick = () => updateIdea(ideaId, "approved");
    card.querySelector('[data-action="reject"]').onclick = () => updateIdea(ideaId, "rejected");
    card.querySelector('[data-action="tweak"]').onclick = () => {
      const comment = prompt("What should change about this idea?");
      if (comment !== null) updateIdea(ideaId, "tweaked", comment);
    };
  });
}

async function updateIdea(ideaId, status, tweak_comment = "") {
  await api(`/brands/${STATE.brandId}/research/ideas/${ideaId}`, {
    method: "PATCH",
    body: JSON.stringify({ status, tweak_comment }),
  });
  const activeFilter = document.querySelector(".filter-btn.active").dataset.status;
  loadIdeas(activeFilter);
  populateGenSelectors();
}

// ---------------- Tab 9: Content Studio ----------------

async function populateGenSelectors() {
  const ideaSel = document.getElementById("ideaSourceSelect");
  const approved = await api(`/brands/${STATE.brandId}/research/ideas?status=approved`).catch(() => []);
  ideaSel.innerHTML =
    `<option value="manual">— Type a manual topic —</option>` +
    approved.map((i) => `<option value="${i.id}">${esc(i.topic)}</option>`).join("");
  ideaSel.onchange = () => {
    document.getElementById("manualTopicInput").style.display = ideaSel.value === "manual" ? "block" : "none";
  };

  const formats = (STATE.brand && STATE.brand.formats) || [];
  const platforms = (STATE.brand && STATE.brand.platforms) || [];
  const fSel = document.getElementById("genFormatSelect");
  const pSel = document.getElementById("genPlatformSelect");
  fSel.innerHTML = formats.map((fid) => {
    const f = STATE.formats.find((x) => x.id === fid);
    return `<option value="${fid}">${esc(f ? f.name : fid)}</option>`;
  }).join("") || `<option value="">Select formats in Tab 3</option>`;
  pSel.innerHTML = platforms.map((pid) => {
    const p = STATE.platforms.find((x) => x.id === pid);
    return `<option value="${pid}">${esc(p ? p.name : pid)}</option>`;
  }).join("") || `<option value="">Select platforms in Tab 3</option>`;
}

function wireStudioTab() {
  document.getElementById("generateBtn").onclick = async () => {
    const ideaSel = document.getElementById("ideaSourceSelect");
    const format_id = document.getElementById("genFormatSelect").value;
    const platform_id = document.getElementById("genPlatformSelect").value;
    if (!format_id || !platform_id) {
      setStatus("generateStatus", "Pick a format and platform (set them in Tab 3 first).", "error");
      return;
    }
    const build_spec = ((STATE.brand.build_specs || {})[format_id]) || {};
    const creative_angle = STATE.brand.creative_angles && STATE.brand.creative_angles.structure !== "standalone"
      ? `${STATE.brand.creative_angles.structure}: ${STATE.brand.creative_angles.name || ""}` : "";

    const payload = { brand_id: STATE.brandId, format_id, platform_id, build_spec, creative_angle };
    if (ideaSel.value === "manual") {
      const manual = document.getElementById("manualTopicInput").value.trim();
      if (!manual) { setStatus("generateStatus", "Type a manual topic or pick an approved idea.", "error"); return; }
      payload.manual_topic = manual;
    } else {
      payload.research_idea_id = ideaSel.value;
    }

    setStatus("generateStatus", "Zoara is writing...");
    try {
      await api("/content/generate", { method: "POST", body: JSON.stringify(payload) });
      setStatus("generateStatus", "Generated.", "success");
      loadContentList();
    } catch (e) {
      setStatus("generateStatus", e.message, "error");
    }
  };
}

async function loadContentList() {
  const items = await api(`/content?brand_id=${STATE.brandId}`);
  const el = document.getElementById("contentList");
  if (!items.length) {
    el.innerHTML = `<p class="hint">Nothing generated yet.</p>`;
    return;
  }
  el.innerHTML = "";
  for (const item of items) {
    el.appendChild(await renderContentCard(item));
  }
}

async function renderContentCard(item) {
  const div = document.createElement("div");
  div.className = "content-card";
  const critiques = await api(`/content/${item.id}/critiques`).catch(() => []);
  const latest = critiques[0];

  div.innerHTML = `
    <div class="content-card-header">
      <div>
        <div class="item-title">${esc(item.title || "Untitled")}</div>
        <div class="item-meta">${esc(item.format)} · ${esc(item.platform)} · v${item.version} · ${esc(item.status)}</div>
      </div>
    </div>
    <div class="content-text">${esc(item.raw_text)}</div>
    <div class="edit-row">
      <input type="text" class="text-input edit-comment-input" placeholder="Edit instruction, e.g. 'make the hook punchier'">
      <button class="btn btn-small btn-primary" data-action="revise">Edit</button>
      <button class="btn btn-small btn-ghost" data-action="repurpose" style="color:var(--navy);border-color:var(--border);">Repurpose</button>
      <button class="btn btn-small btn-accent" data-action="critique">Critique</button>
    </div>
    <div class="critique-box" data-critique-box></div>
  `;

  if (latest) renderCritique(div.querySelector("[data-critique-box]"), item, latest);

  div.querySelector('[data-action="revise"]').onclick = async () => {
    const comment = div.querySelector(".edit-comment-input").value.trim();
    if (!comment) return;
    await api(`/content/${item.id}/revise`, { method: "POST", body: JSON.stringify({ edit_comment: comment }) });
    loadContentList();
  };

  div.querySelector('[data-action="repurpose"]').onclick = async () => {
    const formats = (STATE.brand.formats || []);
    const platforms = (STATE.brand.platforms || []);
    const targetFormat = prompt("Repurpose to which format id?\n" + formats.join(", "), item.format);
    if (!targetFormat) return;
    const targetPlatform = prompt("Repurpose to which platform id?\n" + platforms.join(", "), item.platform);
    if (!targetPlatform) return;
    await api(`/content/${item.id}/repurpose`, {
      method: "POST",
      body: JSON.stringify({ target_format_id: targetFormat, target_platform_id: targetPlatform }),
    });
    loadContentList();
  };

  div.querySelector('[data-action="critique"]').onclick = async () => {
    const goal = (STATE.brand.goals || {}).primary_goal || "";
    const result = await api(`/content/${item.id}/critique`, { method: "POST", body: JSON.stringify({ goal }) });
    renderCritique(div.querySelector("[data-critique-box]"), item, result);
  };

  return div;
}

function renderCritique(box, item, c) {
  const passClass = c.passed_cutoff ? "score-pass" : "score-fail";
  box.innerHTML = `
    <div class="score-row">
      <div class="score-pill ${passClass}">Overall: ${c.overall_score}/10 ${c.passed_cutoff ? "✓ Passes 7.0 bar" : "— below 7.0 bar"}</div>
      <div class="score-pill">Strategist: ${c.strategist_score}/10</div>
      <div class="score-pill">Customer: ${c.customer_score}/10</div>
    </div>
    <div class="perspective"><div class="perspective-label">Strategist perspective</div>${esc(c.strategist_feedback)}</div>
    <div class="perspective"><div class="perspective-label">Ideal customer perspective</div>${esc(c.customer_feedback)}</div>
    <div class="improvement-box"><strong>${c.passed_cutoff ? "Polish idea" : "What would push this above 7.0"}:</strong> ${esc(c.improvement_notes)}</div>
    <div class="edit-row" style="margin-top:10px;">
      <input type="text" class="text-input critique-comment-input" placeholder="Leave a comment for the record...">
      <button class="btn btn-small btn-primary" data-action="comment-critique">Save comment</button>
    </div>
  `;
  box.querySelector('[data-action="comment-critique"]').onclick = async () => {
    const comment = box.querySelector(".critique-comment-input").value.trim();
    if (!comment) return;
    await api(`/content/critiques/${c.id}/comment`, { method: "POST", body: JSON.stringify({ comment }) });
    box.querySelector(".critique-comment-input").value = "Saved ✓";
  };
}

// ---------------- Tab 10: Knowledge Panel ----------------

async function renderKnowledgePanel() {
  const kp = await api("/meta/knowledge-panel");
  const area = document.getElementById("knowledgePanelArea");
  area.innerHTML = `
    <div class="kp-section">
      <h3>Core writing principles</h3>
      <ol class="principle-list">${kp.core_writing_principles.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
    </div>
    <div class="kp-section">
      <h3>Books</h3>
      <ul class="kp-list">${kp.books.map((b) => `<li><div class="kp-title">${esc(b.title)} — ${esc(b.author)}</div><div class="kp-why">${esc(b.why)}</div></li>`).join("")}</ul>
    </div>
    <div class="kp-section">
      <h3>YouTube &amp; creators</h3>
      <ul class="kp-list">${kp.youtube_and_creators.map((y) => `<li><div class="kp-title">${esc(y.name)}</div><div class="kp-why">${esc(y.why)}</div></li>`).join("")}</ul>
    </div>
    <div class="kp-section">
      <h3>Sites &amp; communities</h3>
      <ul class="kp-list">${kp.sites_and_communities.map((s) => `<li><div class="kp-title">${esc(s.name)}</div><div class="kp-why">${esc(s.why)}</div></li>`).join("")}</ul>
    </div>
  `;
}

// ---------------- Master load ----------------

async function loadEverythingForBrand() {
  if (!STATE.brandId) return;
  try {
    STATE.brand = await api(`/brands/${STATE.brandId}`);
  } catch (err) {
    // The saved brand ID no longer exists on the server - most commonly
    // because a free-tier redeploy reset the database while this browser
    // still remembered an old brand from before. Recover instead of
    // crashing: forget the stale ID and fall back to whatever brands
    // actually exist right now.
    console.warn("Zoara: saved brand no longer exists, resetting:", err.message);
    localStorage.removeItem("zoara_brand_id");
    STATE.brandId = null;
    STATE.brand = null;
    await safeRun(() => loadBrandList(), "brand list");
    if (STATE.brandId) {
      return loadEverythingForBrand(); // retry once with whatever brand loadBrandList picked
    }
    document.getElementById("strategyQuestionsList").innerHTML =
      `<p class="hint">That brand isn't available anymore (likely a server reset) — click <strong>+ New Brand</strong> above to start fresh.</p>`;
    return;
  }
  document.getElementById("brandNameInput").value = STATE.brand.name || "";

  await safeRun(() => renderStrategyQuestions(), "strategy questions", "strategyQuestionsList");
  await safeRun(() => loadCompetitors(), "competitors", "competitorsList");
  await safeRun(() => renderFormatPlatformPills(), "format/platform pills", "formatPills");
  await safeRun(() => renderRoomTabs(), "inspiration room tabs", "roomTabs");
  await safeRun(() => renderInspoDropdowns(), "inspiration dropdowns", "inspoDropdownArea");
  await safeRun(() => loadInspoList(), "inspiration list", "inspoList");
  await safeRun(() => renderGoalsTab(), "goals", "goalPills");
  await safeRun(() => renderBuildSpecArea(), "build/length specs", "buildSpecArea");
  await safeRun(() => renderAngleTab(), "creative angle");
  await safeRun(() => loadIdeas(""), "research ideas", "ideasList");
  await safeRun(() => populateGenSelectors(), "content studio selectors");
  await safeRun(() => loadContentList(), "content list", "contentList");
}

async function init() {
  initTabs();
  wireNewBrandModal();
  wireReadinessModal();
  wireStrategyTab();
  wireCompetitorsTab();
  wireFormatPlatformTab();
  wireInspoTab();
  wireGoalsTab();
  wireBuildTab();
  wireAngleTab();
  wireResearchTab();
  wireStudioTab();

  await safeRun(async () => { STATE.formats = await api("/meta/formats"); }, "formats meta");
  await safeRun(async () => { STATE.platforms = await api("/meta/platforms"); }, "platforms meta");
  await safeRun(async () => { STATE.strategyQuestions = await api("/meta/strategy-questions"); }, "strategy questions meta");

  await safeRun(() => loadBrandList(), "brand list");
  if (STATE.brandId) {
    await safeRun(() => loadEverythingForBrand(), "brand data");
  }
  await safeRun(() => renderKnowledgePanel(), "knowledge panel");
}

document.addEventListener("DOMContentLoaded", init);
