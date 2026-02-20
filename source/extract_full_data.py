import os
import json
import re
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def clean_greek_text_preserve_accents(text):
    """
    Cleans structural symbols and normalizes text while PRESERVING polytonic accents
    and epigraphic markers (like underdots).
    """
    if not text:
        return ""

    # 1. Normalize Unicode (NFC)
    text = unicodedata.normalize("NFC", text)

    # 2. Handle missing parts [․․5․․] or [..5..] -> [-----]
    def replace_missing(match):
        content = match.group(1)
        num_match = re.search(r'\d+', content)
        if num_match:
            count = int(num_match.group(0))
            return "[" + "-" * count + "]"
        return match.group(0)

    text = re.sub(r'\[([^\]]*?\d+[^\]]*?)\]', replace_missing, text)

    # 3. Map specific structural characters to standard equivalents
    # ∶ (U+2236), ⋮ (U+22EE) are word separators -> map to space
    text = text.replace('∶', ' ')
    text = text.replace('⋮', ' ')
    # ․ (U+2024 ONE DOT LEADER) -> standard dot
    text = text.replace('․', '.')
    # 〚 〛 are erasures -> map to [[ ]]
    text = text.replace('〚', '[[').replace('〛', ']]')
    
    # Map dashes and specific spaces to standard equivalents
    text = text.replace('—', '-')
    text = text.replace(' ', ' ')
    text = text.replace('–', '-')
    
    # 4. Whitelist:
    # \u0370-\u03FF: Greek and Coptic
    # \u1F00-\u1FFF: Greek Extended (Polytonic)
    # \u0300-\u036F: Combining Diacritical Marks (Underdots, etc.)
    # \s: whitespace
    # \[ \] \( \) \- \. \, \; \: \d \? \! : Standard punctuation and brackets
    keep_pattern = r'[^\u0370-\u03FF\u1F00-\u1FFF\u0300-\u036F\s\[\]\(\)\-\.\,\;\:\d\?\!]'
    text = re.sub(keep_pattern, '', text)

    # 5. Collapse horizontal whitespace but preserve newlines
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def date_parser_phi(d):
    if not d: return None, None
    d = re.sub(r'\([^\)]*\)', r'', d)
    circa = False
    circa_words = ['?', 'probably', 'perhaps', 'perh.', 'prob.', 'or', 'ca']
    for w in circa_words:
        if w in d.lower():
            circa = True
            break
    m = re.findall(r'(-?\d+)', d)
    if len(m) >= 2:
        return f"{m[0]} {m[1]}", circa
    elif len(m) == 1:
        return f"{m[0]} {m[0]}", circa
    return None, circa

def extract_from_html(html_file):
    try:
        phi_id = html_file.stem
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        lines = []
        table = soup.find('table', attrs={'class': 'grk'})
        if not table:
            return None
            
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            line_text = ""
            for td in tds:
                if 'class' in td.attrs and 'id' in td.attrs['class']:
                    continue
                line_text += td.get_text()
            if line_text.strip():
                cleaned_line = clean_greek_text_preserve_accents(line_text)
                if cleaned_line:
                    lines.append(cleaned_line)
                
        full_text = "\n".join(lines)
        
        region_main, region_sub = '', ''
        hdr1 = soup.find('div', attrs={'class': 'hdr1'})
        if hdr1:
            hdr1_a = hdr1.find_all('a')
            if hdr1_a and len(hdr1_a) >= 2:
                region_main = hdr1_a[1].get_text().strip()
            if hdr1_a and len(hdr1_a) >= 3:
                region_sub = hdr1_a[2].get_text().strip()

        metadata = ''
        ti_span = soup.find('span', attrs={'class': 'ti'})
        if ti_span:
            metadata = ti_span.get_text().strip()

        date_str = ''
        date_min, date_max, date_circa = None, None, None
        parts = re.split(r'[—|~|–|―]', metadata)
        for tok in parts:
            if re.search(r'\W(BC|AD|period|reign|a\.|p\.(?!\s+\d)|aet\.)(\W|$)', tok):
                date_str = tok.strip()
                date_range, circa = date_parser_phi(tok)
                if date_range:
                    try:
                        d_min, d_max = date_range.split(' ')
                        date_min, date_max, date_circa = float(d_min), float(d_max), circa
                    except: pass
                break

        return {
            'id': int(phi_id),
            'text': full_text,
            'text_by_lines': lines,
            'metadata': metadata,
            'region_main': region_main,
            'region_sub': region_sub,
            'date_str': date_str,
            'date_min': date_min,
            'date_max': date_max,
            'date_circa': date_circa,
        }
    except Exception:
        return None

def process_file(html_file):
    data = extract_from_html(html_file)
    if data:
        output_path = Path("data/input") / f"{data['id']}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    return False

def main():
    html_dir = Path("../iphi#/train/data/iphi-json")
    output_dir = Path("data/input")
    
    if not html_dir.exists():
        print(f"Error: HTML source directory not found at {html_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    html_files = list(html_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files. Starting parallel extraction with refined cleaning...")
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(tqdm(executor.map(process_file, html_files), total=len(html_files)))

    success_count = sum(1 for r in results if r)
    print(f"Extraction complete. Successfully processed {success_count} inscriptions.")

if __name__ == "__main__":
    main()
