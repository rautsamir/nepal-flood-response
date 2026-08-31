const DATA_ROOT = "./data";

const copy = {
  en: {
    brand: "Nepal Flood Response Map", brandSub: "Open-data situation dashboard",
    method: "Methodology", eyebrow: "BHOTEKOSHI–TRISHULI CORRIDOR · OPEN DATA",
    title: "Where damage and access constraints overlap",
    intro: "A public view of building damage, estimated population exposure, bridge access and response infrastructure. Explore the evidence—not a forecast or official assessment.",
    snapshot: "Static lakehouse snapshot", snapshotSub: "No login, no AI-generated answers",
    damaged: "Damaged buildings", people: "People in damaged footprint",
    isolated: "Likely isolated cells", cells: "Affected ~1 km cells",
    explore: "EXPLORE", filters: "Filter the response picture", reset: "Reset",
    district: "District", access: "Access condition", all: "All",
    isolatedShort: "Likely isolated", connected: "No nearby bridge damage",
    priority: "Minimum priority percentile", layers: "Map layers",
    health: "Health facilities", education: "Education", openSpace: "Open spaces",
    hydropower: "Hydropower", bridges: "Damaged bridges", helipads: "Helipads",
    floodExtent: "Observed flood extent", needLegend: "PRIORITY SCORE",
    lower: "Lower", higher: "Higher", cellsVisible: "cells visible",
    comparison: "DISTRICT COMPARISON", districtNeed: "Relative priority score",
    districtCaption: "Score combines damage-weighted population with nearby bridge failures. Compare relative urgency; do not interpret as a casualty estimate.",
    highest: "HIGHEST PRIORITY LOCATIONS", ranked: "Ranked evidence",
    location: "Location", damagedShort: "Damaged", population: "Population",
    bridges5: "Bridges ≤5 km", helipad: "Helipad", priorityShort: "Priority",
    provenance: "PROVENANCE", sourcesTitle: "Built from open humanitarian evidence",
    buildingDamage: "Building damage", populationGrid: "Population grid",
    accessInfra: "Access & infrastructure", operationalLayers: "Operational layers",
    disclaimer: "Prototype derived from open data. Not an official assessment. Validate locally before operational use.",
    readMethod: "Read methodology", methodologyLabel: "METHODOLOGY",
    howRanked: "How locations are ranked",
    methodCopy: "Buildings are grouped into approximately 1 km cells and joined to a population grid. Nearby damaged bridges increase the priority score as an access constraint. Helipad distance is shown as context but does not change the score.",
    methodCaution: "These are relative triage indicators, not counts of casualties, displaced people or verified unmet need.",
    allDistricts: "All districts", search: "Search location", asOf: "Snapshot",
    isolatedFlag: "Likely isolated", estimatedPeople: "Estimated people", affectedCells: "affected cells",
    km: "km", unknown: "Unnamed cell"
  },
  ne: {
    brand: "नेपाल बाढी प्रतिकार्य नक्सा", brandSub: "खुला तथ्याङ्क स्थिति ड्यासबोर्ड",
    method: "विधि", eyebrow: "भोटेकोशी–त्रिशूली करिडोर · खुला तथ्याङ्क",
    title: "क्षति र पहुँच अवरोध एकै ठाउँमा",
    intro: "भवन क्षति, अनुमानित जनसङ्ख्या प्रभाव, पुल पहुँच र प्रतिकार्य पूर्वाधारको सार्वजनिक दृश्य। यो पूर्वानुमान वा आधिकारिक मूल्याङ्कन होइन।",
    snapshot: "लेकहाउसको स्थिर स्न्यापसट", snapshotSub: "लगइन वा एआई उत्तर आवश्यक छैन",
    damaged: "क्षतिग्रस्त भवन", people: "क्षतिग्रस्त क्षेत्रमा अनुमानित मानिस",
    isolated: "सम्भावित अलग भएका सेल", cells: "प्रभावित ~१ किमि सेल",
    explore: "अन्वेषण", filters: "प्रतिकार्य चित्र फिल्टर गर्नुहोस्", reset: "रिसेट",
    district: "जिल्ला", access: "पहुँच अवस्था", all: "सबै",
    isolatedShort: "सम्भावित अलग", connected: "नजिक पुल क्षति छैन",
    priority: "न्यूनतम प्राथमिकता प्रतिशतक", layers: "नक्साका तहहरू",
    health: "स्वास्थ्य सुविधा", education: "शिक्षा", openSpace: "खुला स्थान",
    hydropower: "जलविद्युत", bridges: "क्षतिग्रस्त पुल", helipads: "हेलिप्याड",
    floodExtent: "अवलोकित बाढी क्षेत्र", needLegend: "प्राथमिकता स्कोर",
    lower: "न्यून", higher: "उच्च", cellsVisible: "सेल देखिएका",
    comparison: "जिल्ला तुलना", districtNeed: "सापेक्ष प्राथमिकता स्कोर",
    districtCaption: "स्कोरले जनसङ्ख्याद्वारा भारित क्षति र नजिकका क्षतिग्रस्त पुललाई जोड्छ। यो हताहतीको अनुमान होइन।",
    highest: "उच्च प्राथमिकताका स्थान", ranked: "क्रमबद्ध प्रमाण",
    location: "स्थान", damagedShort: "क्षति", population: "जनसङ्ख्या",
    bridges5: "५ किमिभित्र पुल", helipad: "हेलिप्याड", priorityShort: "प्राथमिकता",
    provenance: "स्रोत", sourcesTitle: "खुला मानवीय प्रमाणबाट निर्मित",
    buildingDamage: "भवन क्षति", populationGrid: "जनसङ्ख्या ग्रिड",
    accessInfra: "पहुँच र पूर्वाधार", operationalLayers: "सञ्चालन तहहरू",
    disclaimer: "खुला तथ्याङ्कमा आधारित नमुना। आधिकारिक मूल्याङ्कन होइन। प्रयोगअघि स्थानीय रूपमा पुष्टि गर्नुहोस्।",
    readMethod: "विधि पढ्नुहोस्", methodologyLabel: "विधि",
    howRanked: "स्थानहरू कसरी क्रमबद्ध गरिन्छन्",
    methodCopy: "भवनलाई करिब १ किमि सेलमा समूह गरी जनसङ्ख्या ग्रिडसँग जोडिएको छ। नजिकका क्षतिग्रस्त पुलले पहुँच अवरोधका रूपमा प्राथमिकता बढाउँछन्। हेलिप्याड दूरी सन्दर्भका लागि मात्र हो।",
    methodCaution: "यी सापेक्ष प्राथमिकता सूचक हुन्; हताहती, विस्थापित व्यक्ति वा पुष्टि भएको आवश्यकताको गणना होइनन्।",
    allDistricts: "सबै जिल्ला", search: "स्थान खोज्नुहोस्", asOf: "स्न्यापसट",
    isolatedFlag: "सम्भावित अलग", estimatedPeople: "अनुमानित मानिस", affectedCells: "प्रभावित सेल",
    km: "किमि", unknown: "नाम नभएको सेल"
  }
};

