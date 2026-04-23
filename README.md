# Metro Ethernet MPLS – Do An Cuoi Ky TKM
## MSSV: 52300267 | Truong DH Ton Duc Thang

---

## 📁 Cau truc thu muc

```
tkm_cuoi_ky_52300267/
├── main_topology.py       # Topology chinh Mininet (chay dau tien)
├── run_all.sh             # Script chay toan bo tu dong
├── scripts/               # Cac script phu tro
│   ├── performance_test.py
│   ├── generate_excel_report.py
│   └── create_task_excel.py
├── results/               # File Excel dau ra
├── configs/               # Folder chua config (neu co)
├── docs/                  # Tai lieu huong dan
└── README.md              # File nay
```

---

## 🌐 Kien truc mang

```
[Site A - Flat]          [Site B - 3-Tier]        [Site C - Leaf-Spine]
 hA1 hA2 hA3              hB1 hB2 hB3 hB4           hC1 hC2 hC3
    |                       |                           |
   sA                   sBcore                    spine1─spine2
    |                  /       \                  /  \ / \  \
   CE1              sBdist1  sBdist2           leaf1 leaf2 leaf3
    |  (172.16.1/30)  |          |               \    |    /
   PE1──────────────CE2(172.16.2/30)             CE3(172.16.3/30)
    |  (10.0.13/30)                               |  (10.0.24/30)
    P1────────────────────────────────────────── P2
    |       (10.0.12/30)                          |
   PE1                                           PE2
```

### Dia chi IP
| Doan mang | Subnet | Mo ta |
|---|---|---|
| Backbone PE1-P1 | 10.0.13.0/30 | PE1=.1, P1=.2 |
| Backbone PE2-P2 | 10.0.24.0/30 | PE2=.1, P2=.2 |
| Backbone P1-P2  | 10.0.12.0/30 | P1=.1, P2=.2 |
| WAN CE1-PE1 | 172.16.1.0/30 | CE1=.2, PE1=.1 |
| WAN CE2-PE1 | 172.16.2.0/30 | CE2=.2, PE1=.1 |
| WAN CE3-PE2 | 172.16.3.0/30 | CE3=.2, PE2=.1 |
| LAN Site A | 192.168.10.0/24 | GW: CE1=.1 |
| LAN Site B | 192.168.20.0/24 | GW: CE2=.1 |
| LAN Site C | 192.168.30.0/24 | GW: CE3=.1 |
| Loopbacks | 10.255.0.1-4/32 | P1,P2,PE1,PE2 |

---

## 🚀 Huong dan chay

### Buoc 1: Tao Task Excel (khong can root)
```bash
cd tkm_cuoi_ky_52300267
pip3 install openpyxl
python3 scripts/create_task_excel.py
# → results/task_list_tkm_52300267.xlsx
```

### Buoc 2: Chay topology Mininet
```bash
sudo python3 main_topology.py
```

### Buoc 3: Do hieu nang (trong Mininet CLI)
```
mininet> py exec(open('scripts/performance_test.py').read(), globals()); full_test(net)
```

### Buoc 4: Kiem tra MPLS thu cong (trong CLI)
```
mininet> pe1 vtysh -c "show mpls ldp binding"
mininet> pe1 vtysh -c "show ip ospf neighbor"
mininet> p1  vtysh -c "show mpls forwarding-table"
mininet> hA1 ping 192.168.20.11
mininet> hA1 traceroute 192.168.30.11
```

### Buoc 5: Tao bao cao Excel (sau khi do xong)
```bash
python3 scripts/generate_excel_report.py
# → results/performance_report_YYYYMMDD_HHMMSS.xlsx
```

### Chay tat ca 1 lenh
```bash
sudo bash run_all.sh
```

---

## 📊 Ket qua can dat (theo de bai)

| Yeu cau | Script | Status |
|---|---|---|
| Site A – Flat Network | main_topology.py | ✅ |
| Site B – 3-Tier (Core-Dist-Access) | main_topology.py | ✅ |
| Site C – Leaf-Spine | main_topology.py | ✅ |
| MPLS Backbone (P1, P2, PE1, PE2) | main_topology.py | ✅ |
| FRR OSPF + LDP | main_topology.py start_frr() | ✅ |
| Ket noi cross-site qua MPLS | performance_test.py | ✅ |
| Do Throughput (iPerf) | performance_test.py | ✅ |
| Do Delay & Jitter (Ping/UDP) | performance_test.py | ✅ |
| Do Packet Loss | performance_test.py | ✅ |
| Do thi so sanh Excel | generate_excel_report.py | ✅ |
| So sanh 3 kien truc LAN | generate_excel_report.py | ✅ |

---

## 🛠 Yeu cau he thong
- Ubuntu 20.04+ / Debian 11+
- Mininet ≥ 2.3.0
- FRRouting (FRR) ≥ 8.0
- Python 3.8+
- `pip3 install openpyxl`
- Kernel modules: `mpls_router`, `mpls_iptunnel`
