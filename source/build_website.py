import json
import urllib.request
import time
import concurrent.futures
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR, DATA_DIR
from .data_loader import load_inscriptions

ROOT_INDEX = Path("index.html")
WEBSITE_DIR = Path("website")
INSCRIPTIONS_DIR = WEBSITE_DIR / "inscriptions"
ASSETS_DIR = WEBSITE_DIR / "assets"
TEMPLATES_DIR = Path(__file__).parent / "templates"

REGION_DATA = {
    "Attica": {"uri": "https://pleiades.stoa.org/places/579888", "coords": [38.0, 23.8]},
    "Peloponnese": {"uri": "https://pleiades.stoa.org/places/570599", "coords": [37.5, 22.4]},
    "Boeotia": {"uri": "https://pleiades.stoa.org/places/540677", "coords": [38.3, 23.1]},
    "Thessaly": {"uri": "https://pleiades.stoa.org/places/541136", "coords": [39.5, 22.2]},
    "Epirus": {"uri": "https://pleiades.stoa.org/places/540776", "coords": [39.6, 20.8]},
    "Macedonia": {"uri": "https://pleiades.stoa.org/places/491656", "coords": [40.7, 22.5]},
    "Thrace": {"uri": "https://pleiades.stoa.org/places/501616", "coords": [41.5, 25.5]},
    "Illyria": {"uri": "https://pleiades.stoa.org/places/481865", "coords": [40.5, 19.8]},
    "Crete": {"uri": "https://pleiades.stoa.org/places/589748", "coords": [35.2, 24.9]},
    "Aegean Islands": {"uri": "https://pleiades.stoa.org/places/579885", "coords": [37.0, 25.5]},
    "Delos": {"uri": "https://pleiades.stoa.org/places/599588", "coords": [37.39, 25.26]},
    "Asia Minor": {"uri": "https://pleiades.stoa.org/places/638753", "coords": [39.0, 32.0]},
    "Caria": {"uri": "https://pleiades.stoa.org/places/638803", "coords": [37.5, 28.0]},
    "Ionia": {"uri": "https://pleiades.stoa.org/places/550597", "coords": [38.5, 27.5]},
    "Sicily": {"uri": "https://pleiades.stoa.org/places/462492", "coords": [37.5, 14.0]},
    "Italy": {"uri": "https://pleiades.stoa.org/places/1052", "coords": [42.0, 12.5]}
}

PLEIADES_CACHE_FILE = DATA_DIR / "pleiades_cache.json"
PLEIADES_CACHE = {}

def load_pleiades_cache():
    global PLEIADES_CACHE
    if PLEIADES_CACHE_FILE.exists():
        try:
            with open(PLEIADES_CACHE_FILE, 'r', encoding='utf-8') as f:
                PLEIADES_CACHE = json.load(f)
        except Exception:
            PLEIADES_CACHE = {}

def save_pleiades_cache():
    with open(PLEIADES_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(PLEIADES_CACHE, f, ensure_ascii=False)

def fetch_pleiades_coords(uri):
    if not uri or "pleiades.stoa.org" not in uri: return None
    if uri in PLEIADES_CACHE: return PLEIADES_CACHE[uri]
    
    try:
        api_url = f"{uri.rstrip('/')}/json"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'AGKI-Tagging-Tool/1.0'})
        print(f"DEBUG: Fetching {api_url}...")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                content = json.loads(response.read().decode())
                if 'reprPoint' in content:
                    lon, lat = content['reprPoint']
                    PLEIADES_CACHE[uri] = [lat, lon]
                    return PLEIADES_CACHE[uri]
    except Exception:
        pass
    
    PLEIADES_CACHE[uri] = None
    return None

def get_coords(name, uri=None):
    # 1. Try explicit URI
    if uri:
        c = fetch_pleiades_coords(uri)
        if c: return c
        
    # 2. Try looking up URI by name in REGION_DATA
    if name and name in REGION_DATA:
        entry = REGION_DATA[name]
        if isinstance(entry, dict) and 'uri' in entry:
            c = fetch_pleiades_coords(entry['uri'])
            if c: return c
            
    return None

