
import sys

# Read the file
with open('source/build_website.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract html_head string
# It starts at line 160 and ends at... line 535?
start_marker = 'html_head = """<!doctype html>'
end_marker = '""".format(phi_id, phi_id, phi_id)'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find markers")
    sys.exit(1)

# The string includes the quote marks """ at the start
# start_idx points to h of html_head...
# Let's find the first """ after start_idx
quote_start = content.find('"""', start_idx) + 3
html_string = content[quote_start:end_idx]

print(f"Extracted string length: {len(html_string)}")

try:
    formatted = html_string.format("ID1", "ID2", "ID3")
    print("Format successful!")
except Exception as e:
    print(f"Format failed: {e}")
    # Try to find where the placeholders are
    import string
    formatter = string.Formatter()
    try:
        parsed = list(formatter.parse(html_string))
        placeholders = [p for p in parsed if p[1] is not None]
        print(f"Found {len(placeholders)} placeholders.")
        for i, p in enumerate(placeholders):
            print(f"{i}: {p[1]}")
    except Exception as parse_e:
        print(f"Parse failed: {parse_e}")
