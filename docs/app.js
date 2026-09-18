// Client-side filter/search/sort + interactive charts for the GenAI
// Security Incidents dataset. Pure vanilla JS, no build, no deps.

const PAGE_SIZE_DEFAULT = 250;
const PAGE_SIZE_OPTIONS = [50, 100, 250, 500, 1000];
let PAGE_SIZE = PAGE_SIZE_DEFAULT;
const SEV_RANK = { Critical: 4, High: 3, Medium: 2, Low: 1, Info: 0 };
const SEV_VARS = {
  Critical: "var(--critical)",
  High: "var(--high)",
  Medium: "var(--medium)",
  Low: "var(--low)",
  Info: "var(--info)",
};
// OWASP Top 10 for LLM Applications 2026. Rank order matters: charts and
// filter dropdowns render in insertion order.
const LLM_NAMES = {
  LLM01: "Prompt Injection", LLM02: "Sensitive Info Disclosure",
  LLM03: "Excessive Agency", LLM04: "Supply Chain",
  LLM05: "Data & Model Poisoning", LLM06: "Unbounded Consumption",
  LLM07: "Misinformation", LLM08: "Hidden Context Exposure",
  LLM09: "Vector & Embedding", LLM10: "Improper Output Handling",
};
const ASI_NAMES = {
  ASI01: "Agent Goal Hijack", ASI02: "Tool Misuse & Exploit",
  ASI03: "Identity & Privilege Abuse", ASI04: "Agentic Supply Chain",
  ASI05: "Unexpected RCE", ASI06: "Memory & Context Poisoning",
  ASI07: "Insecure Inter-Agent Comm", ASI08: "Cascading Failures",
  ASI09: "Human-Agent Trust Exploit", ASI10: "Rogue Agents",
};

const els = {
  q: document.getElementById('q'),
  year: document.getElementById('year'),
  severity: document.getElementById('severity'),
  llm: document.getElementById('llm'),
  asi: document.getElementById('asi'),
  vector: document.getElementById('vector'),
  corpus: document.getElementById('corpus'),
  quality: document.getElementById('quality'),
  cveOnly: document.getElementById('cve_only'),
  pageSize: document.getElementById('page_size'),
  status: document.getElementById('result-status'),
  body: document.querySelector('#incidents tbody'),
  pager: document.getElementById('pager'),
  chips: document.getElementById('filter-chips'),
  stats: document.getElementById('stats'),
  meta: document.getElementById('dataset-meta'),
  table: document.getElementById('incidents'),
  backToTop: document.getElementById('back-to-top'),
  exportCsv: document.getElementById('export-csv'),
};

const FILTER_KEYS = ['q','year','severity','llm','asi','vector','corpus','quality','cveOnly'];
const FILTER_LABEL = {
  q: 'Search', year: 'Year', severity: 'Severity',
  llm: 'OWASP LLM', asi: 'OWASP ASI', vector: 'Vector',
  corpus: 'Corpus', quality: 'Quality', cveOnly: 'CVE',
};

let DATA = [];
let FILTERED = [];
let PAGE = 1;
let SORT_BY = 'date';
let SORT_DIR = 'desc';
let EXPANDED = new Set();

// ----------------------------- Lazy detail loading ------------------------
// The initial fetch is data/incidents.core.json -- table/filter/chart
// fields PLUS primary_reference (~36.0% of the full dataset's bytes,
// measured -- see scripts/gen_docs_core_data.py's printed summary).
// primary_reference is core, not lazy, because matches() below searches it
// on every keystroke against the FULL dataset (see the CORE_FIELDS comment
// in that script for the search-correctness bug this fixes). The remaining
// fields (description, tags, content_license, nist_ai_rmf, mitre_atlas,
// source_freshness) live in one data/detail/<year>.json shard per
// publication year and are fetched only when a row in that year is
// actually expanded, or on CSV export. Once a year's shard resolves, its
// fields are merged directly onto the matching objects in DATA, so every
// later read (including re-renders) is synchronous with no cache-lookup
// indirection.
// Explicit per-year fetch status, not inferred from field presence: the
// earlier version treated "loaded" as `description !== undefined`, which
// made "not fetched yet" and "fetch failed" indistinguishable -- a failed
// shard left every row of that year showing "Loading details…" forever
// (renderDetail's early return never had a failure branch), and CSV export
// (below) used Promise.allSettled and silently exported blank cells for
// the failed year with no warning. Tracking 'unloaded' / 'loading' /
// 'loaded' / 'failed' explicitly lets renderDetail show a real error state
// with retry, and lets export detect and warn about partial data instead
// of shipping a CSV that looks complete but silently isn't (WS6-T5
// design-pass report, defect A3).
const DETAIL_STATUS = new Map(); // year (string) -> 'loading' | 'loaded' | 'failed'
const DETAIL_PROMISES = new Map();
const DETAIL_FIELDS = ['description', 'tags',
  'content_license', 'nist_ai_rmf', 'mitre_atlas', 'source_freshness'];

function hasDetail(e) { return e.description !== undefined; }
function detailStatus(year) { return DETAIL_STATUS.get(String(year)) || 'unloaded'; }

function ensureDetailLoaded(year) {
  const key = String(year);
  const status = DETAIL_STATUS.get(key);
  if (status === 'loaded') return Promise.resolve();
  if (status === 'loading') return DETAIL_PROMISES.get(key);
  DETAIL_STATUS.set(key, 'loading');
  const p = fetch(`data/detail/${encodeURIComponent(key)}.json`)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(map => {
      for (const e of DATA) {
        if (String(e.year) === key && map[e.id]) Object.assign(e, map[e.id]);
      }
      DETAIL_STATUS.set(key, 'loaded');
    })
    .catch(err => {
      console.warn('detail shard load failed for', key, err);
      DETAIL_STATUS.set(key, 'failed');
      DETAIL_PROMISES.delete(key);
      throw err;
    });
  DETAIL_PROMISES.set(key, p);
  return p;
}