# Combined Gazetteer
GAZETTEER = REGION_DATA.copy()
GAZETTEER.update({
    "Athen": [37.98, 23.72],
    "Eleusis": [38.04, 23.54],
    "Brauron": [37.92, 23.99],
    "Sparta": [37.07, 22.43],
    "Korinth": [37.90, 22.88],
    "Olympia": [37.63, 21.63],
    "Theben": [38.32, 23.32],
    "Tanagra": [38.31, 23.53],
    "Delos (City)": [37.39, 25.26],
    "Sanctuary of Apollo": [37.40, 25.27],
    "Ephesos": [37.94, 27.36],
    "Milet": [37.53, 27.27],
    "Pergamon": [37.93, 27.18],
    "Knossos": [35.29, 25.16],
    "Pella": [40.76, 22.52]
})

def load_json(path):
    if not path.exists(): return None
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def load_taxonomy():
    with open(TAXONOMY_DIR / "taxonomy.json", 'r', encoding='utf-8') as f: return json.load(f)

def sync_static_pages():
    index_template = TEMPLATES_DIR / "index.html"
    if index_template.exists():
        ROOT_INDEX.write_text(index_template.read_text(encoding="utf-8"), encoding="utf-8")
    for name in ("search.html", "explore.html"):
        template = TEMPLATES_DIR / name
        if not template.exists():
            continue
        target = WEBSITE_DIR / name
        target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")

