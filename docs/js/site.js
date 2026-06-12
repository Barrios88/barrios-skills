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

let catalog = null;
let activeCategory = "all";
let searchQuery = "";

function titleCase(id) {
  return id.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function truncate(text, n = 140) {
  if (!text) return "";
  const clean = text.replace(/\s+/g, " ").trim();
  return clean.length > n ? clean.slice(0, n - 1) + "…" : clean;
}

function githubPath(path) {
  return `https://github.com/Barrios88/barrios-skills/tree/main/${path}`;
}

function renderFeatured() {
  const grid = document.getElementById("featured-grid");
  grid.innerHTML = "";
  FEATURED_IDS.forEach((id) => {
    const skill = catalog.skills.find((s) => s.id === id);
    if (!skill) return;
    const a = document.createElement("a");
    a.className = "feature-card";
    a.href = githubPath(skill.path);
    a.target = "_blank";
    a.rel = "noopener";
    a.innerHTML = `<h3>${titleCase(skill.id)}</h3><p>${truncate(skill.description, 110)}</p><span class="feature-card-cta">Open on GitHub →</span>`;
    grid.appendChild(a);
  });
}

function renderFilters() {
  const filters = document.getElementById("filters");
  const allBtn = document.createElement("button");
  allBtn.className = "filter-btn active";
  allBtn.textContent = "All skills";
  allBtn.dataset.category = "all";
  allBtn.type = "button";
  filters.appendChild(allBtn);

  catalog.categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = "filter-btn";
    btn.textContent = cat.label;
    btn.dataset.category = cat.id;
    btn.type = "button";
    filters.appendChild(btn);
  });

  filters.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    activeCategory = btn.dataset.category;
    filters.querySelectorAll(".filter-btn").forEach((b) => b.classList.toggle("active", b === btn));
    renderSkills();
  });
}

function matches(skill) {
  const q = searchQuery.toLowerCase();
  const inCategory = activeCategory === "all" || skill.category === activeCategory;
  if (!inCategory) return false;
  if (!q) return true;
  const hay = `${skill.id} ${skill.name} ${skill.description} ${skill.category}`.toLowerCase();
  return hay.includes(q);
}

function renderSkills() {
  const grid = document.getElementById("skill-grid");
  const meta = document.getElementById("results-meta");
  const visible = catalog.skills.filter(matches).sort((a, b) => a.id.localeCompare(b.id));
  meta.textContent = `${visible.length} skill${visible.length === 1 ? "" : "s"} shown`;
  grid.innerHTML = "";

  if (visible.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" role="status">
        <p><strong>No skills match your search.</strong></p>
        <p>Try a broader term like “Stata”, “LaTeX”, or “WRDS”, or choose “All skills”.</p>
      </div>`;
    return;
  }

  visible.forEach((skill, i) => {
    const card = document.createElement("a");
    card.className = "skill-card";
    card.href = githubPath(skill.path);
    card.target = "_blank";
    card.rel = "noopener";
    card.style.animationDelay = `${Math.min(i * 0.02, 0.4)}s`;
    const tag = CATEGORY_SHORT[skill.category] || skill.category;
    card.innerHTML = `
      <div class="skill-card-head">
        <h3>${titleCase(skill.id)}</h3>
        <span class="category-tag category-tag--${skill.category}">${tag}</span>
      </div>
      <p>${truncate(skill.description)}</p>
      <span class="skill-card-cta">Open on GitHub →</span>
    `;
    grid.appendChild(card);
  });
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
  initScrollSpy();
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
