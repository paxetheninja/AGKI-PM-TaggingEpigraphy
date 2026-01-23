import os
import urllib.request
from pathlib import Path

LIBS_DIR = Path("website/assets/libs")
LIBS_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "d3.js": "https://d3js.org/d3.v7.min.js",
    "chart.js": "https://cdn.jsdelivr.net/npm/chart.js",
    "plotly.js": "https://cdn.plot.ly/plotly-2.27.0.min.js",
    "leaflet.js": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
    "leaflet.css": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
    "leaflet.markercluster.js": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js",
    "MarkerCluster.css": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css",
    "MarkerCluster.Default.css": "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css",
    "intro.js": "https://cdn.jsdelivr.net/npm/intro.js@7.2.0/minified/intro.min.js",
    "introjs.min.css": "https://cdn.jsdelivr.net/npm/intro.js@7.2.0/minified/introjs.min.css"
}

for name, url in URLS.items():
    print(f"Downloading {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(LIBS_DIR / name, 'wb') as f:
                f.write(response.read())
    except Exception as e:
        print(f"Failed to download {name}: {e}")

print("Download complete.")