async function ensureDetailLoadedForRows(rows) {
  // Returns the list of years that failed to load, so callers (CSV export)
  // can warn instead of exporting silently-incomplete rows.
  const years = Array.from(new Set(rows.map(r => String(r.year))));
  const results = await Promise.allSettled(years.map(ensureDetailLoaded));
  return years.filter((_, i) => results[i].status === 'rejected');
}

// ----------------------------- Utilities ---------------------------------

const escapeHtml = s => (s || '').replace(/[&<>"']/g,
  c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

// Only allow http(s)/mailto/relative hrefs. escapeHtml stops attribute
// break-out but NOT a javascript:/data: scheme, which would execute on click,
// so any URL coming from incident data must pass through here first.
const safeUrl = s => {
  const u = (s || '').trim();
  // Allow only http(s)/mailto/relative, and reject whitespace/angle-brackets
  // (a valid URL has none; malformed scraped ones can carry raw HTML).
  if (!/^(https?:|mailto:|\/|#|\.{0,2}\/)/i.test(u)) return '#';
  if (/[\s<>"']/.test(u)) return '#';
  return u;
};

const uniqSorted = arr => Array.from(new Set(arr)).sort();

const dateScore = e => (e.date || String(e.year || 0)).padEnd(10, '0');

const fmtNum = n => Number(n).toLocaleString();

const isFilterActive = key => {
  const v = filterValue(key);
  return v !== '' && v !== false && v != null;
};

function filterValue(key) {
  const el = els[key === 'cveOnly' ? 'cveOnly' : key];
  if (!el) return '';
  return el.type === 'checkbox' ? el.checked : el.value;
}

function setFilter(key, value) {
  const el = els[key === 'cveOnly' ? 'cveOnly' : key];
  if (!el) return;
  if (el.type === 'checkbox') el.checked = !!value;
  else el.value = value || '';
}

function activeFiltersCount() {
  return FILTER_KEYS.filter(isFilterActive).length;
}

// ----------------------------- URL state ---------------------------------

function readFiltersFromUrl() {
  const raw = location.hash.slice(1) || location.search.slice(1);
  if (!raw) return;
  const p = new URLSearchParams(raw);
  for (const k of FILTER_KEYS) {
    if (k === 'cveOnly') {
      if (p.get('cve_only') === '1') els.cveOnly.checked = true;
    } else if (p.has(k)) {
      setFilter(k, p.get(k));
    }
  }
  if (p.has('sort')) SORT_BY = p.get('sort');
  if (p.has('dir'))  SORT_DIR = p.get('dir') === 'asc' ? 'asc' : 'desc';
  if (p.has('page')) PAGE = Math.max(1, parseInt(p.get('page'), 10) || 1);
  if (p.has('ps')) {
    const n = parseInt(p.get('ps'), 10);
    if (PAGE_SIZE_OPTIONS.includes(n)) PAGE_SIZE = n;
  }
}

function writeFiltersToUrl() {
  const p = new URLSearchParams();
  for (const k of FILTER_KEYS) {
    const v = filterValue(k);
    if (k === 'cveOnly') { if (v) p.set('cve_only', '1'); }
    else if (v) p.set(k, v);
  }
  if (SORT_BY !== 'date' || SORT_DIR !== 'desc') {
    p.set('sort', SORT_BY); p.set('dir', SORT_DIR);
  }
  if (PAGE > 1) p.set('page', String(PAGE));
  if (PAGE_SIZE !== PAGE_SIZE_DEFAULT) p.set('ps', String(PAGE_SIZE));
  const qs = p.toString();
  history.replaceState(null, '', qs ? '#' + qs : location.pathname);
}

// ----------------------------- Filtering / sorting -----------------------

function matches(e) {
  if (els.year.value     && String(e.year) !== els.year.value) return false;
  if (els.severity.value && e.severity !== els.severity.value)  return false;
  if (els.llm.value      && !(e.owasp_llm || []).includes(els.llm.value)) return false;
  if (els.asi.value      && !(e.owasp_asi || []).includes(els.asi.value)) return false;
  if (els.vector.value   && e.attack_vector !== els.vector.value) return false;
  if (els.corpus.value   && e.corpus !== els.corpus.value)      return false;
  if (els.quality.value  && e.quality_tier !== els.quality.value) return false;
  if (els.cveOnly.checked && !(e.cve_ids || []).length)         return false;
  const q = els.q.value.trim().toLowerCase();
  if (q) {
    const hay = (
      e.id + ' ' + e.title + ' ' + (e.attack_vector || '') + ' ' +
      (e.affected || '') + ' ' +
      (e.cve_ids || []).join(' ') + ' ' +
      (e.owasp_llm || []).join(' ') + ' ' + (e.owasp_asi || []).join(' ') + ' ' +
      (e.primary_reference || '')
    ).toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function comparator() {
  const dir = SORT_DIR === 'asc' ? 1 : -1;
  if (SORT_BY === 'date') return (a, b) => dateScore(a).localeCompare(dateScore(b)) * dir;
  if (SORT_BY === 'severity') return (a, b) => ((SEV_RANK[a.severity] ?? -1) - (SEV_RANK[b.severity] ?? -1)) * dir;
  return (a, b) => 0;
}

// ----------------------------- Stats hero --------------------------------

function renderStats(allRows) {
  const total = allRows.length;
  // Replace the static "12,500+" hero fallback with the exact live count.
  const heroCount = document.getElementById('hero-count');
  if (heroCount) heroCount.textContent = fmtNum(total);
  const crit = allRows.filter(r => r.severity === 'Critical').length;
  const withCve = allRows.filter(r => (r.cve_ids || []).length).length;
  const curated = allRows.filter(r => r.quality_tier === 'curated').length;
  const reviewed = allRows.filter(r => r.quality_tier === 'reviewed').length;
  const years = uniqSorted(allRows.map(r => r.year).filter(Boolean));
  const latest = years[years.length - 1];
  const earliest = years[0];

  els.stats.innerHTML = `
    <div class="stat"><span class="num">${fmtNum(total)}</span><span class="label">Incidents</span><span class="sub">${earliest}–${latest}</span></div>
    <div class="stat"><span class="num sev-Critical" style="color: var(--critical)">${fmtNum(crit)}</span><span class="label">Critical</span><span class="sub">${(100*crit/total).toFixed(1)}% of total</span></div>
    <div class="stat"><span class="num">${fmtNum(withCve)}</span><span class="label">With CVE</span><span class="sub">${(100*withCve/total).toFixed(1)}% of total</span></div>
    <div class="stat"><span class="num">${fmtNum(curated + reviewed)}</span><span class="label">Curated + Reviewed</span><span class="sub">${fmtNum(curated)} curated</span></div>
    <div class="stat"><span class="num">${fmtNum(years.length)}</span><span class="label">Years</span><span class="sub">unbroken since ${earliest}</span></div>
  `;
}

// ----------------------------- Filter chips ------------------------------

function renderChips() {
  const parts = [];
  for (const k of FILTER_KEYS) {
    if (!isFilterActive(k)) continue;
    const v = filterValue(k);
    const display = v === true ? 'present' : String(v);
    parts.push(
      `<span class="chip" data-key="${k}">
        <span class="chip-key">${escapeHtml(FILTER_LABEL[k])}</span>
        ${escapeHtml(display)}
        <button type="button" aria-label="remove">×</button>
      </span>`
    );
  }
  if (parts.length) {
    parts.push('<button type="button" class="chip chip-clear" id="clear-filters">Clear all</button>');
  }
  els.chips.innerHTML = parts.join('');
  els.chips.querySelectorAll('.chip[data-key] button').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.parentElement.dataset.key;
      setFilter(key, key === 'cveOnly' ? false : '');
      PAGE = 1;
      EXPANDED.clear();
      rerender();
    });
  });
  const clear = document.getElementById('clear-filters');
  if (clear) {
    clear.addEventListener('click', () => {
      for (const k of FILTER_KEYS) setFilter(k, k === 'cveOnly' ? false : '');
      PAGE = 1;
      EXPANDED.clear();
      rerender();
    });
  }
}

// ----------------------------- Table -------------------------------------

function renderTable(slice, start) {
  const rows = slice.map((e, i) => {
    const cves = (e.cve_ids || []);
    const cveCell = cves.length === 0 ? '' :
      cves.length === 1 ? `<code>${escapeHtml(cves[0])}</code>` :
      `<code>${escapeHtml(cves[0])}</code> +${cves.length - 1}`;
    // Link the ID to the year-shard anchor (the per-incident standalone pages
    // were retired). stopPropagation so following the link doesn't also toggle
    // the row's expand handler.
    const incidentUrl = `incidents/${e.year}.html#${e.id.toLowerCase()}`;
    const idCell = `<a href="${incidentUrl}" onclick="event.stopPropagation()">${escapeHtml(e.id)}</a>`;
    const llm = (e.owasp_llm || []).join(', ');
    const asi = (e.owasp_asi || []).join(', ');
    const expanded = EXPANDED.has(e.id);
    const cls = expanded ? ' class="expanded"' : '';
    const detailId = `detail-${escapeHtml(e.id)}`;
    // Explicit, keyboard-and-screen-reader-reachable expand control (A4):
    // a native <button> gets Tab focus, Enter/Space activation and an
    // implicit "button" role for free, so no custom keydown handling or
    // ARIA role override on the <tr> itself is needed (overriding a <tr>'s
    // implicit "row" role to "button" would also orphan the ID link inside
    // it as nested interactive content). The whole-row click handler below
    // still toggles too, for mouse users -- the button calls
    // stopPropagation so a click on it doesn't double-toggle via bubbling.
    const toggleBtn = `<button type="button" class="row-toggle" aria-expanded="${expanded}" aria-controls="${detailId}" aria-label="${expanded ? 'Hide' : 'Show'} details for ${escapeHtml(e.id)}"><span aria-hidden="true">${expanded ? '−' : '+'}</span></button>`;
    const main = `<tr${cls} data-row="${e.id}">
      <td class="date"><span class="date-cell">${toggleBtn}${escapeHtml(e.date || String(e.year || ''))}</span></td>
      <td class="id">${idCell}</td>
      <td class="title-cell">${escapeHtml(e.title)}</td>
      <td><span class="sev-badge sev-${escapeHtml(e.severity)}">${escapeHtml(e.severity || '')}</span></td>
      <td class="llm col-llm">${escapeHtml(llm)}</td>
      <td class="asi col-asi">${escapeHtml(asi)}</td>
      <td class="cves col-cves">${cveCell}</td>
    </tr>`;
    if (!expanded) return main;
    return main + renderDetail(e, detailId);
  }).join('');

  els.body.innerHTML = rows || '<tr><td colspan="7" class="status">No matches.</td></tr>';

  function toggleRow(id) {
    if (EXPANDED.has(id)) {
      EXPANDED.delete(id);
      rerender();
      return;
    }
    EXPANDED.add(id);
    // Render immediately with whatever fields are already loaded (shows a
    // "Loading details…" placeholder if this row's year hasn't been
    // fetched yet), then re-render once the year's detail shard resolves
    // (or failed -- ensureDetailLoaded's rejection still re-renders so the
    // error state in renderDetail below can show).
    rerender();
    const row = DATA.find(r => r.id === id);
    if (row && !hasDetail(row)) {
      ensureDetailLoaded(row.year).then(rerender).catch(() => rerender());
    }
  }

  els.body.querySelectorAll('tr[data-row]').forEach(tr => {
    tr.addEventListener('click', () => toggleRow(tr.dataset.row));
  });
  els.body.querySelectorAll('.row-toggle').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      toggleRow(btn.closest('tr[data-row]').dataset.row);
    });
  });
  els.body.querySelectorAll('.detail-retry').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const year = btn.dataset.year;
      rerender(); // shows "Loading details…" immediately (status flips to 'loading' synchronously below)
      ensureDetailLoaded(year).then(rerender).catch(() => rerender());
    });
  });
}

