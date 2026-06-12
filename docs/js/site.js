const FEATURED_IDS = [
  "stata-regression",
  "wrds",
  "python-panel-data",
  "econ-humanizer-plus",
  "latex-tables",
  "econ-lit-search",
  "econ-visualization",
];

const CATEGORY_SHORT = {
  "econometrics": "Econometrics",
  "data-and-visualization": "Data & viz",
  "research-tools": "Research",
  "writing-and-review": "Writing",
};

const CATEGORY_FILTER_LABELS = {
  "econometrics": "Econometrics",
  "data-and-visualization": "Data & viz",
  "research-tools": "Research",
  "writing-and-review": "Writing",
};

let catalog = null;
let activeCategory = "all";
let searchQuery = "";

function titleCase(id) {
  return id.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function descriptionNeedsClamp(text, n = 96) {
  if (!text) return false;
  return text.replace(/\s+/g, " ").trim().length > n;
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function skillSummary(skill) {
  return skill.summary || skill.description || "";
}

function skillHasDetail(skill) {
  const summary = skillSummary(skill);
  const detail = skill.description || "";
  return Boolean(detail && detail !== summary);
}

function skillDownloadUrl(skillId) {
  return `downloads/skills/${skillId}.zip`;
}

function skillCardMarkup(skill, { featured = false } = {}) {
  const tag = CATEGORY_SHORT[skill.category] || skill.category;
  const summary = skillSummary(skill);
  const hasDetail = skillHasDetail(skill);
  const clampAt = featured ? 72 : 80;
  const expandable =
    descriptionNeedsClamp(summary, clampAt) || (hasDetail && descriptionNeedsClamp(skill.description, 100));
  const descClass = expandable ? "skill-card-desc is-clamped" : "skill-card-desc";
  const detailHtml = hasDetail
    ? `<p class="skill-card-detail">${escapeHtml(skill.description)}</p>`
    : "";

  return `
    <div class="skill-card-head">
      <h3>${titleCase(skill.id)}</h3>
      <span class="category-tag category-tag--${skill.category}">${tag}</span>
    </div>
    <div class="skill-card-body">
      <p class="${descClass}">${escapeHtml(summary)}</p>
      ${detailHtml}
    </div>
    <div class="skill-card-footer">
      <a class="skill-card-download" href="${skillDownloadUrl(skill.id)}" download="${skill.id}.zip" aria-label="Download ${titleCase(skill.id)} zip">Download zip ↓</a>
    </div>
  `;
}

function applySkillCardClasses(card, skill, { featured = false } = {}) {
  const summary = skillSummary(skill);
  const hasDetail = skillHasDetail(skill);
  const clampAt = featured ? 72 : 80;
  if (descriptionNeedsClamp(summary, clampAt) || (hasDetail && descriptionNeedsClamp(skill.description, 100))) {
    card.classList.add("is-expandable");
  }
  card.dataset.category = skill.category;
}

function createSkillCard(skill, { featured = false, animationIndex = 0 } = {}) {
  const card = document.createElement("article");
  card.className = featured ? "feature-card skill-card-interactive" : "skill-card skill-card-interactive";
  card.tabIndex = 0;
  card.setAttribute("aria-label", `${titleCase(skill.id)} skill`);
  if (!featured && animationIndex > 0) {
    card.style.animationDelay = `${Math.min(animationIndex * 0.02, 0.4)}s`;
  }
  card.innerHTML = skillCardMarkup(skill, { featured });
  applySkillCardClasses(card, skill, { featured });
  return card;
}

function renderFeatured() {
  const grid = document.getElementById("featured-grid");
  grid.innerHTML = "";
  FEATURED_IDS.forEach((id) => {
    const skill = catalog.skills.find((s) => s.id === id);
    if (!skill) return;
    grid.appendChild(createSkillCard(skill, { featured: true }));
  });
}

function updateFilterAria(filters) {
  filters.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.setAttribute("aria-selected", btn.classList.contains("active") ? "true" : "false");
  });
}

function renderFilters() {
  const filters = document.getElementById("filters");
  const allBtn = document.createElement("button");
  allBtn.className = "filter-btn active";
  allBtn.textContent = "All skills";
  allBtn.dataset.category = "all";
  allBtn.type = "button";
  allBtn.setAttribute("role", "tab");
  allBtn.setAttribute("aria-selected", "true");
  filters.appendChild(allBtn);

  catalog.categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = "filter-btn";
    btn.textContent = CATEGORY_FILTER_LABELS[cat.id] || cat.label;
    btn.title = cat.label;
    btn.dataset.category = cat.id;
    btn.type = "button";
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", "false");
    filters.appendChild(btn);
  });

  filters.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    activeCategory = btn.dataset.category;
    filters.querySelectorAll(".filter-btn").forEach((b) => b.classList.toggle("active", b === btn));
    updateFilterAria(filters);
    renderSkills();
  });
}

function matches(skill) {
  const q = searchQuery.toLowerCase();
  const inCategory = activeCategory === "all" || skill.category === activeCategory;
  if (!inCategory) return false;
  if (!q) return true;
  const hay = `${skill.id} ${skill.name} ${skill.summary || ""} ${skill.description} ${skill.category}`.toLowerCase();
  return hay.includes(q);
}

function categoryMeta(categoryId) {
  return catalog.categories.find((cat) => cat.id === categoryId);
}

function sortSkillsForDisplay(skills, grouped) {
  if (!grouped) {
    return [...skills].sort((a, b) => a.id.localeCompare(b.id));
  }
  const order = catalog.categories.map((cat) => cat.id);
  return [...skills].sort((a, b) => {
    const ai = order.indexOf(a.category);
    const bi = order.indexOf(b.category);
    if (ai !== bi) return ai - bi;
    return a.id.localeCompare(b.id);
  });
}

