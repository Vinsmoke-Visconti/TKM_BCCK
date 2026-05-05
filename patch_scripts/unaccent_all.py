import os
import glob
import unicodedata

def remove_accents(input_str):
    s1 = input_str.replace('Đ', 'D').replace('đ', 'd')
    return ''.join(c for c in unicodedata.normalize('NFD', s1) if unicodedata.category(c) != 'Mn')

# Fix the syntax error in main_topology.py first
with open("main_topology.py", "r", encoding='utf-8') as f:
    content = f.read()

bad_def = "def _write_frr_conf(name, cfg_dir)\n        node.cmd(f'chmod -R 777 {cfg_dir}'):"
good_def = "def _write_frr_conf(name, cfg_dir):"

if bad_def in content:
    content = content.replace(bad_def, good_def)
    with open("main_topology.py", "w", encoding='utf-8') as f:
        f.write(content)
        print("Fixed SyntaxError in main_topology.py")

# Apply unaccent to all text files
extensions = ["*.py", "*.sh", "*.md"]
files = []
for ext in extensions:
    files.extend(glob.glob(ext))

for file in files:
    if file == "unaccent_all.py":
        continue
    with open(file, "r", encoding='utf-8') as f:
        text = f.read()
    
    new_text = remove_accents(text)
    
    with open(file, "w", encoding='utf-8') as f:
        f.write(new_text)
    print(f"Processed {file}")