function renderDetail(e, detailId) {
  const idAttr = detailId ? ` id="${detailId}"` : '';
  if (!hasDetail(e)) {
    const status = detailStatus(e.year);
    if (status === 'failed') {
      return `<tr class="detail"${idAttr}><td colspan="7"><div class="detail-body detail-error">
        <p class="hint" role="alert">
          Couldn't load details for this row (network error).
          <button type="button" class="btn-secondary detail-retry" data-year="${escapeHtml(String(e.year))}">Retry</button>
        </p>
      </div></td></tr>`;
    }
    return `<tr class="detail"${idAttr}><td colspan="7"><div class="detail-body">
      <p class="hint" aria-busy="true">Loading details…</p>
    </div></td></tr>`;
  }
  const cves = (e.cve_ids || []).map(c => `<code>${escapeHtml(c)}</code>`).join(' ');
  const tags = (e.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
  const llm = (e.owasp_llm || []).join(', ');
  const asi = (e.owasp_asi || []).join(', ');
  const refLink = e.primary_reference
    ? `<a href="${escapeHtml(safeUrl(e.primary_reference))}" rel="noopener" target="_blank" title="Cite this incident from its primary source, not this site">cite this incident ↗</a>`
    : '';
  const shardLink = `<a href="incidents/${e.year}.html#${e.id.toLowerCase()}">full details ↗</a>`;
  return `<tr class="detail"${idAttr}><td colspan="7"><div class="detail-body">
    <p>${escapeHtml(e.description || 'No description.')}</p>
    <div class="detail-meta">
      ${e.affected ? `<span><strong>Affected:</strong> ${escapeHtml(e.affected)}</span>` : ''}
      ${e.attack_vector ? `<span><strong>Vector:</strong> <code>${escapeHtml(e.attack_vector)}</code></span>` : ''}
      ${e.corpus ? `<span><strong>Corpus:</strong> ${escapeHtml(e.corpus)}</span>` : ''}
      ${e.quality_tier ? `<span><strong>Quality:</strong> ${escapeHtml(e.quality_tier)}</span>` : ''}
      ${llm ? `<span><strong>OWASP LLM:</strong> ${escapeHtml(llm)}</span>` : ''}
      ${asi ? `<span><strong>OWASP ASI:</strong> ${escapeHtml(asi)}</span>` : ''}
      ${cves ? `<span><strong>CVEs:</strong> ${cves}</span>` : ''}
    </div>
    ${tags ? `<div class="detail-tags">${tags}</div>` : ''}
    <div class="detail-meta" style="margin-top:0.5rem">${refLink} ${shardLink}</div>
  </div></td></tr>`;
}

function renderPager(total) {
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = (PAGE - 1) * PAGE_SIZE;
  els.pager.innerHTML = `
    <button id="prev" ${PAGE === 1 ? 'disabled' : ''}>← Previous</button>
    <button id="next" ${PAGE >= totalPages ? 'disabled' : ''}>Next →</button>
    <span class="pager-info">Page ${fmtNum(PAGE)} of ${fmtNum(totalPages)}</span>
  `;
  document.getElementById('prev').onclick = () => { PAGE = Math.max(1, PAGE - 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0, behavior:'smooth'}); };
  document.getElementById('next').onclick = () => { PAGE = Math.min(totalPages, PAGE + 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0, behavior:'smooth'}); };
}

