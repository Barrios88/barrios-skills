const FEATURED_IDS = [
  "stata-regression",
  "wrds",
  "python-panel-data",
  "econ-humanizer-plus",
  "latex-tables",
  "econ-lit-search",
  "peer-review",
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
  return `https://github.com/jmb432/barrios-skills/tree/main/${path}`;
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
    a.innerHTML = `<h3>${titleCase(skill.id)}</h3><p>${truncate(skill.description, 110)}</p>`;
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

  visible.forEach((skill, i) => {
    const card = document.createElement("article");
    card.className = "skill-card";
    card.style.animationDelay = `${Math.min(i * 0.02, 0.4)}s`;
    const tag = CATEGORY_SHORT[skill.category] || skill.category;
    card.innerHTML = `
      <div class="skill-card-head">
        <h3>${titleCase(skill.id)}</h3>
        <span class="category-tag">${tag}</span>
      </div>
      <p>${truncate(skill.description)}</p>
      <a href="${githubPath(skill.path)}" target="_blank" rel="noopener">View skill folder →</a>
    `;
    grid.appendChild(card);
  });
}

async function init() {
  const res = await fetch("data/skills.json");
  catalog = await res.json();
  document.getElementById("stat-skills").textContent = catalog.skills.length;
  document.getElementById("stat-categories").textContent = catalog.categories.length;
  renderFeatured();
  renderFilters();
  renderSkills();
  document.getElementById("search").addEventListener("input", (e) => {
    searchQuery = e.target.value;
    renderSkills();
  });
}

init().catch((err) => {
  console.error(err);
  document.getElementById("results-meta").textContent = "Could not load skill catalog.";
});