const state = {
  language: "en",
  meta: null,
  cells: [],
  pois: [],
  bridges: [],
  helipads: [],
  flood: null,
  isolation: "all",
  sort: { key: "priority_score", direction: "desc" }
};

let map;
let cellLayer;
let poiLayer;
let bridgeLayer;
let helipadLayer;
let floodLayer;

const nf = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const getText = key => copy[state.language][key] ?? key;
const formatNumber = value => nf.format(Number(value) || 0);

function initMap() {
  map = L.map("map", { zoomControl: false, preferCanvas: true }).setView([28.05, 85.25], 9);
  L.control.zoom({ position: "topright" }).addTo(map);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);
  cellLayer = L.layerGroup().addTo(map);
  poiLayer = L.layerGroup().addTo(map);
  bridgeLayer = L.layerGroup().addTo(map);
  helipadLayer = L.layerGroup().addTo(map);
  floodLayer = L.geoJSON(null, {
    style: { color: "#2784a9", weight: 2, fillColor: "#2784a9", fillOpacity: .16 }
  }).addTo(map);
}

async function getJson(filename) {
  const response = await fetch(`${DATA_ROOT}/${filename}`);
  if (!response.ok) throw new Error(`${filename}: HTTP ${response.status}`);
  return response.json();
}

async function loadData() {
  const [meta, cells, pois, bridges, helipads, flood] = await Promise.all([
    getJson("meta.json"),
    getJson("need-cells.geojson"),
    getJson("pois.geojson"),
    getJson("bridges.geojson"),
    getJson("helipads.geojson"),
    getJson("flood-extent.geojson")
  ]);
  state.meta = meta;
  state.cells = cells.features;
  state.pois = pois.features;
  state.bridges = bridges.features;
  state.helipads = helipads.features;
  state.flood = flood;
}