function updateSortIndicators() {
  els.table.querySelectorAll('th.sortable').forEach(th => {
    th.classList.remove('sort-asc','sort-desc');
    if (th.dataset.sort === SORT_BY) th.classList.add(SORT_DIR === 'asc' ? 'sort-asc' : 'sort-desc');
  });
}

function rerender() {
  FILTERED = DATA.filter(matches).sort(comparator());
  const totalPages = Math.max(1, Math.ceil(FILTERED.length / PAGE_SIZE));
  if (PAGE > totalPages) PAGE = 1;
  const start = (PAGE - 1) * PAGE_SIZE;
  const slice = FILTERED.slice(start, start + PAGE_SIZE);

  renderTable(slice, start);
  renderPager(FILTERED.length);
  renderChips();
  updateSortIndicators();

  const total = FILTERED.length;
  els.status.textContent = total === 0
    ? 'No incidents match your filters.'
    : `${fmtNum(total)} of ${fmtNum(DATA.length)} incidents — showing ${fmtNum(start + 1)}–${fmtNum(start + slice.length)}.`;

  if (els.exportCsv) {
    els.exportCsv.disabled = total === 0;
    els.exportCsv.title = total === 0
      ? 'No matching rows to export'
      : `Download these ${fmtNum(total)} rows as CSV`;
  }

  writeFiltersToUrl();
}

