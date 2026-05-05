import re
with open("main_topology.py") as f:
    content = f.read()

# Add chmod 777
content = content.replace("_write_frr_conf(name, cfg_dir)", "_write_frr_conf(name, cfg_dir)\n        node.cmd(f'chmod -R 777 {cfg_dir}')")

# Remove -u root -g root
content = content.replace("f'-u root -g root '", "f''")

with open("main_topology.py", "w") as f:
    f.write(content)