function percentileThreshold(percentile) {
  if (!percentile) return -Infinity;
  const scores = state.cells
    .map(feature => Number(feature.properties.priority_score) || 0)
    .sort((a, b) => a - b);
  return scores[Math.floor((scores.length - 1) * percentile / 100)] ?? -Infinity;
}

function filteredCells() {
  const district = document.getElementById("district-filter").value;
  const percentile = Number(document.getElementById("priority-filter").value);
  const threshold = percentileThreshold(percentile);
  return state.cells.filter(feature => {
    const p = feature.properties;
    const isolationMatch =
      state.isolation === "all" ||
      (state.isolation === "isolated" && p.likely_isolated) ||
      (state.isolation === "connected" && !p.likely_isolated);
    return (!district || p.district === district) &&
      isolationMatch &&
      Number(p.priority_score) >= threshold;
  });
}

function scoreColor(score) {
  const max = Math.max(...state.cells.map(f => Number(f.properties.priority_score) || 0), 1);
  const ratio = Math.log1p(Number(score) || 0) / Math.log1p(max);
  if (ratio > .72) return "#d72f4a";
  if (ratio > .46) return "#ed7a31";
  return "#f3b64c";
}

function popupNode(properties, kind = "cell") {
  const wrap = document.createElement("div");
  const title = document.createElement("strong");
  title.className = "popup-title";
  title.textContent = properties.place_name || properties.name || getText("unknown");
  wrap.appendChild(title);
  const lines = kind === "cell"
    ? [
        [getText("district"), properties.district],
        [getText("damaged"), formatNumber(properties.damaged_bld)],
        [getText("population"), formatNumber(properties.population)],
        [getText("bridges5"), properties.damaged_bridges_5km],
        [getText("helipad"), properties.nearest_helipad_km == null ? null : `${properties.nearest_helipad_km} ${getText("km")}`],
        [getText("isolatedFlag"), properties.likely_isolated ? "Yes" : "No"]
      ]
    : [
        [getText("district"), properties.district],
        ["Type", properties.subtype || properties.category],
        ["Status", properties.status],
        ["Municipality", properties.municipality]
      ];
  lines.forEach(([label, value]) => {
    if (value === null || value === undefined || value === "") return;
    const line = document.createElement("div");
    line.className = "popup-line";
    line.textContent = `${label}: ${value}`;
    wrap.appendChild(line);
  });
  if (kind === "cell") {
    const score = document.createElement("div");
    score.className = "popup-score";
    score.textContent = `${getText("priorityShort")}: ${formatNumber(properties.priority_score)}`;
    wrap.appendChild(score);
  }
  return wrap;
}

function renderCells(features) {
  cellLayer.clearLayers();
  const points = [];
  features.forEach(feature => {
    const [lon, lat] = feature.geometry.coordinates;
    const p = feature.properties;
    const score = Number(p.priority_score) || 0;
    const radius = Math.max(5, Math.min(20, 4 + Math.log10(score + 1) * 2.25));
    L.circleMarker([lat, lon], {
      radius,
      color: "#fff",
      weight: 1.2,
      fillColor: scoreColor(score),
      fillOpacity: .82
    }).bindPopup(popupNode(p)).addTo(cellLayer);
    points.push([lat, lon]);
  });
  document.getElementById("visible-count").textContent = features.length;
  if (points.length) map.fitBounds(points, { padding: [35, 35], maxZoom: 11 });
}

