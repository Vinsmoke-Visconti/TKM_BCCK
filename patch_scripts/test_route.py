import re
with open("main_topology.py") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "STATIC ROUTES" in l:
        print("Found STATIC ROUTES at line", i)
