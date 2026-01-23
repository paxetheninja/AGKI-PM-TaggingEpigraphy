import json
import sys

try:
    with open('website/assets/js/data.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip prefix and suffix
    json_str = content.replace('const APP_DATA = ', '').rstrip(';')
    
    data = json.loads(json_str)
    print(f"JSON is valid. Keys: {data.keys()}")
    print(f"Number of inscriptions: {len(data.get('inscriptions', []))}")
    
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
except Exception as e:
    print(f"Error: {e}")