function createCategoryHeading(categoryId) {
  const cat = categoryMeta(categoryId);
  const heading = document.createElement("div");
  heading.className = `skill-category-heading skill-category-heading--${categoryId}`;
  heading.innerHTML = `
    <h3>${escapeHtml(CATEGORY_SHORT[categoryId] || cat?.label || categoryId)}</h3>
    ${cat?.hook ? `<p>${escapeHtml(cat.hook)}</p>` : ""}
  `;
  return heading;
}

function renderSkills() {
  const grid = document.getElementById("skill-grid");
  const meta = document.getElementById("results-meta");
  const grouped = activeCategory === "all" && !searchQuery;
  const visible = sortSkillsForDisplay(catalog.skills.filter(matches), grouped);
  meta.textContent = `${visible.length} skill${visible.length === 1 ? "" : "s"} shown`;
  grid.innerHTML = "";
  grid.classList.toggle("skill-grid--grouped", grouped);

  if (visible.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" role="status">
        <p><strong>No skills match your search.</strong></p>
        <p>Try a broader term like “Stata”, “LaTeX”, or “WRDS”, or choose “All skills”.</p>
      </div>`;
    return;
  }

  let lastCategory = null;
  visible.forEach((skill, i) => {
    if (grouped && skill.category !== lastCategory) {
      grid.appendChild(createCategoryHeading(skill.category));
      lastCategory = skill.category;
    }
    grid.appendChild(createSkillCard(skill, { animationIndex: i }));
  });
}

let activateInstallPanel = null;

function initInstallTabs() {
  const tablist = document.querySelector(".install-tabs");
  if (!tablist) return;

  const tabs = tablist.querySelectorAll(".install-tab");
  const panels = {
    skills: document.getElementById("install-panel-skills"),
    mcp: document.getElementById("install-panel-mcp"),
  };

  activateInstallPanel = (panelId) => {
    tabs.forEach((tab) => {
      const active = tab.dataset.panel === panelId;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    Object.entries(panels).forEach(([id, panel]) => {
      if (!panel) return;
      const active = id === panelId;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  };

  tablist.addEventListener("click", (e) => {
    const tab = e.target.closest(".install-tab");
    if (!tab) return;
    activateInstallPanel(tab.dataset.panel);
  });
}

function activateInstallFromHash() {
  if (!activateInstallPanel) return;
  const hash = window.location.hash;
  if (hash === "#install-mcp" || hash === "#install?mcp") activateInstallPanel("mcp");
  else if (hash === "#install-skills") activateInstallPanel("skills");
}

function setNavOpen(nav, toggle, open) {
  const backdrop = document.getElementById("nav-backdrop");
  nav.classList.toggle("is-open", open);
  toggle.setAttribute("aria-expanded", open ? "true" : "false");
  document.body.classList.toggle("nav-open", open);
  if (backdrop) {
    backdrop.hidden = !open;
    backdrop.setAttribute("aria-hidden", open ? "false" : "true");
  }
}

function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  const backdrop = document.getElementById("nav-backdrop");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    setNavOpen(nav, toggle, !nav.classList.contains("is-open"));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setNavOpen(nav, toggle, false));
  });

  if (backdrop) {
    backdrop.addEventListener("click", () => setNavOpen(nav, toggle, false));
  }

  document.addEventListener("click", (e) => {
    if (!nav.classList.contains("is-open")) return;
    if (nav.contains(e.target) || toggle.contains(e.target)) return;
    setNavOpen(nav, toggle, false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      setNavOpen(nav, toggle, false);
    }
  });
}

function initScrollSpy() {
  const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
  if (!navLinks.length) return;

  const sections = [...navLinks]
    .map((link) => {
      const id = link.getAttribute("href").slice(1);
      return document.getElementById(id);
    })
    .filter(Boolean);

  if (!sections.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        navLinks.forEach((link) => {
          link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
        });
      });
    },
    { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
  );

  sections.forEach((section) => observer.observe(section));
}

function showSiteAlert(html) {
  const alert = document.getElementById("site-alert");
  if (!alert) return;
  alert.innerHTML = html;
  alert.hidden = false;
}

async function init() {
  initNav();

  const grid = document.getElementById("skill-grid");
  if (!grid) return;

  if (window.location.protocol === "file:") {
    showSiteAlert(
      "<strong>Local preview needed.</strong> Open this site through a web server, not as a file. " +
      "From the repo: <code>cd docs && python3 -m http.server 8080</code> then visit " +
      "<code>http://localhost:8080</code>."
    );
    const meta = document.getElementById("results-meta");
    if (meta) meta.textContent = "Skill catalog unavailable (file:// preview).";
    return;
  }

  const res = await fetch("data/skills.json");
  if (!res.ok) throw new Error(`skills.json HTTP ${res.status}`);
  catalog = await res.json();
  const el = document.getElementById("stat-skills");
  if (el) el.textContent = catalog.skills.length;
  renderFeatured();
  renderFilters();
  renderSkills();
  initInstallTabs();
  initScrollSpy();

  activateInstallFromHash();
  window.addEventListener("hashchange", activateInstallFromHash);
  document.getElementById("search").addEventListener("input", (e) => {
    searchQuery = e.target.value;
    renderSkills();
  });
}

init().catch((err) => {
  console.error(err);
  showSiteAlert(
    "<strong>Could not load the skill catalog.</strong> If this is GitHub Pages, confirm the repo is pushed " +
    "and Pages is enabled (<em>Settings → Pages → GitHub Actions</em>). For local preview run " +
    "<code>cd docs && python3 -m http.server 8080</code>."
  );
  const meta = document.getElementById("results-meta");
  if (meta) meta.textContent = "Could not load skill catalog.";
});
