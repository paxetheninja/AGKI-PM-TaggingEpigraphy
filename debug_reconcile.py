import urllib.request
import json
import urllib.error
import urllib.parse

import re

def search_pleiades_direct(name):
    print(f"Searching Pleiades for '{name}' (HTML Scraping)...")
    try:
        # Using the standard search page
        params = {"SearchableText": name}
        url = f"https://pleiades.stoa.org/search?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Debug/1.0'})
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Look for links to places like href="https://pleiades.stoa.org/places/12345"
            # or href="/places/12345"
            # We want the first unique Place ID found in the search results area.
            # A simple regex for the ID:
            matches = re.findall(r'href="[^"]*/places/(\d+)"', html)
            unique_ids = []
            for m in matches:
                if m not in unique_ids: unique_ids.append(m)
            
            print(f"  Found IDs: {unique_ids}")
            
            if unique_ids:
                # Return the first one
                final_url = f"https://pleiades.stoa.org/places/{unique_ids[0]}"
                print(f"  Selected: {final_url}")
                return final_url

    except Exception as e:
        print(f"  Error: {e}")
    return None

def check_wikidata_for_pleiades(qid):
    print(f"Checking Wikidata {qid}...")
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Debug/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            entity = data.get("entities", {}).get(qid, {})
            claims = entity.get("claims", {}).get("P1566", [])
            if claims:
                val = claims[0].get("mainsnak", {}).get("datavalue", {}).get("value")
                print(f"  Found Pleiades ID: {val}")
                return val
            else:
                print("  No Pleiades ID (P1566) found.")
    except Exception as e:
        print(f"  Error: {e}")
    return None

def check_url(url):
    print(f"Checking URL: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Debug/1.0'})
        with urllib.request.urlopen(req) as response:
            print(f"  Status: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    check_wikidata_for_pleiades("Q1524") # Athens
    check_wikidata_for_pleiades("Q1351") # Pergamon (ancient)
    
    # check_url("https://pleiades.stoa.org/places/4180386") # Commented out

    check_wikidata_for_pleiades("Q12877385") # Eupyridai
    check_wikidata_for_pleiades("Q13518344") # Hestiaia

    check_url("https://pleiades.stoa.org/places/8354440")
    check_url("https://pleiades.stoa.org/places/579888")
