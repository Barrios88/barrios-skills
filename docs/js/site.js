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
  econometrics: "Econometrics",
  "data-and-visualization": "Data & viz",
  "research-tools": "Research",
  "writing-and-review": "Writing",
};

const CATEGORY_FILTER_LABELS = {
  econometrics: "Econometrics",
  "data-and-visualization": "Data & viz",
  "research-tools": "Research",
  "writing-and-review": "Writing",
};

const PAGE = document.body.dataset.page || "home";

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

function cardIsExpandable(skill, { featured = false } = {}) {
  const summary = skillSummary(skill);
  const hasDetail = skillHasDetail(skill);
  const clampAt = featured ? 72 : 80;
  return descriptionNeedsClamp(summary, clampAt) || (hasDetail && descriptionNeedsClamp(skill.description, 100));
}

function skillCardMarkup(skill, { featured = false } = {}) {
  const tag = CATEGORY_SHORT[skill.category] || skill.category;
  const summary = skillSummary(skill);
  const hasDetail = skillHasDetail(skill);
  const expandable = cardIsExpandable(skill, { featured });
  const descClass = expandable ? "skill-card-desc is-clamped" : "skill-card-desc";
  const detailHtml = hasDetail
    ? `<p class="skill-card-detail">${escapeHtml(skill.description)}</p>`
    : "";
  const moreBtn = expandable
    ? `<button type="button" class="skill-card-more" aria-expanded="false">More</button>`
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
      ${moreBtn}
      <a class="skill-card-download" href="${skillDownloadUrl(skill.id)}" download="${skill.id}.zip" aria-label="Download ${titleCase(skill.id)} zip">Download zip ↓</a>
    </div>
  `;
}

function applySkillCardClasses(card, skill, { featured = false } = {}) {
  if (cardIsExpandable(skill, { featured })) {
    card.classList.add("is-expandable");
  }
  card.classList.add(`skill-card--${skill.category}`);
  card.dataset.category = skill.category;
}

function bindSkillCardInteractions(root = document) {
  root.querySelectorAll(".skill-card-interactive.is-expandable").forEach((card) => {
    const more = card.querySelector(".skill-card-more");
    if (!more) return;
    more.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = card.classList.toggle("is-expanded");
      more.setAttribute("aria-expanded", open ? "true" : "false");
      more.textContent = open ? "Less" : "More";
    });
  });
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
  if (!grid) return;
  grid.innerHTML = "";
  FEATURED_IDS.forEach((id) => {
    const skill = catalog.skills.find((s) => s.id === id);
    if (!skill) return;
    grid.appendChild(createSkillCard(skill, { featured: true }));
  });
  bindSkillCardInteractions(grid);
}

function updateFilterAria(filters) {
  filters.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.setAttribute("aria-selected", btn.classList.contains("active") ? "true" : "false");
  });
}

function setActiveCategory(categoryId, filters) {
  activeCategory = categoryId;
  filters.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.category === categoryId);
  });
  updateFilterAria(filters);
}

function renderFilters(filters) {
  filters.innerHTML = "";
  const allBtn = document.createElement("button");
  allBtn.className = `filter-btn${activeCategory === "all" ? " active" : ""}`;
  allBtn.textContent = "All skills";
  allBtn.dataset.category = "all";
  allBtn.type = "button";
  allBtn.setAttribute("role", "tab");
  allBtn.setAttribute("aria-selected", activeCategory === "all" ? "true" : "false");
  filters.appendChild(allBtn);

  catalog.categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = `filter-btn${activeCategory === cat.id ? " active" : ""}`;
    btn.textContent = CATEGORY_FILTER_LABELS[cat.id] || cat.label;
    btn.title = cat.label;
    btn.dataset.category = cat.id;
    btn.type = "button";
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", activeCategory === cat.id ? "true" : "false");
    filters.appendChild(btn);
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

function emptyStateHtml() {
  const hint = searchQuery
    ? `No results for “${escapeHtml(searchQuery)}”.`
    : "No skills in this category yet.";
  return `
    <div class="empty-state" role="status">
      <div class="empty-state-icon" aria-hidden="true">⌕</div>
      <p><strong>${hint}</strong></p>
      <p>Try “Stata”, “LaTeX”, or “WRDS”, or choose <strong>All skills</strong>.</p>
    </div>`;
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
    grid.innerHTML = emptyStateHtml();
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
  bindSkillCardInteractions(grid);
}

function syncUrlParams() {
  if (PAGE !== "skills") return;
  const params = new URLSearchParams(window.location.search);
  const q = params.get("q") || "";
  const cat = params.get("category") || "all";
  searchQuery = q;
  if (catalog.categories.some((c) => c.id === cat) || cat === "all") {
    activeCategory = cat;
  }
  const search = document.getElementById("search");
  if (search) search.value = q;
}

function updateUrlParams() {
  if (PAGE !== "skills") return;
  const params = new URLSearchParams();
  if (searchQuery) params.set("q", searchQuery);
  if (activeCategory !== "all") params.set("category", activeCategory);
  const qs = params.toString();
  const next = `${window.location.pathname}${qs ? `?${qs}` : ""}`;
  window.history.replaceState(null, "", next);
}

function initBrowseFilters() {
  const filters = document.getElementById("filters");
  if (!filters) return;

  renderFilters(filters);

  filters.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    setActiveCategory(btn.dataset.category, filters);
    updateUrlParams();
    renderSkills();
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

function initScrollSpy() {
  const navLinks = document.querySelectorAll('.site-nav a[href^="#"]');
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
          link.classList.toggle("active", link.getAttribute("href") === `#${id}`);
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

async function loadCatalog() {
  const res = await fetch("data/skills.json");
  if (!res.ok) throw new Error(`skills.json HTTP ${res.status}`);
  catalog = await res.json();
  const el = document.getElementById("stat-skills");
  if (el) el.textContent = catalog.skills.length;
}

async function initHomePage() {
  if (window.location.protocol === "file:") {
    showSiteAlert(
      "<strong>Local preview needed.</strong> Open through a web server: " +
      "<code>cd docs && python3 -m http.server 8080</code>"
    );
    return;
  }

  await loadCatalog();
  renderFeatured();
  initInstallTabs();
  initScrollSpy();
  activateInstallFromHash();
  window.addEventListener("hashchange", activateInstallFromHash);
}

async function initSkillsPage() {
  const grid = document.getElementById("skill-grid");
  if (!grid) return;

  if (window.location.protocol === "file:") {
    showSiteAlert(
      "<strong>Local preview needed.</strong> Open through a web server: " +
      "<code>cd docs && python3 -m http.server 8080</code>"
    );
    const meta = document.getElementById("results-meta");
    if (meta) meta.textContent = "Skill catalog unavailable (file:// preview).";
    return;
  }

  await loadCatalog();
  syncUrlParams();
  initBrowseFilters();
  renderSkills();

  const search = document.getElementById("search");
  if (search) {
    search.addEventListener("input", (e) => {
      searchQuery = e.target.value;
      updateUrlParams();
      renderSkills();
    });
  }
}

async function init() {
  if (PAGE === "skills") {
    await initSkillsPage();
  } else {
    await initHomePage();
  }
}

init().catch((err) => {
  console.error(err);
  showSiteAlert(
    "<strong>Could not load the skill catalog.</strong> Confirm the repo is pushed and GitHub Pages is enabled."
  );
  const meta = document.getElementById("results-meta");
  if (meta) meta.textContent = "Could not load skill catalog.";
});