// ----------------------------- Charts ------------------------------------

const CHART_ID = {
  year: 'chart-year', severity: 'chart-severity-stack',
  llm: 'chart-owasp-llm', asi: 'chart-owasp-asi',
  vectors: 'chart-vectors', vendors: 'chart-vendors',
};

const tooltipEl = document.createElement('div');
tooltipEl.className = 'chart-tooltip';
document.body.appendChild(tooltipEl);

function showTip(html, x, y) {
  tooltipEl.innerHTML = html;
  tooltipEl.style.left = x + 'px';
  tooltipEl.style.top = y + 'px';
  tooltipEl.classList.add('visible');
}
function hideTip() { tooltipEl.classList.remove('visible'); }

function svg(width, height, content) {
  return `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMinYMin meet">${content}</svg>`;
}

function topN(counts, n) {
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n);
}

function colorForSeverity(sev) { return SEV_VARS[sev] || 'var(--accent)'; }

function renderBarChart(containerId, items, onClick, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!items.length) { el.innerHTML = '<p class="hint">No data.</p>'; return; }

  const W = opts.width || 640;
  const ROW_H = opts.rowH || 20;
  const M_LEFT = opts.leftPad || 170;
  const M_RIGHT = 56;
  const M_TOP = 6;
  const M_BOTTOM = 6;
  const chartW = W - M_LEFT - M_RIGHT;
  const H = M_TOP + M_BOTTOM + items.length * ROW_H;
  const maxV = Math.max(...items.map(i => i.value));

  const bars = items.map((it, i) => {
    const y = M_TOP + i * ROW_H + 4;
    const bw = (it.value / maxV) * chartW;
    // Truncate to what actually fits the label gutter (M_LEFT) at the mono
    // label size (~6.8px/char), so labels never overflow the chart box.
    const maxChars = Math.max(6, Math.floor((M_LEFT - 12) / 6.8));
    const labelTrunc = it.label.length > maxChars ? it.label.slice(0, maxChars - 1) + '…' : it.label;
    const color = it.color || 'var(--bar)';
    const filterPayload = JSON.stringify(it.filter || null).replace(/"/g, '&quot;');
    return `
      <text class="row-label" x="${M_LEFT - 8}" y="${y + 13}" text-anchor="end">${escapeHtml(labelTrunc)}</text>
      <rect class="bar" x="${M_LEFT}" y="${y}" width="${bw}" height="${ROW_H - 8}"
        rx="3" fill="${color}"
        data-filter="${filterPayload}"
        data-tip="${escapeHtml(it.label)}: ${fmtNum(it.value)}"/>
      <text class="value-label" x="${M_LEFT + bw + 6}" y="${y + 13}">${fmtNum(it.value)}</text>
    `;
  }).join('');

  el.innerHTML = svg(W, H, bars);
  wireChart(el, onClick);
}

function renderColumnChart(containerId, items, onClick, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!items.length) { el.innerHTML = '<p class="hint">No data.</p>'; return; }
  const W = opts.width || 720;
  const H = opts.height || 200;
  const M_LEFT = 40, M_RIGHT = 10, M_TOP = 10, M_BOTTOM = 26;
  const chartW = W - M_LEFT - M_RIGHT;
  const chartH = H - M_TOP - M_BOTTOM;
  const maxV = Math.max(...items.map(i => i.value));
  const barW = chartW / items.length;

  const grid = [];
  for (let g = 0; g <= 4; g++) {
    const y = M_TOP + chartH * g / 4;
    const v = Math.round(maxV * (4 - g) / 4);
    grid.push(`<line class="gridline" x1="${M_LEFT}" y1="${y}" x2="${W - M_RIGHT}" y2="${y}"/>`);
    grid.push(`<text class="tick" x="${M_LEFT - 6}" y="${y + 3}" text-anchor="end">${fmtNum(v)}</text>`);
  }
  const bars = items.map((it, i) => {
    const bw = barW * 0.78;
    const x = M_LEFT + i * barW + (barW - bw) / 2;
    const bh = (it.value / maxV) * chartH;
    const y = M_TOP + chartH - bh;
    const filterPayload = JSON.stringify(it.filter || null).replace(/"/g, '&quot;');
    const labelEvery = items.length > 18 ? 2 : 1;
    const showLabel = (i === 0) || (i === items.length - 1) || (i % labelEvery === 0);
    return `
      <rect class="bar" x="${x}" y="${y}" width="${bw}" height="${bh}" rx="2"
        fill="${it.color || 'var(--bar)'}"
        data-filter="${filterPayload}"
        data-tip="${escapeHtml(it.label)}: ${fmtNum(it.value)}"/>
      ${showLabel ? `<text class="tick" x="${x + bw / 2}" y="${H - M_BOTTOM + 14}" text-anchor="middle">${escapeHtml(it.label)}</text>` : ''}
    `;
  }).join('');

  el.innerHTML = svg(W, H, grid.join('') + bars);
  wireChart(el, onClick);
}

