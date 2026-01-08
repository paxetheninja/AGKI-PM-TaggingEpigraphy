import json
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR
from .data_loader import load_inscriptions

WEBSITE_DIR = Path("website")
INSCRIPTIONS_DIR = WEBSITE_DIR / "inscriptions"
ASSETS_DIR = WEBSITE_DIR / "assets"

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

def get_coords(name):
    if not name: return None
    val = None
    if name in GAZETTEER: 
        val = GAZETTEER[name]
    else:
        for key, coords in GAZETTEER.items():
            if key in name or name in key: 
                val = coords
                break
    
    if val:
        if isinstance(val, dict) and 'coords' in val:
            return val['coords']
        if isinstance(val, list):
            return val
    return None

# Combined Gazetteer from previous steps
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

        themes_html += """
        <div class="theme-card" onmouseover="highlightQuote('{quote}')" onmouseout="clearHighlight()">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="tag domain-tag">{domain}</span>
                    <span class="badge {conf_color}" style="font-size:0.7rem; vertical-align:middle; margin-left:0.5rem;">{conf_pct}% Conf.</span>
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
            domain=h.get('domain', 'Unclassified'),
            conf_color=conf_color,
            conf_pct=int(conf*100),
            path=path_str,
            label=t['label'],
            orig_quote=html.escape(quote)
        )

    # Entities
    entities = merged_data.get('output', {}).get('entities', {})
    persons_html = ""
    for p in entities.get('persons', []):
        persons_html += '<span class="tag entity-tag">👤 {} <small>({})</small></span>'.format(html.escape(p["name"]), html.escape(p.get("role", "")))
    places_html = ""
    for p in entities.get('places', []):
        places_html += '<span class="tag entity-tag">📍 {} <small>({})</small></span>'.format(html.escape(p["name"]), html.escape(p.get("type", "")))
    deities_html = ""
    for d in entities.get('deities', []):
        deities_html += '<span class="tag entity-tag">⚡ {}</span>'.format(html.escape(d))

    # Global Analysis Summary
    global_rationale = merged_data.get('output', {}).get('rationale') or 'No additional analysis provided.'

    # Original Text (Strict Line-by-Line)
    # We just use the raw text content. The CSS white-space: pre-wrap will handle the newlines and wrapping.
    raw_greek_html = html.escape(text_content)
    
    lines = text_content.split('\n')
    line_nums = [str(i+1) if (i+1)%5==0 or i==0 else "" for i in range(len(lines))]
    line_nums_html = "\n".join(line_nums)

    # Assemble HTML
    html_head = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PHI-{} - AGKI</title>
  <link rel="stylesheet" href="../assets/css/main.css">
  <style>
    /* Custom Scrollbar Styling */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: rgba(0,0,0,0.05); 
    }}
    ::-webkit-scrollbar-thumb {{
        background: #ccc; 
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #aaa; 
    }}

    .page-container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
    .back-link {{ display: inline-block; margin-bottom: 1rem; color: var(--primary); font-weight: 600; }}
    
    /* Original View Styles (Line by Line) */
    .text-viewer-original {{ 
        display: grid; 
        grid-template-columns: 40px 1fr; 
        gap: 2rem; 
        font-family: "New Athena Unicode", "Gentium Plus", "Times New Roman", serif; 
        font-size: 1.25rem; 
        line-height: 1.6; 
        background: var(--panel); 
        padding: 2rem; 
        border: 1px solid var(--border); 
        border-radius: 4px; 
        margin-bottom: 2rem; 
        color: var(--text);
    }}

    .line-numbers {{ 
        text-align: right; 
        color: var(--muted); 
        font-size: 1.25rem; 
        line-height: 1.6; 
        user-select: none; 
        opacity: 0.5; 
        font-family: inherit; 
        white-space: pre; 
        padding-right: 1rem;
        border-right: 1px solid var(--border);
    }}

    .greek-content {{ 
        white-space: pre-wrap; 
        word-break: break-word;
        padding-left: 1rem; 
    }}

    .highlight-evidence {{
        background-color: var(--accent);
        color: white;
        border-radius: 2px;
        padding: 0 2px;
    }}

    .theme-card {{ background: var(--panel); padding: 1rem 1.5rem; border-left: 4px solid var(--primary); margin-bottom: 0.75rem; border: 1px solid var(--border); border-left-width: 4px; }}
    .ai-analysis-box {{ background: rgba(31, 167, 163, 0.05); padding: 2rem; border-radius: 8px; border: 1px solid var(--border); margin-top: 2rem; }}
    .evidence-box {{ max-width: 500px; text-align: right; }}
    .evidence-quote {{ font-size: 0.85rem; font-style: italic; color: var(--muted); margin: 0; }}
    .badge.green {{ background: #e6f4ea; color: #137333; border-color: #137333; }}
    .badge.orange {{ background: #fef7e0; color: #b06000; border-color: #b06000; }}
    .badge.red {{ background: #fce8e6; color: #c5221f; border-color: #c5221f; }}
    .entity-tag {{ background: rgba(217, 123, 61, 0.1); color: var(--accent-2); margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.9rem; border: 1px solid rgba(217, 123, 61, 0.2); }}
    
    /* Split View Styles */
    .split-container {{ display: block; }}
    .split-container.active {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }}
    .split-col-left {{ }}
    .split-col-right {{ }}
    
    /* Sticky sidebar in split view */
    .split-container.active .split-col-right {{ position: sticky; top: 20px; max-height: 90vh; overflow-y: auto; padding-right: 10px; }}
  </style>
  <script>
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    function toggleSplitView() {{
        const container = document.getElementById('main-content');
        const btn = document.getElementById('splitViewBtn');
        container.classList.toggle('active');
        if(container.classList.contains('active')) {{
            btn.textContent = 'View: Split';
            btn.classList.add('active');
        }} else {{
            btn.textContent = 'View: Standard';
            btn.classList.remove('active');
        }}
    }}

    function copyCitation() {{
        const citation = "AGKI Project. (2026). Inscription PHI-" + "{}" + ". Retrieved from " + window.location.href;
        navigator.clipboard.writeText(citation);
        alert("Citation copied to clipboard!");
    }}
    
    function highlightQuote(quote) {{
        const container = document.querySelector('.greek-content');
        if (!container || !quote) return;
        
        const escapedQuote = quote.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
        const regex = new RegExp(escapedQuote, 'g');
        container.innerHTML = container.innerHTML.replace(
            regex, 
            match => `<mark class="highlight-evidence">${{match}}</mark>`
        );
    }}
    
    function clearHighlight() {{
        const container = document.querySelector('.greek-content');
        if (!container) return;
        container.innerHTML = container.innerHTML.replace(/<mark class="highlight-evidence">(.*?)<\/mark>/g, '$1');
    }}

    function updateFontSize(size) {{
        const container = document.getElementById('original-view');
        if (container) {{
            container.style.fontSize = size + 'px';
            const lines = container.querySelector('.line-numbers');
            if(lines) lines.style.fontSize = size + 'px';
        }}
    }}
  </script>
</head>""".format(phi_id, phi_id)

    html_body = """
<body>
  <header class="site-header">
    <div class="brand">
      <h1><a href="../index.html" style="color:white;text-decoration:none;">AGKI Tagging Tool</a></h1>
    </div>
    <nav class="nav-links">
        <a href="../index.html" class="nav-item">Search</a>
        <a href="../explore.html" class="nav-item">Explore</a>
        <a href="../indices.html" class="nav-item">Indices</a>
    </nav>
  </header>
  <main class="page-container">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
        <a href="../index.html" class="back-link" style="margin:0;">← Back to Dashboard</a>
        <button id="splitViewBtn" onclick="toggleSplitView()" class="button secondary" style="font-size:0.8rem; padding:0.3rem 0.8rem;">View: Standard</button>
    </div>
    
    <div id="main-content" class="split-container">
        <div class="split-col-left">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Inscription PHI-{}</h2>
                <div style="display:flex; gap:0.5rem;">
                    <button onclick="copyCitation()" class="button secondary" style="font-size:0.9rem; padding:0.5rem 1rem;">📜 Cite</button>
                    <a href="https://epigraphy.packhum.org/text/{}" target="_blank" class="button">View on PHI</a>
                </div>
            </div>
            
            <div class="meta-grid">
                <div><small class="eyebrow">Provenance</small><br>{}</div>
                <div><small class="eyebrow">Date</small><br><strong>{}</strong></div>
                <div><small class="eyebrow">Completeness</small><br><span class="badge info">{}</span></div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:end; margin-bottom:0.5rem;">
                <h3>Original Text</h3>
                <!-- Font Size Control -->
                <div style="display:flex; align-items:center; gap:0.5rem; background:var(--panel); border:1px solid var(--border); padding:0.2rem 0.5rem; border-radius:4px;">
                    <span style="font-size:0.8rem; color:var(--muted);">A</span>
                    <input type="range" id="fontSizeSlider" min="14" max="32" value="20" oninput="updateFontSize(this.value)" style="width:80px; accent-color:var(--primary);">
                    <span style="font-size:1rem; font-weight:bold; color:var(--muted);">A</span>
                </div>
            </div>

            <!-- Original Line-by-Line View -->
            <div id="original-view" class="text-viewer-original">
                <div class="line-numbers">{}</div>
                <div class="greek-content">{}</div>
            </div>
        </div>

        <div class="split-col-right">
            <h3>Thematic Analysis</h3>
            {}
            
            <div style="margin-top:2rem;">
                <h3>Entities</h3>
                <div>{}</div>
            </div>

            <div class="ai-analysis-box">
                <h3>🤖 AI Analysis Summary</h3>
                <p style="line-height:1.7;">{}</p>
            </div>
        </div>
    </div>
  </main>
</body>
</html>
""".format(
        phi_id,
        phi_id,
        region_html,
        merged_data['input'].get('date_str', 'N/A'),
        merged_data['output'].get('completeness', 'unknown'),
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
            if is_person: extra = f"<td>{html.escape(val['role'] or '')}</td>"
            if is_place: extra = f"<td>{html.escape(val['type'] or '')}</td>"
            
            uri_link = ""
            if not isinstance(val, int) and val.get('uri'):
                uri_link = f' <a href="{val["uri"]}" target="_blank" style="text-decoration:none;">🔗</a>'
            
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
  <style>
    .page-container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
    .index-nav {{ display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }}
    .index-nav a {{ text-decoration: none; color: var(--muted); font-weight: 600; padding: 0.5rem 1rem; border-radius: 4px; }}
    .index-nav a:hover {{ background: var(--panel); }}
    .index-nav a.active {{ background: var(--primary); color: white; }}
    .index-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
    th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
    .nav-links {{ display: flex; gap: 1.5rem; }}
    .nav-item {{ color: rgba(255,255,255,0.8); font-weight: 600; text-decoration: none; padding: 0.5rem 0; }}
    .nav-item:hover, .nav-item.active {{ color: white; border-bottom: 2px solid white; }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="brand"><h1>AGKI Tagging Tool</h1></div>
    <nav class="nav-links">
        <a href="index.html" class="nav-item">Search</a>
        <a href="explore.html" class="nav-item">Explore</a>
        <a href="indices.html" class="nav-item active">Indices</a>
    </nav>
  </header>
  <main class="page-container">
    <h2>Corpus Indices</h2>
    <nav class="index-nav">
        <a href="indices.html" class="{"active" if active_sub=="main" else ""}">Overview</a>
        <a href="index_deities.html" class="{"active" if active_sub=="deities" else ""}">⚡ Deities</a>
        <a href="index_persons.html" class="{"active" if active_sub=="persons" else ""}">👤 Persons</a>
        <a href="index_places.html" class="{"active" if active_sub=="places" else ""}">📍 Places</a>
    </nav>
    {content}
  </main>
</body>
</html>"""

    # 1. Main Landing Page
    main_content = f"""
    <div class="index-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:1.5rem;">
        <div class="index-card">
            <h3>⚡ Deities</h3>
            <p>Total unique deities: <strong>{len(deities)}</strong></p>
            <a href="index_deities.html" class="button">Browse Deities</a>
        </div>
        <div class="index-card">
            <h3>👤 Persons</h3>
            <p>Total unique persons: <strong>{len(persons)}</strong></p>
            <a href="index_persons.html" class="button">Browse Persons</a>
        </div>
        <div class="index-card">
            <h3>📍 Places</h3>
            <p>Total unique places: <strong>{len(places)}</strong></p>
            <a href="index_places.html" class="button">Browse Places</a>
        </div>
    </div>
    """
    with open(WEBSITE_DIR / "indices.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Indices", main_content, "main"))

    # 2. Deities Page
    deities_content = f"""
    <div class="index-card">
        <h3>⚡ Deities Index</h3>
        <table>
            <thead><tr><th>Name</th><th>Mentions</th></tr></thead>
            <tbody>{dict_to_rows(deities)}</tbody>
        </table>
    </div>
    """
    with open(WEBSITE_DIR / "index_deities.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Deities Index", deities_content, "deities"))

    # 3. Persons Page
    persons_content = f"""
    <div class="index-card">
        <h3>👤 Persons Index</h3>
        <table>
            <thead><tr><th>Name</th><th>Role</th><th>Mentions</th></tr></thead>
            <tbody>{dict_to_rows(persons, is_person=True)}</tbody>
        </table>
    </div>
    """
    with open(WEBSITE_DIR / "index_persons.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Persons Index", persons_content, "persons"))

    # 4. Places Page
    places_content = f"""
    <div class="index-card">
        <h3>📍 Places Index</h3>
        <table>
            <thead><tr><th>Name</th><th>Type</th><th>Mentions</th></tr></thead>
            <tbody>{dict_to_rows(places, is_place=True)}</tbody>
        </table>
    </div>
    """
    with open(WEBSITE_DIR / "index_places.html", 'w', encoding='utf-8') as f:
        f.write(get_template("Places Index", places_content, "places"))

def build_website(mode=None):
    print("Building website...")
    INSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    inputs = load_inscriptions(INPUT_DIR)
    inputs_map = {i.id: i.model_dump() for i in inputs}
    
    target_dir = OUTPUT_DIR

    outputs = []
    for f in target_dir.glob("*.json"):
        data = load_json(f)
        if data: outputs.append(data)
    
    all_deities = {} # Name -> count
    all_persons = {} # Name -> {role, uri, count}
    all_places = {}  # Name -> {type, uri, count}

    merged_list = []
    for out in outputs:
        phi_id = out['phi_id']
        inp = inputs_map.get(phi_id)
        if not inp: continue
        merged = { "id": phi_id, "input": inp, "output": out }
        merged_list.append(merged)
        
        # Collect Entities for Index
        ents = out.get('entities', {})
        for d in ents.get('deities', []):
            all_deities[d] = all_deities.get(d, 0) + 1
        
        for p in ents.get('persons', []):
            name = p['name']
            if name not in all_persons:
                all_persons[name] = {"role": p.get('role'), "uri": p.get('uri'), "count": 0}
            all_persons[name]["count"] += 1
            
        for pl in ents.get('places', []):
            name = pl['name']
            if name not in all_places:
                all_places[name] = {"type": pl.get('type'), "uri": pl.get('uri'), "count": 0}
            all_places[name]["count"] += 1

        with open(INSCRIPTIONS_DIR / f"{phi_id}.html", 'w', encoding='utf-8') as f:
            f.write(generate_detail_page(merged))
            
    # Generate Index Page
    generate_indices_page(all_deities, all_persons, all_places)
            
    search_index = []
    for m in merged_list:
        themes = m['output'].get('themes', [])
        
        # Extended theme info for filtering
        theme_data = []
        for t in themes:
            h = t['hierarchy']
            path_parts = [h.get('domain'), h.get('subdomain'), h.get('category'), h.get('subcategory')]
            theme_data.append({
                "label": t['label'],
                "path": "/".join(filter(None, path_parts)),
                "confidence": t.get('confidence', 1.0)
            })
        
        prov_list = m['output'].get('provenance', [])
        coords = None
        region_display = m['input'].get('region_main')
        
        if prov_list:
            for loc in reversed(prov_list):
                c = get_coords(loc['name'])
                if c:
                    coords = c
                    region_display = loc['name']
                    break
        
        if not coords:
            coords = get_coords(m['input'].get('region_main'))
        
        entities = m['output'].get('entities', {})
        mentioned_places = []
        for p in entities.get('places', []):
            c = get_coords(p['name'])
            if c:
                mentioned_places.append({
                    "name": p['name'],
                    "coords": c,
                    "type": p.get('type')
                })
        
        search_index.append({
            "id": m['id'],
            "region": region_display,
            "date_str": m['input'].get('date_str'),
            "date_min": m['input'].get('date_min'),
            "date_max": m['input'].get('date_max'),
            "preview_text": m['input'].get('text', '')[:120] + "...",
            "text_length": len(m['input'].get('text', '')),
            "completeness": m['output'].get('completeness'),
            "coordinates": coords,
            "mentioned_places": mentioned_places,
            "themes": theme_data,
            "themes_display": [t['label'] for t in themes]
        })

    full_data = {
        "taxonomy": load_taxonomy(),
        "inscriptions": search_index
    }

    js_content = f"const APP_DATA = {json.dumps(full_data, ensure_ascii=False)};"
    with open(WEBSITE_DIR / "assets/js/data.js", 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Website built. {len(merged_list)} pages generated.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dummy", "real", "auto"], default="auto")
    args = parser.parse_args()
    build_website(mode=args.mode)