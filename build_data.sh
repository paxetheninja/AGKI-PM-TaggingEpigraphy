#!/bin/bash
# Script to build both dummy and real data files

echo "Building Dummy Data..."
# The build_website.py currently auto-detects. We need to force it or modify it.
# Let's modify build_website.py to accept an argument.
python -m source.build_website --mode dummy
mv website/assets/js/data.js website/assets/js/data_dummy.js

echo "Building Real Data..."
python -m source.build_website --mode real
mv website/assets/js/data.js website/assets/js/data_real.js

# Restore a default data.js (e.g. dummy)
cp website/assets/js/data_dummy.js website/assets/js/data.js
echo "Done."