function renderStackedColumnChart(containerId, years, byYearBySeverity, onClick) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const sevOrder = ['Critical','High','Medium','Low','Info'];
  const W = 720, H = 200;
  const M_LEFT = 40, M_RIGHT = 100, M_TOP = 10, M_BOTTOM = 26;
  const chartW = W - M_LEFT - M_RIGHT;
  const chartH = H - M_TOP - M_BOTTOM;
  const totals = years.map(y => sevOrder.reduce((a,s) => a + (byYearBySeverity[y][s] || 0), 0));
  const maxV = Math.max(...totals) || 1;
  const barW = chartW / years.length;

  const grid = [];
  for (let g = 0; g <= 4; g++) {
    const y = M_TOP + chartH * g / 4;
    const v = Math.round(maxV * (4 - g) / 4);
    grid.push(`<line class="gridline" x1="${M_LEFT}" y1="${y}" x2="${W - M_RIGHT}" y2="${y}"/>`);
    grid.push(`<text class="tick" x="${M_LEFT - 6}" y="${y + 3}" text-anchor="end">${fmtNum(v)}</text>`);
  }
  const bars = years.map((yr, i) => {
    const bw = barW * 0.78;
    const x = M_LEFT + i * barW + (barW - bw) / 2;
    let cumulative = 0;
    const segs = [];
    for (const sev of sevOrder) {
      const c = byYearBySeverity[yr][sev] || 0;
      if (!c) continue;
      const bh = (c / maxV) * chartH;
      const segY = M_TOP + chartH - cumulative - bh;
      segs.push(`<rect class="bar" x="${x}" y="${segY}" width="${bw}" height="${bh}"
        fill="${colorForSeverity(sev)}"
        data-filter='${JSON.stringify({ year: String(yr), severity: sev })}'
        data-tip="${escapeHtml(String(yr))} · ${sev}: ${fmtNum(c)}"/>`);
      cumulative += bh;
    }
    const labelEvery = years.length > 18 ? 2 : 1;
    const showLabel = (i === 0) || (i === years.length - 1) || (i % labelEvery === 0);
    return segs.join('') + (showLabel
      ? `<text class="tick" x="${x + bw / 2}" y="${H - M_BOTTOM + 14}" text-anchor="middle">${yr}</text>`
      : '');
  }).join('');
  // Legend
  const legend = sevOrder.map((sev, i) => {
    const ly = M_TOP + i * 18;
    const lx = W - M_RIGHT + 6;
    return `<rect x="${lx}" y="${ly}" width="11" height="11" fill="${colorForSeverity(sev)}"/>
      <text class="row-label" x="${lx + 16}" y="${ly + 9}">${sev}</text>`;
  }).join('');

  el.innerHTML = svg(W, H, grid.join('') + bars + legend);
  wireChart(el, onClick);
}

function wireChart(el, onClick) {
  const rect = () => el.getBoundingClientRect();
  el.querySelectorAll('.bar').forEach(bar => {
    bar.addEventListener('mousemove', ev => {
      const r = rect();
      showTip(bar.dataset.tip, ev.clientX, ev.clientY);
    });
    bar.addEventListener('mouseleave', hideTip);
    bar.addEventListener('click', () => {
      hideTip();
      try {
        const filt = JSON.parse(bar.dataset.filter || 'null');
        if (filt && onClick) onClick(filt);
      } catch (_) { /* ignore */ }
    });
  });
}

