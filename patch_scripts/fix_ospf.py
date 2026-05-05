import re
with open("main_topology.py") as f:
    content = f.read()

# Replace all occurrences in pe1 and pe2 configs
content = content.replace(" network 10.0.0.0/8 area 0\n network {lb[name]}/32 area 0",
                          " network 10.0.0.0/8 area 0\n network 172.16.0.0/16 area 0\n network {lb[name]}/32 area 0")

with open("main_topology.py", "w") as f:
    f.write(content)
