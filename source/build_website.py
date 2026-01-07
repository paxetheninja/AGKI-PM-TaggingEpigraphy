import json
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, OUTPUT_DUMMY_DIR, TAXONOMY_DIR
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

    # Global Analysis Summary
    global_rationale = merged_data.get('output', {}).get('rationale', 'No additional analysis provided.')

    # Prepare Tokenized Data
    translations = merged_data.get('output', {}).get('translations', [])
    
    # We prepare a JS object containing the alignments for dynamic rendering
    # format: { "en": [ {greek: "...", trans: "..."}, ... ], "de": ... }
    alignment_js_data = {}
    for tr in translations:
        lang = tr['language']
        alignment_js_data[lang] = tr.get('alignment', [])

    alignment_json = json.dumps(alignment_js_data, ensure_ascii=False)
    
    # Original Text (Strict Line-by-Line)
    # We just use the raw text content. The CSS white-space: pre will handle the newlines.
    raw_greek_html = html.escape(text_content)
    
    lines = text_content.split('\n')
    line_nums = [str(i+1) if (i+1)%5==0 or i==0 else "" for i in range(len(lines))]
    line_nums_html = "\n".join(line_nums)

    # Raw JS string
    js_raw = r"""
    <script>
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const ALIGNMENTS = %s;

    function setTranslation(lang) {
        const btnEn = document.getElementById('btnEn');
        const btnDe = document.getElementById('btnDe');
        const btnOff = document.getElementById('btnOff');
        
        const originalView = document.getElementById('original-view');
        const comparisonView = document.getElementById('comparison-view');
        
        const greekCol = document.getElementById('fluent-greek');
        const transCol = document.getElementById('fluent-trans');

        // Reset Buttons
        [btnEn, btnDe, btnOff].forEach(b => b.classList.remove('active'));

        if(lang === 'none') {
            // Show Original Line-by-Line View
            originalView.style.display = 'grid';
            comparisonView.style.display = 'none';
            btnOff.classList.add('active');
        } else {
            // Show Comparison Side-by-Side View
            originalView.style.display = 'none';
            comparisonView.style.display = 'grid';
            
            if(lang === 'en') btnEn.classList.add('active');
            if(lang === 'de') btnDe.classList.add('active');
            
            // Render Fluent Columns
            const data = ALIGNMENTS[lang] || [];
            let greekHtml = '';
            let transHtml = '';
            
            if (data.length === 0) {
                greekHtml = '<p class="muted">No alignment data.</p>';
                transHtml = '<p class="muted">No alignment data.</p>';
            } else {
                data.forEach((row, index) => {
                    // Create interactive spans for fluent reading
                    greekHtml += `<span class="fluent-segment" data-seg-id="${index}" onmouseover="highlightSegment(${index})" onmouseout="clearHighlightSegment()">${row.greek} </span>`;
                    transHtml += `<span class="fluent-segment" data-seg-id="${index}" onmouseover="highlightSegment(${index})" onmouseout="clearHighlightSegment()">${row.translation} </span>`;
                });
            }
            greekCol.innerHTML = greekHtml;
            transCol.innerHTML = transHtml;
        }
    }

    function highlightSegment(id) {
        document.querySelectorAll(`.fluent-segment[data-seg-id="${id}"]`).forEach(el => el.classList.add('active-segment'));
    }

    function clearHighlightSegment() {
        document.querySelectorAll('.fluent-segment').forEach(el => el.classList.remove('active-segment'));
    }

    function copyCitation() {
        const citation = "AGKI Project. (2026). Inscription PHI-" + "%s" + ". Retrieved from " + window.location.href;
        navigator.clipboard.writeText(citation);
        alert("Citation copied to clipboard!");
    }
    </script>
    """ % (alignment_json, phi_id)

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
        white-space: pre-wrap; /* Better than scrollbar: wrap lines nicely */
        word-break: break-word;
        padding-left: 1rem; 
    }}

    /* Fluent Comparison View Styles */
    .comparison-container {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 4px;
        margin-bottom: 2rem;
        padding: 2rem;
    }}
    
    .fluent-col {{
        line-height: 1.8;
        font-size: 1.15rem;
    }}

    .fluent-col-header {{
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--muted);
        font-size: 0.85rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }}

    .fluent-greek {{
        font-family: "New Athena Unicode", "Gentium Plus", "Times New Roman", serif; 
        font-size: 1.25rem;
        color: var(--text);
    }}

    .fluent-trans {{
        font-family: system-ui, -apple-system, sans-serif;
        color: var(--text);
    }}

    .fluent-segment {{
        border-radius: 3px;
        transition: background-color 0.2s, color 0.1s;
        cursor: pointer;
    }}
    
    .fluent-segment:hover, .active-segment {{
        background-color: rgba(217, 123, 61, 0.15); /* Accent color tint */
        color: var(--primary);
    }}

    .trans-controls {{ margin-bottom: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; align-items: center; }}
    .trans-btn {{ background: var(--bg); border: 1px solid var(--border); padding: 0.4rem 0.8rem; cursor: pointer; color: var(--muted); font-size: 0.85rem; border-radius: 4px; }}
    .trans-btn:hover {{ border-color: var(--primary); color: var(--text); }}
    .trans-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}

    .theme-card {{ background: var(--panel); padding: 1rem 1.5rem; border-left: 4px solid var(--primary); margin-bottom: 0.75rem; border: 1px solid var(--border); border-left-width: 4px; }}
    .ai-analysis-box {{ background: rgba(31, 167, 163, 0.05); padding: 2rem; border-radius: 8px; border: 1px solid var(--border); margin-top: 2rem; }}
    .evidence-box {{ max-width: 500px; text-align: right; }}
    .evidence-quote {{ font-size: 0.85rem; font-style: italic; color: var(--muted); margin: 0; }}
    .badge.green {{ background: #e6f4ea; color: #137333; border-color: #137333; }}
    .badge.orange {{ background: #fef7e0; color: #b06000; border-color: #b06000; }}
    .badge.red {{ background: #fce8e6; color: #c5221f; border-color: #c5221f; }}
    .entity-tag {{ background: rgba(217, 123, 61, 0.1); color: var(--accent-2); margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.9rem; border: 1px solid rgba(217, 123, 61, 0.2); }}
  </style>
  {}
</head>""".format(phi_id, js_raw)

    html_body = """
<body>
  <header class="site-header">
    <div class="brand">
      <h1><a href="../index.html" style="color:white;text-decoration:none;">AGKI Tagging Tool</a></h1>
    </div>
  </header>
  <main class="page-container">
    <a href="../index.html" class="back-link">← Back to Dashboard</a>
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
        <h3>Original Text & Translation</h3>
        <div class="trans-controls">
            <span class="eyebrow" style="margin:0; margin-right:0.5rem;">Translation:</span>
            <button id="btnOff" class="trans-btn active" onclick="setTranslation('none')">Original (Lines)</button>
            <button id="btnEn" class="trans-btn" onclick="setTranslation('en')">English (Compare)</button>
            <button id="btnDe" class="trans-btn" onclick="setTranslation('de')">German (Compare)</button>
        </div>
    </div>

    <!-- Original Line-by-Line View -->
    <div id="original-view" class="text-viewer-original">
        <div class="line-numbers">{}</div>
        <div class="greek-content">{}</div>
    </div>

    <!-- Fluent Comparison View -->
    <div id="comparison-view" class="comparison-container" style="display:none;">
        <div class="fluent-col">
            <div class="fluent-col-header">Greek Text</div>
            <div id="fluent-greek" class="fluent-greek"></div>
        </div>
        <div class="fluent-col">
            <div class="fluent-col-header">Translation</div>
            <div id="fluent-trans" class="fluent-trans"></div>
        </div>
    </div>

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
        persons_html + places_html,
        html.escape(global_rationale).replace('\n', '<br>')
    )

    return html_head + html_body

def build_website(mode=None):
    print(f"Building website (mode: {mode or 'auto'})...")
    INSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    inputs = load_inscriptions(INPUT_DIR)
    inputs_map = {i.id: i.model_dump() for i in inputs}
    
    if mode == "dummy":
        target_dir = OUTPUT_DUMMY_DIR
    elif mode == "real":
        target_dir = OUTPUT_DIR
    else:
        target_dir = OUTPUT_DUMMY_DIR 
        if not target_dir.exists(): target_dir = OUTPUT_DIR

    outputs = []
    for f in target_dir.glob("*.json"):
        data = load_json(f)
        if data: outputs.append(data)
    
    merged_list = []
    for out in outputs:
        phi_id = out['phi_id']
        inp = inputs_map.get(phi_id)
        if not inp: continue
        merged = { "id": phi_id, "input": inp, "output": out }
        merged_list.append(merged)
        with open(INSCRIPTIONS_DIR / f"{phi_id}.html", 'w', encoding='utf-8') as f:
            f.write(generate_detail_page(merged))
            
    search_index = []
    for m in merged_list:
        themes = m['output'].get('themes', [])
        hierarchy_paths = [t['hierarchy'] for t in themes]
        
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
            "hierarchy_paths": hierarchy_paths,
            "themes_display": [t['label'] for t in themes]
        })

    full_data = {
        "taxonomy": load_taxonomy(),
        "inscriptions": search_index
    }

    js_content = f"const APP_DATA = {json.dumps(full_data, ensure_ascii=False)};"
    with open(WEBSITE_DIR / "assets/js/data.js", 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # Also update the specific mode file for the dashboard's data switcher
    if mode in ["real", "dummy"]:
        with open(WEBSITE_DIR / f"assets/js/data_{mode}.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
        
    print(f"Website built. {len(merged_list)} pages generated.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dummy", "real", "auto"], default="auto")
    args = parser.parse_args()
    build_website(mode=args.mode)