function applyChartFilter(patch) {
  // Apply chart-click filters on top of whatever is already set.
  for (const [k, v] of Object.entries(patch)) {
    if (k === 'cveOnly') els.cveOnly.checked = !!v;
    else if (els[k]) els[k].value = v;
  }
  PAGE = 1;
  EXPANDED.clear();
  rerender();
  document.querySelector('.filters-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

const isNarrow = () => window.innerWidth < 720;

function renderAllCharts() {
  // Per-year column chart
  const yearCounts = {};
  for (const e of DATA) if (e.year) yearCounts[e.year] = (yearCounts[e.year] || 0) + 1;
  const years = Object.keys(yearCounts).map(Number).sort((a,b) => a - b);
  const yearItems = years.map(y => ({ label: String(y), value: yearCounts[y], filter: { year: String(y) } }));
  renderColumnChart(CHART_ID.year, yearItems, applyChartFilter);

  // Severity composition over time (last 16 years that have data)
  const sevYears = years.slice(-16);
  const byYearBySev = {};
  for (const y of sevYears) byYearBySev[y] = { Critical: 0, High: 0, Medium: 0, Low: 0, Info: 0 };
  for (const e of DATA) {
    if (byYearBySev[e.year]) byYearBySev[e.year][e.severity || 'Medium']++;
  }
  renderStackedColumnChart(CHART_ID.severity, sevYears, byYearBySev, applyChartFilter);

  // OWASP LLM bar chart
  const llmCounts = {};
  Object.keys(LLM_NAMES).forEach(k => llmCounts[k] = 0);
  for (const e of DATA) for (const c of e.owasp_llm || []) llmCounts[c] = (llmCounts[c] || 0) + 1;
  const llmItems = Object.keys(LLM_NAMES).map(k => ({
    label: `${k} · ${LLM_NAMES[k]}`, value: llmCounts[k] || 0, filter: { llm: k },
  })).sort((a,b) => b.value - a.value);
  renderBarChart(CHART_ID.llm, llmItems, applyChartFilter, { rowH: 24, leftPad: 250 });

  // OWASP ASI bar chart
  const asiCounts = {};
  Object.keys(ASI_NAMES).forEach(k => asiCounts[k] = 0);
  for (const e of DATA) for (const c of e.owasp_asi || []) asiCounts[c] = (asiCounts[c] || 0) + 1;
  const asiItems = Object.keys(ASI_NAMES).map(k => ({
    label: `${k} · ${ASI_NAMES[k]}`, value: asiCounts[k] || 0, filter: { asi: k },
  })).sort((a,b) => b.value - a.value);
  renderBarChart(CHART_ID.asi, asiItems, applyChartFilter, { rowH: 24, leftPad: 250 });

  // Top attack vectors — fewer rows on narrow viewports
  const vecCounts = {};
  for (const e of DATA) {
    const v = e.attack_vector || 'other';
    vecCounts[v] = (vecCounts[v] || 0) + 1;
  }
  const vecItems = topN(vecCounts, isNarrow() ? 6 : 12).map(([k, v]) => ({
    label: k, value: v, filter: { vector: k },
  }));
  renderBarChart(CHART_ID.vectors, vecItems, applyChartFilter, { rowH: 20, leftPad: 160 });

  // Top affected vendors / products (extracted from the `affected` field)
  const vendorCounts = {};
  for (const e of DATA) {
    const text = (e.affected || '').trim();
    if (!text) continue;
    // Pull out the first comma-separated chunk and normalise common noise.
    const first = text.split(/[,;|]/)[0].trim();
    if (!first || first.length > 60) continue;
    const key = first.replace(/\s+v?\d+(\.\d+)*$/, '').trim();
    vendorCounts[key] = (vendorCounts[key] || 0) + 1;
  }
  const vendorItems = topN(vendorCounts, isNarrow() ? 6 : 12).map(([k, v]) => ({
    label: k, value: v, filter: { q: k },
  }));
  renderBarChart(CHART_ID.vendors, vendorItems, applyChartFilter, { rowH: 20, leftPad: 190 });
}

// Re-render charts when the viewport crosses the narrow/wide boundary
// so the top-N counts adjust on rotation / window resize.
let _wasNarrow = null;
window.addEventListener('resize', () => {
  const n = isNarrow();
  if (n !== _wasNarrow && DATA.length) {
    _wasNarrow = n;
    renderAllCharts();
  }
}, { passive: true });

// ----------------------------- CSV export --------------------------------

const CSV_COLUMNS = [
  ['id',                'ID'],
  ['date',              'Date'],
  ['year',              'Year'],
  ['title',             'Title'],
  ['severity',          'Severity'],
  ['attack_vector',     'Attack Vector'],
  ['affected',          'Affected'],
  ['corpus',            'Corpus'],
  ['quality_tier',      'Quality'],
  ['owasp_llm',         'OWASP LLM'],
  ['owasp_asi',         'OWASP ASI'],
  ['nist_ai_rmf',       'NIST AI RMF'],
  ['mitre_atlas',       'MITRE ATLAS'],
  ['cve_ids',           'CVEs'],
  ['tags',              'Tags'],
  ['primary_reference', 'Primary Reference'],
  ['description',       'Description'],
];

function csvCell(value) {
  if (value == null) return '';
  if (Array.isArray(value)) value = value.join('; ');
  const s = String(value);
  // Escape per RFC 4180: wrap in quotes and double internal quotes if the
  // cell contains comma, quote, or newline.
  if (/[",\r\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

async function exportFilteredAsCsv() {
  if (!FILTERED.length) return;
  // CSV includes detail-only columns (description, NIST/ATLAS mappings);
  // those live in per-year lazy shards, so make sure every year present in
  // the filtered set is loaded before building rows. This is the one path
  // that can need every shard at once (a filter matching all years), which
  // is why it stays an explicit, user-initiated action rather than
  // something the initial page load or a single row-expand ever triggers.
  const btn = els.exportCsv;
  const originalLabel = btn ? btn.textContent : null;
  if (btn) { btn.disabled = true; btn.textContent = 'Preparing export…'; }
  try {
    const failedYears = await ensureDetailLoadedForRows(FILTERED);
    if (failedYears.length) {
      // Previously this was silent: Promise.allSettled swallowed the
      // rejection and the export completed looking normal while rows from
      // the failed year(s) had blank Description/Primary Reference/Tags/
      // NIST AI RMF/MITRE ATLAS cells (WS6-T5 design-pass report, defect
      // A3 -- measured: a 5,401-row export with one shard missing produced
      // 5,377/5,401 empty Description cells and 4,509/5,401 empty NIST AI
      // RMF cells, with the button returning to normal and no error).
      // Ask before shipping a CSV the user would otherwise have no reason
      // to distrust.
      const proceed = window.confirm(
        `Couldn't load full details for ${failedYears.length} year` +
        `${failedYears.length === 1 ? '' : 's'} (${failedYears.join(', ')}). ` +
        `Rows from ${failedYears.length === 1 ? 'that year' : 'those years'} will export with ` +
        `blank Description / Primary Reference / Tags / NIST AI RMF / MITRE ATLAS cells. ` +
        `Export anyway?`
      );
      if (!proceed) return;
    }

    const lines = [];
    lines.push(CSV_COLUMNS.map(c => csvCell(c[1])).join(','));
    for (const row of FILTERED) {
      lines.push(CSV_COLUMNS.map(c => csvCell(row[c[0]])).join(','));
    }
    // Prepend UTF-8 BOM so Excel opens it as UTF-8.
    const blob = new Blob(['﻿' + lines.join('\r\n')],
      { type: 'text/csv;charset=utf-8' });
    const today = new Date().toISOString().slice(0, 10);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `genai-incidents-${today}-${FILTERED.length}rows.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 0);
  } finally {
    if (btn) { btn.disabled = FILTERED.length === 0; btn.textContent = originalLabel; }
  }
}

// ----------------------------- Integrity note ------------------------------
// GitHub Pages has no published SLA for content integrity, so the served
// data files' SHA-256 hashes are published alongside them (see
// scripts/gen_data_integrity.py + docs/data/SHA256SUMS) and surfaced here so
// a visitor can verify a downloaded copy without leaving the page. Loaded
// after the main render so a slow/failed fetch never blocks the table.
async function loadIntegrityNote() {
  const el = document.getElementById('integrity-note');
  if (!el) return;
  try {
    const r = await fetch('data/SHA256SUMS');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const text = await r.text();
    const line = text.split('\n').find(l => l.includes('incidents.min.json'));
    const hash = line ? line.trim().split(/\s+/)[0] : null;
    if (hash) {
      el.innerHTML = `<code title="${escapeHtml(hash)}">sha256:${escapeHtml(hash.slice(0, 12))}…</code> ` +
        `<a href="data/SHA256SUMS">verify ↗</a>`;
    } else {
      el.innerHTML = `<a href="data/SHA256SUMS">SHA-256 checksums ↗</a>`;
    }
  } catch (e) {
    // Non-fatal: the checksums file link in the header still works even if
    // this fetch-and-summarize fails.
    el.textContent = '';
  }
}

// ----------------------------- Bootstrap ---------------------------------

function populateOptions(select, values) {
  const frag = document.createDocumentFragment();
  for (const v of values) {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    frag.appendChild(opt);
  }
  select.appendChild(frag);
}

async function init() {
  try {
    // The initial load is the trimmed core payload (table/filter/chart
    // fields only -- see scripts/gen_docs_core_data.py). Full per-incident
    // description/reference/tags/taxonomy-mapping fields are fetched lazily
    // per publication year, on row-expand or CSV export (see
    // ensureDetailLoaded above). The full, untrimmed data/incidents.min.json
    // is still published unchanged for direct download (see the JSON link
    // in the header) and is what the integrity manifest hashes.
    const r = await fetch('data/incidents.core.json');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const payload = await r.json();
    DATA = payload.incidents || [];

    populateOptions(els.year,
      uniqSorted(DATA.map(e => String(e.year))).filter(Boolean).reverse());
    populateOptions(els.llm,
      uniqSorted(DATA.flatMap(e => e.owasp_llm || [])));
    populateOptions(els.asi,
      uniqSorted(DATA.flatMap(e => e.owasp_asi || [])));
    populateOptions(els.vector,
      uniqSorted(DATA.map(e => e.attack_vector).filter(Boolean)));

    // Populate page-size selector (URL state may already have set PAGE_SIZE)
    for (const n of PAGE_SIZE_OPTIONS) {
      const opt = document.createElement('option');
      opt.value = String(n);
      opt.textContent = n.toLocaleString();
      els.pageSize.appendChild(opt);
    }

    // On a narrow viewport, titles wrap to several lines each (the LLM/ASI/
    // CVE columns are already dropped below 640px -- see style.css -- so
    // Title gets more of the remaining width, not less), so the 250-row
    // desktop default would mean tens of thousands of pixels of scroll per
    // page. Start narrow viewports at the smallest page size instead;
    // `readFiltersFromUrl()` below still overrides this if the URL already
    // has an explicit `ps` param (e.g. a shared link), so this is only a
    // first-load default, never a forced setting.
    if (window.innerWidth < 640) PAGE_SIZE = PAGE_SIZE_OPTIONS[0];

    readFiltersFromUrl();
    els.pageSize.value = String(PAGE_SIZE);
    els.pageSize.addEventListener('change', () => {
      const n = parseInt(els.pageSize.value, 10);
      if (PAGE_SIZE_OPTIONS.includes(n)) {
        PAGE_SIZE = n;
        PAGE = 1;
        rerender();
      }
    });

    // CSV export
    if (els.exportCsv) {
      els.exportCsv.addEventListener('click', exportFilteredAsCsv);
    }

    // Back-to-top FAB
    if (els.backToTop) {
      window.addEventListener('scroll', () => {
        els.backToTop.classList.toggle('visible', window.scrollY > 600);
      }, { passive: true });
      els.backToTop.addEventListener('click', (ev) => {
        ev.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // Light/dark theme toggle. The <head> script already set data-theme from
    // localStorage / OS preference before paint; here we just wire the button
    // and re-render the SVG charts so their var()-driven fills repaint in the
    // new palette.
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const next = document.documentElement.getAttribute('data-theme') === 'light'
          ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
        renderAllCharts();
        if (DATA.length) renderStats(DATA);
      });
    }

    renderStats(DATA);
    renderAllCharts();

    // Filter change handlers
    for (const k of FILTER_KEYS) {
      const el = els[k === 'cveOnly' ? 'cveOnly' : k];
      if (!el) continue;
      const ev = (el.type === 'checkbox' || el.tagName === 'SELECT') ? 'change' : 'input';
      el.addEventListener(ev, () => {
        PAGE = 1;
        EXPANDED.clear();
        rerender();
      });
    }
    // Sortable headers
    els.table.querySelectorAll('th.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const next = th.dataset.sort;
        if (SORT_BY === next) SORT_DIR = SORT_DIR === 'asc' ? 'desc' : 'asc';
        else { SORT_BY = next; SORT_DIR = next === 'severity' ? 'desc' : 'desc'; }
        rerender();
      });
    });

    els.meta.textContent =
      `Dataset v${payload.version || '?'} · generated ${payload.generated || '?'} · ${fmtNum(DATA.length)} incidents`;

    rerender();
    loadIntegrityNote();
  } catch (err) {
    els.status.textContent = 'Failed to load dataset: ' + err.message;
    console.error(err);
  }
}

init();