def generate_detail_page(merged_data):
    import html
    phi_id = merged_data['id']
    text_content = merged_data['input'].get('text', '').replace('\r\n', '\n').replace('\r', '\n')
    
    # Provenance
    prov_list = merged_data['output'].get('provenance', [])
    if prov_list:
        breadcrumbs = []
        for p in prov_list:
            label = p['name']
            if p.get('uri'):
                label = '<a href="{}" target="_blank" title="View in Pleiades">{}</a>'.format(p['uri'], p['name'])
            breadcrumbs.append(label)
        region_html = " &gt; ".join(breadcrumbs)
    else:
        region_name = merged_data['input'].get('region_main', 'N/A')
        region_html = "<strong>{}</strong>".format(region_name)

    # Themes
    themes_html = ""
    for t in merged_data.get('output', {}).get('themes', []):
        h = t['hierarchy']
        path_str = " > ".join(filter(None, [h.get('domain'), h.get('subdomain'), h.get('category'), h.get('subcategory')]))
        conf = t.get('confidence', 1.0)
        conf_color = "green" if conf > 0.8 else ("orange" if conf > 0.6 else "red")
        quote = t.get('quote', '') or ''
        safe_quote = html.escape(quote).replace('"', '&quot;')
        
        ambiguity_html = ""
        if t.get('is_ambiguous'):
            note = html.escape(t.get('ambiguity_note', ''))
            ambiguity_html = f'<span class="badge orange" title="{note}" style="font-size:0.7rem; vertical-align:middle; margin-left:0.5rem; cursor:help;">⚠️ Ambiguous</span>'

        themes_html += """
        <div class="theme-card" onmouseover="highlightQuote('{quote}')" onmouseout="clearHighlight()">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <a href=\"../search.html?theme={path_encoded}" class="tag domain-tag" style="text-decoration:none;">{domain}</a>
                    <span class="badge {conf_color}" style="font-size:0.7rem; vertical-align:middle; margin-left:0.5rem;">{conf_pct}% Conf.</span>
                    {ambiguity}
                    <div class="theme-path">{path}</div>
                    <div class="theme-label">{label}</div>
                </div>
                <div class="evidence-box">
                    <p class="evidence-quote">Evidence: "{orig_quote}"</p>
                </div>
            </div>
        </div>
        """.format(
            quote=safe_quote,
            path_encoded=html.escape(path_str.replace(" > ", "/")),
            domain=h.get('domain', 'Unclassified'),
            conf_color=conf_color,
            conf_pct=int(conf*100),
            ambiguity=ambiguity_html,
            path=path_str,
            label=t['label'],
            orig_quote=html.escape(quote)
        )

    # Entities
    entities = merged_data.get('output', {}).get('entities', {})
    persons_html = ""
    for p in entities.get('persons', []):
        persons_html += '<a href="../search.html?q={}" class="tag entity-tag" style="text-decoration:none;">👤 {} <small>({})</small></a>'.format(html.escape(p["name"]), html.escape(p["name"]), html.escape(p.get("role", "")))
    places_html = ""
    for p in entities.get('places', []):
        places_html += '<a href="../index_places.html" class="tag entity-tag" style="text-decoration:none;">📍 {} <small>({})</small></a>'.format(html.escape(p["name"]), html.escape(p.get("type", "")))
    deities_html = ""
    for d in entities.get('deities', []):
        name = d['name'] if isinstance(d, dict) else d
        deities_html += '<a href="../index_deities.html" class="tag entity-tag" style="text-decoration:none;">⚡ {}</a>'.format(html.escape(name))

    # Global Analysis Summary
    global_rationale = merged_data.get('output', {}).get('rationale') or 'No additional analysis provided.'

    # Model version
    model_version = merged_data.get('output', {}).get('model') or 'Unknown'

    # Original Text (Strict Line-by-Line)
    raw_greek_html = html.escape(text_content)
    lines = text_content.split('\n')
    line_nums = [str(i+1) if (i+1)%5==0 or i==0 else "" for i in range(len(lines))]
    line_nums_html = "\n".join(line_nums)

    # Assemble HTML
    html_head = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PHI-{} - AGKI</title>
  <link rel="stylesheet" href="../assets/css/main.css">
  <style>
    /* Custom Scrollbar Styling */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.05); }}
    ::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #aaa; }}

    .page-container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
    .back-link {{ display: inline-block; margin-bottom: 1rem; color: var(--primary); font-weight: 600; }}
    .text-viewer-original {{ display: grid; grid-template-columns: 40px 1fr; gap: 2rem; font-family: "New Athena Unicode", "Gentium Plus", "Times New Roman", serif; font-size: 1.25rem; line-height: 1.6; background: var(--panel); padding: 2rem; border: 1px solid var(--border); border-radius: 4px; margin-bottom: 2rem; color: var(--text); }}
    .line-numbers {{ text-align: right; color: var(--muted); font-size: 1.25rem; line-height: 1.6; user-select: none; opacity: 0.5; font-family: inherit; white-space: pre; padding-right: 1rem; border-right: 1px solid var(--border); }}
    .greek-content {{ white-space: pre-wrap; word-break: break-word; padding-left: 1rem; }}
    .highlight-evidence {{ background-color: var(--accent); color: white; border-radius: 2px; padding: 0 2px; }}
    .theme-card {{ background: var(--panel); padding: 1rem 1.5rem; border-left: 4px solid var(--primary); margin-bottom: 0.75rem; border: 1px solid var(--border); border-left-width: 4px; }}
    .ai-analysis-box {{ background: rgba(31, 167, 163, 0.05); padding: 2rem; border-radius: 8px; border: 1px solid var(--border); margin-top: 2rem; }}
    .evidence-box {{ max-width: 500px; text-align: right; }}
    .evidence-quote {{ font-size: 0.85rem; font-style: italic; color: var(--muted); margin: 0; }}
    .badge.green {{ background: #e6f4ea; color: #137333; border-color: #137333; }}
    .badge.orange {{ background: #fef7e0; color: #b06000; border-color: #b06000; }}
    .badge.red {{ background: #fce8e6; color: #c5221f; border-color: #c5221f; }}
    .entity-tag {{ background: rgba(217, 123, 61, 0.1); color: var(--accent-2); margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.9rem; border: 1px solid rgba(217, 123, 61, 0.2); }}
    .split-container {{ display: block; }}
    .split-container.active {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }}
    .split-container.active .split-col-right {{ position: sticky; top: 20px; max-height: 90vh; overflow-y: auto; padding-right: 10px; }}
  </style>
  <script>
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    function toggleSplitView() {{
        const container = document.getElementById('main-content');
        const btn = document.getElementById('splitViewBtn');
        container.classList.toggle('active');
        btn.textContent = container.classList.contains('active') ? 'View: Split' : 'View: Standard';
    }}

    function copyCitation() {{
        const citation = "AGKI Project. (2026). Inscription PHI-{} . Retrieved from " + window.location.href;
        navigator.clipboard.writeText(citation);
        alert("Citation copied to clipboard!");
    }}

    function highlightQuote(quote) {{
        const container = document.querySelector('.greek-content');
        if (!container || !quote) return;
        if (!container.dataset.original) container.dataset.original = container.innerHTML;
        else container.innerHTML = container.dataset.original;
        
        const regex = new RegExp(quote.trim().replace(/\s+/g, '\\s+'), 'g');
        container.innerHTML = container.innerHTML.replace(regex, match => `<mark class="highlight-evidence">${{match}}</mark>`);
    }}

    function clearHighlight() {{
        const container = document.querySelector('.greek-content');
        if (container && container.dataset.original) container.innerHTML = container.dataset.original;
    }}

    function updateFontSize(size) {{
        const v = document.getElementById('original-view');
        if(v) v.style.fontSize = size + 'px';
    }}

    function openReportModal() {{ document.getElementById('reportModal').style.display = 'block'; }}
    function closeReportModal() {{ document.getElementById('reportModal').style.display = 'none'; }}
    function sendReport() {{
        const category = document.getElementById('reportCategory').value;
        const desc = document.getElementById('reportDesc').value;
        const fix = document.getElementById('reportFix').value;
        const subject = `AGKI Error Report: PHI-{}`;
        const body = `Category: ${{category}}%0D%0ADescription: ${{desc}}%0D%0AProposed Fix: ${{fix}}`;
        window.location.href = `mailto:admin@agki-project.org?subject=${{encodeURIComponent(subject)}}&body=${{body}}`;
        closeReportModal();
    }}
  </script>
</head>
""".format(phi_id, phi_id, phi_id)

    html_body = r"""
<body>
  <header class="site-header">
    <div class="brand"><h1><a href="../../index.html">AGKI Tagging Tool</a></h1></div>
    <nav class="nav-links">
        <a href="../../index.html" class="nav-item">Home</a>
        <a href="../search.html" class="nav-item">Search</a>
        <a href="../explore.html" class="nav-item">Explore</a>
        <a href="../compare.html" class="nav-item">Compare</a>
        <a href="../network.html" class="nav-item">Network</a>
        <a href="../matrix.html" class="nav-item">Matrix</a>
        <a href="../indices.html" class="nav-item">Indices</a>
    </nav>
    <div class="header-controls">
        <button class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn">Dark Mode</button>
    </div>
  </header>

  <script>
    const themeBtn = document.getElementById('themeBtn');
    function updateThemeBtn() {{
        const current = document.documentElement.getAttribute('data-theme');
        if(themeBtn) themeBtn.textContent = current === 'light' ? 'Dark Mode' : 'Light Mode';
    }}
    updateThemeBtn();
    window.toggleTheme = function() {{
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeBtn();
    }}
  </script>

  <main class="page-container inscription-page">
    <div class="inscription-toolbar">
        <a href="../search.html" class="back-link"><- Back to Dashboard</a>
        <div class="inscription-actions">
            <button id="splitViewBtn" onclick="toggleSplitView()" class="button secondary compact">View: Standard</button>
            <button onclick="openReportModal()" class="button error compact">Report Error</button>
        </div>
    </div>

    <!-- Report Modal -->
    <div id="reportModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000;">
        <div style="background:var(--panel); width:90%; max-width:500px; margin:10% auto; padding:2rem; border-radius:8px; border:1px solid var(--border);">
            <h3>Report Error for PHI-{}</h3>
            <label>Error Category</label>
            <select id="reportCategory" style="width:100%; padding:0.5rem; margin-bottom:1rem;">
                <option value="Incorrect Tag">Incorrect Tag / Theme</option>
                <option value="Missing Entity">Missing Person / Place</option>
                <option value="Translation Error">Translation / Text Issue</option>
                <option value="Other">Other</option>
            </select>
            <label>Description</label>
            <textarea id="reportDesc" rows="3" style="width:100%; margin-bottom:1rem;"></textarea>
            <label>Proposed Fix</label>
            <textarea id="reportFix" rows="2" style="width:100%; margin-bottom:1.5rem;"></textarea>
            <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
                <button onclick="closeReportModal()" class="button secondary">Cancel</button>
                <button onclick="sendReport()" class="button">Create Email Report</button>
            </div>
        </div>
    </div>

    <div id="main-content" class="split-container">
        <div class="split-col-left">
            <section class="inscription-hero">
                <div class="inscription-title-row">
                    <h2>Inscription PHI-{}</h2>
                    <div class="inscription-actions">
                        <button onclick="copyCitation()" class="button secondary compact">Cite</button>
                        <a href="https://epigraphy.packhum.org/text/{}" target="_blank" class="button secondary compact">View on PHI</a>
                    </div>
                </div>
                <div class="inscription-meta">
                    <div class="meta-item"><div class="label">Provenance</div><div class="meta-value">{}</div></div>
                    <div class="meta-item"><div class="label">Date</div><div class="meta-value">{}</div></div>
                    <div class="meta-item"><div class="label">Completeness</div><div class="meta-value"><span class="badge info">{}</span></div></div>
                    <div class="meta-item"><div class="label">Tagged by</div><div class="meta-value"><span class="badge" style="background:rgba(12,140,136,0.15); color:#0c8c88; border:1px solid #0c8c88;">{}</span></div></div>
                </div>
            </section>
            <div class="inscription-title-row">
                <h3>Original Text</h3>
                <div class="font-size-control">
                    <input type="range" min="14" max="32" value="20" oninput="updateFontSize(this.value)">
                </div>
            </div>
            <div id="original-view" class="text-viewer-original">
                <div class="line-numbers">{}</div>
                <div class="greek-content">{}</div>
            </div>
        </div>
        <div class="split-col-right">
            <h3>Thematic Analysis</h3>
            {}
            <div style="margin-top:2rem;"><h3>Entities</h3><div>{}</div></div>
            <div class="ai-analysis-box"><h3>AI Analysis Summary</h3><p>{}</p></div>
        </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="footer-content">
      © 2026 Florian Wachter | Private Non-Profit Research Project | 
      <a href="https://github.com/paxetheninja/AGKI-PM-TaggingEpigraphy" target="_blank">GitHub</a>
    </div>
    <div class="footer-legal">
      Impressum: Privates Forschungsprojekt. Verantwortlich: Florian Wachter, Institut für Antike, Goethestraße 19, 8010 Graz. Kontakt: florian.wachter@uni-graz.at. Keine Gewähr für die Richtigkeit der Daten.
    </div>
  </footer>
</body>
</html>
    """.format(
        phi_id, phi_id, phi_id,
        region_html,
        merged_data['input'].get('date_str', 'N/A'),
        merged_data['output'].get('completeness', 'unknown'),
        model_version,
        line_nums_html,
        raw_greek_html,
        themes_html if themes_html else "<p class='muted'>No themes assigned.</p>",
        persons_html + places_html + deities_html,
        html.escape(global_rationale).replace('\n', '<br>')
    )

    return html_head + html_body

def generate_indices_page(deities, persons, places):
    import html

    def dict_to_rows(d, is_person=False, is_place=False):
        sorted_keys = sorted(d.keys())
        rows = ""
        for k in sorted_keys:
            val = d[k]
            count = val if isinstance(val, int) else val['count']
            extra = ""
            if is_person:
                extra = f"<td>{html.escape(val['role'] or '')}</td>"
            if is_place:
                extra = f"<td>{html.escape(val['type'] or '')}</td>"
            uri_link = ""
            uri = val.get('uri') if isinstance(val, dict) else None
            if uri:
                uri_link = f' <a href="{uri}" target="_blank" class="index-link">Link</a>'
            rows += f"<tr><td>{html.escape(k)}{uri_link}</td>{extra}<td>{count}</td></tr>"
        return rows

    def get_template(title, content, active_sub=""):
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - AGKI Epigraphy Tool</title>
  <link rel="stylesheet" href="assets/css/main.css">
  <script>
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
  </script>
  <style>
    .page-container {{ max-width: none; width: 100%; margin: 0 auto; padding: 2rem; }}
    .index-header {{ display: flex; align-items: baseline; gap: 1rem; flex-wrap: wrap; }}
    .index-nav {{ display: flex; gap: 0.75rem; margin: 1.25rem 0 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem; flex-wrap: wrap; }}
    .index-nav a {{ text-decoration: none; color: var(--muted); font-weight: 600; padding: 0.4rem 0.9rem; border-radius: 20px; border: 1px solid var(--border); }}
    .index-nav a:hover {{ background: var(--panel); color: var(--text); }}
    .index-nav a.active {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
    .index-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }}
    .index-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1.75rem; }}
    .index-toolbar {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }}
    .index-search input {{ min-width: 240px; }}
    .index-table {{ margin-top: 1rem; overflow: auto; border-radius: 8px; border: 1px solid var(--border); background: var(--panel); position: relative; }}
    .index-empty {{ display: none; align-items: center; justify-content: center; padding: 2rem; color: var(--muted); }}
    .index-link {{ color: var(--primary); font-size: 0.85rem; margin-left: 0.35rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    th, td {{ text-align: left; padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; background: var(--panel); position: sticky; top: 0; }}
    tbody tr:hover {{ background: rgba(193, 104, 60, 0.08); }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="brand"><h1><a href="../index.html">AGKI Tagging Tool</a></h1></div>
    <nav class="nav-links">
        <a href="../index.html" class="nav-item">Home</a>
        <a href="search.html" class="nav-item">Search</a>
        <a href="explore.html" class="nav-item">Explore</a>
        <a href="compare.html" class="nav-item">Compare</a>
        <a href="network.html" class="nav-item">Network</a>
        <a href="matrix.html" class="nav-item">Matrix</a>
        <a href="indices.html" class="nav-item active">Indices</a>
    </nav>
    <div class="header-controls">
        <button class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn">Dark Mode</button>
    </div>
  </header>
  <main class="page-container page-wide">
    <div class="index-header">
        <h2>Corpus Indices</h2>
    </div>
    <nav class="index-nav">
        <a href="indices.html" class="{"active" if active_sub=="main" else ""}">Overview</a>
        <a href="index_deities.html" class="{"active" if active_sub=="deities" else ""}">Deities</a>
        <a href="index_persons.html" class="{"active" if active_sub=="persons" else ""}">Persons</a>
        <a href="index_places.html" class="{"active" if active_sub=="places" else ""}">Places</a>
    </nav>
    {content}
  </main>

  <footer class="site-footer">
    <div class="footer-content">
      © 2026 Florian Wachter | Private Non-Profit Research Project | 
      <a href="https://github.com/paxetheninja/AGKI-PM-TaggingEpigraphy" target="_blank">GitHub</a>
    </div>
    <div class="footer-legal">
      Impressum: Privates Forschungsprojekt. Verantwortlich: Florian Wachter, Institut für Antike, Goethestraße 19, 8010 Graz. Kontakt: florian.wachter@uni-graz.at. Keine Gewähr für die Richtigkeit der Daten.
    </div>
  </footer>

  <script>
    const themeBtn = document.getElementById('themeBtn');
    function updateThemeBtn() {{
        const current = document.documentElement.getAttribute('data-theme');
        if (themeBtn) themeBtn.textContent = current === 'light' ? 'Dark Mode' : 'Light Mode';
    }}
    updateThemeBtn();
    window.toggleTheme = function() {{
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeBtn();
    }}

    function initIndexSearch() {{
        const input = document.getElementById('indexSearchInput');
        const table = document.getElementById('indexTable');
        if (!input || !table) return;
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const empty = document.getElementById('indexEmpty');

        const filterRows = () => {{
            const query = input.value.trim().toLowerCase();
            let visible = 0;
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const match = !query || text.includes(query);
                row.style.display = match ? '' : 'none';
                if (match) visible += 1;
            }});
            if (empty) {{
                empty.style.display = visible ? 'none' : 'flex';
            }}
        }};

        input.addEventListener('input', filterRows);
        filterRows();
    }}
    initIndexSearch();
  </script>
</body>
</html>"""

    main_content = f"""
    <div class="index-grid">
        <div class="index-card">
            <h3>Deities</h3>
            <p>Total unique deities: <strong>{len(deities)}</strong></p>
            <a href="index_deities.html" class="button">Browse Deities</a>
        </div>
        <div class="index-card">
            <h3>Persons</h3>
            <p>Total unique persons: <strong>{len(persons)}</strong></p>
            <a href="index_persons.html" class="button">Browse Persons</a>
        </div>
        <div class="index-card">
            <h3>Places</h3>
            <p>Total unique places: <strong>{len(places)}</strong></p>
            <a href="index_places.html" class="button">Browse Places</a>
        </div>
    </div>
    """
    with open(WEBSITE_DIR / "indices.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Indices", main_content, "main"))

    deities_content = f"""
    <div class="index-card">
        <div class="index-toolbar">
            <h3>Deities Index</h3>
            <div class="index-search">
                <input type="search" id="indexSearchInput" placeholder="Filter by name..." aria-label="Filter deities by name">
            </div>
        </div>
        <div class="index-table">
            <table id="indexTable">
                <thead><tr><th>Name</th><th>Mentions</th></tr></thead>
                <tbody>{dict_to_rows(deities)}</tbody>
            </table>
            <div class="index-empty" id="indexEmpty">No entries match this filter.</div>
        </div>
    </div>
    """
    with open(WEBSITE_DIR / "index_deities.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Deities Index", deities_content, "deities"))

    persons_content = f"""
    <div class="index-card">
        <div class="index-toolbar">
            <h3>Persons Index</h3>
            <div class="index-search">
                <input type="search" id="indexSearchInput" placeholder="Filter by name or role..." aria-label="Filter persons by name or role">
            </div>
        </div>
        <div class="index-table">
            <table id="indexTable">
                <thead><tr><th>Name</th><th>Role</th><th>Mentions</th></tr></thead>
                <tbody>{dict_to_rows(persons, is_person=True)}</tbody>
            </table>
            <div class="index-empty" id="indexEmpty">No entries match this filter.</div>
        </div>
    </div>
    """
    with open(WEBSITE_DIR / "index_persons.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Persons Index", persons_content, "persons"))

    places_content = f"""
    <div class="index-card">
        <div class="index-toolbar">
            <h3>Places Index</h3>
            <div class="index-search">
                <input type="search" id="indexSearchInput" placeholder="Filter by name or type..." aria-label="Filter places by name or type">
            </div>
        </div>
        <div class="index-table">
            <table id="indexTable">
                <thead><tr><th>Name</th><th>Type</th><th>Mentions</th></tr></thead>
                <tbody>{dict_to_rows(places, is_place=True)}</tbody>
            </table>
            <div class="index-empty" id="indexEmpty">No entries match this filter.</div>
        </div>
    </div>
    """
    with open(WEBSITE_DIR / "index_places.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Places Index", places_content, "places"))

def build_website(mode=None):
    load_pleiades_cache()
    print("Building website...")
    INSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    inputs = load_inscriptions(INPUT_DIR)
    inputs_map = {i.id: i.model_dump() for i in inputs}
    
    outputs = []
    for f in OUTPUT_DIR.glob("*.json"):
        data = load_json(f)
        if data: outputs.append(data)
    
    # Pre-populate cache with REGION_DATA URIs
    print("Pre-fetching REGION_DATA from Pleiades...")
    for rd in REGION_DATA.values():
        if "uri" in rd: fetch_pleiades_coords(rd["uri"])

    # First pass: collect all unique Pleiades URIs from data
    print("Collecting URIs from inscriptions...")
    unique_uris = set()
    for out in outputs:
        for p in out.get('provenance', []):
            if p.get('uri') and "pleiades" in p['uri']: unique_uris.add(p['uri'])
        for pl in out.get('entities', {}).get('places', []):
            if pl.get('uri') and "pleiades" in pl['uri']: unique_uris.add(pl['uri'])
    
    print(f"Fetching {len(unique_uris)} unique Pleiades URIs...")
    uris_to_fetch = [u for u in unique_uris if u not in PLEIADES_CACHE]
    print(f"  {len(uris_to_fetch)} URIs not in cache. Fetching in parallel...")

    if uris_to_fetch:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_uri = {executor.submit(fetch_pleiades_coords, uri): uri for uri in uris_to_fetch}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_uri)):
                if i % 50 == 0: 
                    print(f"  Progress: {i}/{len(uris_to_fetch)}")
                try:
                    future.result()
                except Exception:
                    pass
    
    save_pleiades_cache()

    all_deities, all_persons, all_places = {}, {}, {}
    merged_list = []
    print(f"Generating HTML for {len(outputs)} inscriptions...")
    for i, out in enumerate(outputs):
        if i % 50 == 0: print(f"  Generating page {i}/{len(outputs)}")
        phi_id = out['phi_id']
        inp = inputs_map.get(phi_id)
        if not inp: continue
        merged = { "id": phi_id, "input": inp, "output": out }
        merged_list.append(merged)
        
        ents = out.get('entities', {})
        for d in ents.get('deities', []):
            name = d['name'] if isinstance(d, dict) else d
            if name not in all_deities: all_deities[name] = {"uri": d.get('uri') if isinstance(d, dict) else None, "count": 0}
            all_deities[name]["count"] += 1
        for p in ents.get('persons', []):
            if p['name'] not in all_persons: all_persons[p['name']] = {"role": p.get('role'), "uri": p.get('uri'), "count": 0}
            all_persons[p['name']]["count"] += 1
        for pl in ents.get('places', []):
            if pl['name'] not in all_places: all_places[pl['name']] = {"type": pl.get('type'), "uri": pl.get('uri'), "count": 0}
            all_places[pl['name']]["count"] += 1

        with open(INSCRIPTIONS_DIR / f"{phi_id}.html", 'w', encoding='utf-8') as f:
            f.write(generate_detail_page(merged))
            
    print("Generating indices pages...")
    generate_indices_page(all_deities, all_persons, all_places)
            
    search_index = []
    print("Building search index...")
    for i, m in enumerate(merged_list):
        if i % 200 == 0: print(f"  Indexing {i}/{len(merged_list)}")
        themes = m['output'].get('themes', [])
        theme_data = [{
            "label": t['label'],
            "path": "/".join(filter(None, [t['hierarchy'].get(k) for k in ['domain', 'subdomain', 'category', 'subcategory']])),
            "confidence": t.get('confidence', 1.0)
        } for t in themes]
        
        # Determine coordinates: Check provenance (most specific first), then region_main
        coords = None
        prov_list = m['output'].get('provenance', [])
        for loc in reversed(prov_list):
            coords = get_coords(loc['name'], loc.get('uri'))
            if coords: break
        if not coords:
            coords = get_coords(m['input'].get('region_main'))
        
        mentioned_places = []
        for p in m['output'].get('entities', {}).get('places', []):
            c = get_coords(p['name'], p.get('uri'))
            if c: mentioned_places.append({"name": p['name'], "coords": c, "type": p.get('type')})

        search_index.append({
            "id": m['id'],
            "mentioned_persons": [{"name": p['name'], "role": p.get('role')} for p in m['output'].get('entities', {}).get('persons', [])],
            "mentioned_deities": [ (d['name'] if isinstance(d, dict) else d) for d in m['output'].get('entities', {}).get('deities', []) ],
            "region": m['input'].get('region_main'),
            "date_str": m['output'].get('date_str') or m['input'].get('date_str'),
            "date_min": m['output'].get('date_min') or m['input'].get('date_min'),
            "date_max": m['output'].get('date_max') or m['input'].get('date_max'),
            "preview_text": m['input'].get('text', '')[:120] + "...",
            "text_length": len(m['input'].get('text', '')),
            "completeness": m['output'].get('completeness'),
            "coordinates": coords,
            "mentioned_places": mentioned_places,
            "themes": theme_data,
            "themes_display": [t['label'] for t in themes]
        })

    full_data = {"taxonomy": load_taxonomy(), "inscriptions": search_index}
    with open(WEBSITE_DIR / "assets/js/data.js", 'w', encoding='utf-8') as f:
        f.write(f"const APP_DATA = {json.dumps(full_data, ensure_ascii=False)};")

    sync_static_pages()
    print(f"Website built. {len(merged_list)} pages generated.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dummy", "real", "auto"], default="auto")
    args = parser.parse_args()
    build_website(mode=args.mode)