function renderOverlayLayers() {
  poiLayer.clearLayers();
  bridgeLayer.clearLayers();
  helipadLayer.clearLayers();
  floodLayer.clearLayers();
  const enabled = new Set(
    [...document.querySelectorAll(".layers input:checked")].map(input => input.value)
  );
  const colors = {
    health: "#d93c51", education: "#327db8",
    open_space: "#3b946f", hydropower: "#825ea7"
  };
  state.pois.forEach(feature => {
    const p = feature.properties;
    if (!enabled.has(p.category)) return;
    const [lon, lat] = feature.geometry.coordinates;
    L.circleMarker([lat, lon], {
      radius: 5, color: "#fff", weight: 1.2,
      fillColor: colors[p.category], fillOpacity: .95
    }).bindPopup(popupNode(p, "poi")).addTo(poiLayer);
  });
  if (enabled.has("bridges")) {
    state.bridges.forEach(feature => {
      const [lon, lat] = feature.geometry.coordinates;
      L.circleMarker([lat, lon], {
        radius: 6, color: "#fff", weight: 1.2, fillColor: "#e18121", fillOpacity: .95
      }).bindPopup(popupNode(feature.properties, "poi")).addTo(bridgeLayer);
    });
  }
  if (enabled.has("helipads")) {
    state.helipads.forEach(feature => {
      const [lon, lat] = feature.geometry.coordinates;
      L.circleMarker([lat, lon], {
        radius: 6, color: "#fff", weight: 1.2, fillColor: "#354f6a", fillOpacity: .95
      }).bindPopup(popupNode(feature.properties, "poi")).addTo(helipadLayer);
    });
  }
  if (enabled.has("flood") && state.flood) floodLayer.addData(state.flood);
}

function renderMetrics() {
  const s = state.meta.summary;
  document.getElementById("metric-damaged").textContent = formatNumber(s.damaged_buildings);
  document.getElementById("metric-people").textContent = formatNumber(s.estimated_people);
  document.getElementById("metric-isolated").textContent = formatNumber(s.isolated_cells);
  document.getElementById("metric-cells").textContent = formatNumber(s.affected_cells);
  document.getElementById("as-of").textContent = `${getText("asOf")} · ${state.meta.as_of_label}`;
}

function renderDistricts() {
  const rows = state.meta.districts;
  const max = Math.max(...rows.map(row => Number(row.priority_score)), 1);
  const container = document.getElementById("district-bars");
  container.replaceChildren();
  rows.forEach(row => {
    const item = document.createElement("div");
    item.className = "district-row";
    const meta = document.createElement("div");
    meta.className = "district-meta";
    const name = document.createElement("strong");
    name.textContent = row.district || "Unknown";
    const score = document.createElement("span");
    score.textContent = formatNumber(row.priority_score);
    meta.append(name, score);
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = `${Math.max(1, Number(row.priority_score) / max * 100)}%`;
    track.appendChild(fill);
    const stats = document.createElement("div");
    stats.className = "district-stats";
    stats.textContent = `${formatNumber(row.damaged_buildings)} ${getText("damagedShort").toLowerCase()} · ${formatNumber(row.estimated_people)} ${getText("estimatedPeople").toLowerCase()} · ${row.affected_cells} ${getText("affectedCells")}`;
    item.append(meta, track, stats);
    container.appendChild(item);
  });
}

function compareRows(a, b, key) {
  const left = a.properties[key];
  const right = b.properties[key];
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  if (Number.isFinite(leftNumber) && Number.isFinite(rightNumber)) return leftNumber - rightNumber;
  return String(left ?? "").localeCompare(String(right ?? ""), undefined, { numeric: true });
}

function renderTable(features) {
  const query = document.getElementById("table-search").value.trim().toLowerCase();
  const rows = features
    .filter(feature => !query || Object.values(feature.properties).some(value =>
      String(value ?? "").toLowerCase().includes(query)
    ))
    .sort((a, b) => compareRows(a, b, state.sort.key) * (state.sort.direction === "asc" ? 1 : -1))
    .slice(0, 30);
  const body = document.getElementById("priority-table");
  body.replaceChildren();
  rows.forEach(feature => {
    const p = feature.properties;
    const tr = document.createElement("tr");
    const values = [
      p.place_name || getText("unknown"), p.district,
      formatNumber(p.damaged_bld), formatNumber(p.population),
      p.damaged_bridges_5km,
      p.nearest_helipad_km == null ? "—" : `${p.nearest_helipad_km} ${getText("km")}`,
      formatNumber(p.priority_score)
    ];
    values.forEach((value, index) => {
      const td = document.createElement("td");
      if (index >= 2) td.className = "numeric";
      if (index === 0 && p.likely_isolated) {
        const name = document.createElement("div");
        name.textContent = value;
        const flag = document.createElement("span");
        flag.className = "isolation-flag";
        flag.textContent = getText("isolatedFlag");
        td.append(name, flag);
      } else if (index === 6) {
        const pill = document.createElement("span");
        pill.className = "priority-pill";
        pill.textContent = value;
        td.appendChild(pill);
      } else {
        td.textContent = value ?? "—";
      }
      tr.appendChild(td);
    });
    tr.addEventListener("click", () => {
      const [lon, lat] = feature.geometry.coordinates;
      map.flyTo([lat, lon], 12);
      document.getElementById("map").scrollIntoView({ behavior: "smooth", block: "center" });
    });
    body.appendChild(tr);
  });
}

function renderCounts() {
  const categories = ["health", "education", "open_space", "hydropower"];
  categories.forEach(category => {
    document.getElementById(`count-${category}`).textContent =
      state.pois.filter(feature => feature.properties.category === category).length;
  });
  document.getElementById("count-bridges").textContent = state.bridges.length;
  document.getElementById("count-helipads").textContent = state.helipads.length;
}

function populateDistricts() {
  const select = document.getElementById("district-filter");
  const selected = select.value;
  select.replaceChildren();
  const all = document.createElement("option");
  all.value = "";
  all.textContent = getText("allDistricts");
  select.appendChild(all);
  [...new Set(state.cells.map(f => f.properties.district).filter(Boolean))]
    .sort()
    .forEach(district => {
      const option = document.createElement("option");
      option.value = district;
      option.textContent = district;
      select.appendChild(option);
    });
  select.value = selected;
}

function applyFilters() {
  const features = filteredCells();
  renderCells(features);
  renderTable(features);
}

function setLanguage(language) {
  state.language = language;
  document.documentElement.lang = language;
  document.getElementById("lang-en").classList.toggle("active", language === "en");
  document.getElementById("lang-ne").classList.toggle("active", language === "ne");
  document.querySelectorAll("[data-i18n]").forEach(element => {
    element.textContent = getText(element.dataset.i18n);
  });
  document.getElementById("table-search").placeholder = getText("search");
  populateDistricts();
  renderMetrics();
  renderDistricts();
  applyFilters();
}

function bindEvents() {
  document.getElementById("lang-en").addEventListener("click", () => setLanguage("en"));
  document.getElementById("lang-ne").addEventListener("click", () => setLanguage("ne"));
  document.getElementById("district-filter").addEventListener("change", applyFilters);
  document.getElementById("priority-filter").addEventListener("input", event => {
    document.getElementById("priority-value").textContent = `${event.target.value}%`;
    applyFilters();
  });
  document.querySelectorAll("[data-isolation]").forEach(button => {
    button.addEventListener("click", () => {
      state.isolation = button.dataset.isolation;
      document.querySelectorAll("[data-isolation]").forEach(item =>
        item.classList.toggle("active", item === button)
      );
      applyFilters();
    });
  });
  document.querySelectorAll(".layers input").forEach(input =>
    input.addEventListener("change", renderOverlayLayers)
  );
  document.getElementById("table-search").addEventListener("input", () =>
    renderTable(filteredCells())
  );
  document.querySelectorAll("th[data-sort]").forEach(header => {
    header.addEventListener("click", () => {
      const key = header.dataset.sort;
      state.sort.direction =
        state.sort.key === key && state.sort.direction === "desc" ? "asc" : "desc";
      state.sort.key = key;
      renderTable(filteredCells());
    });
  });
  document.getElementById("reset-filters").addEventListener("click", () => {
    document.getElementById("district-filter").value = "";
    document.getElementById("priority-filter").value = "0";
    document.getElementById("priority-value").textContent = "0%";
    document.getElementById("table-search").value = "";
    state.isolation = "all";
    document.querySelectorAll("[data-isolation]").forEach(item =>
      item.classList.toggle("active", item.dataset.isolation === "all")
    );
    applyFilters();
  });
  const dialog = document.getElementById("method-dialog");
  document.getElementById("open-method").addEventListener("click", () => dialog.showModal());
  document.getElementById("footer-method").addEventListener("click", event => {
    event.preventDefault();
    dialog.showModal();
  });
  document.getElementById("close-method").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
  });
}

async function start() {
  initMap();
  bindEvents();
  try {
    await loadData();
    populateDistricts();
    renderMetrics();
    renderCounts();
    renderDistricts();
    renderOverlayLayers();
    applyFilters();
    document.getElementById("loading").classList.add("hidden");
    window.setTimeout(() => map.invalidateSize(), 300);
  } catch (error) {
    console.error("Unable to load dashboard snapshot", error);
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("error").hidden = false;
  }
}

start();
