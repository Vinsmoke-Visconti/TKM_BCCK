# DANH SACH LENH KIEM THU – Metro Ethernet MPLS
## MSSV: 52300267 | Chay ben trong Mininet CLI

---

## BUOC 0 – Khoi dong mang (terminal root)
```bash
sudo python3 main_topology.py
```

---

## BUOC 1 – Kiem tra ket noi noi bo tung site

### Site A (Flat Network)
```
mininet> hA1 ping -c 3 192.168.10.12
```
**Ket qua mong muon:**
```
3 packets transmitted, 3 received, 0% packet loss
rtt min/avg/max/mdev = 0.x/0.x/0.x/0.x ms   (rat thap, <1ms)
```

### Site B (3-Tier)
```
mininet> hB1 ping -c 3 192.168.20.12
```
**Ket qua mong muon:** 0% loss, RTT < 2ms

### Site C (Leaf-Spine)
```
mininet> hC1 ping -c 3 192.168.30.12
```
**Ket qua mong muon:** 0% loss, RTT < 2ms

---

## BUOC 2 – Kiem tra ket noi cross-site qua MPLS backbone

### Site A → Site B
```
mininet> hA1 ping -c 5 192.168.20.11
```
**Ket qua mong muon:**
```
5 packets transmitted, 5 received, 0% packet loss
rtt min/avg/max/mdev ≈ 10-20/12-22/15-30/1-3 ms
(delay = 2x WAN delay 5ms + backbone 1ms ≈ 11ms)
```

### Site A → Site C
```
mininet> hA1 ping -c 5 192.168.30.11
```
**Ket qua mong muon:** 0% loss, RTT ≈ 12–22ms

### Site B → Site C
```
mininet> hB1 ping -c 5 192.168.30.11
```
**Ket qua mong muon:** 0% loss, RTT ≈ 12–22ms

---

## BUOC 3 – Kiem tra MPLS Control Plane (FRR)

### Kiem tra OSPF neighbor (PE1 phai thay P1)
```
mininet> pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show ip ospf neighbor"
```
**Ket qua mong muon:**
```
Neighbor ID     Pri State     Dead Time Address         Interface
10.255.0.1        1 Full/DR   00:00:35  10.0.13.2       pe1-eth0:10.0.13.1
```

### Kiem tra LDP neighbor (PE1 phai thay P1/P2/PE2)
```
mininet> pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show mpls ldp neighbor"
```
**Ket qua mong muon:**
```
AF   ID              State       Remote Address    Uptime
ipv4 10.255.0.1      OPERATIONAL 10.255.0.1        00:01:xx
```

### Kiem tra LDP binding table
```
mininet> pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show mpls ldp binding"
```
**Ket qua mong muon:** Danh sach cac prefix voi label local/remote

### Kiem tra MPLS forwarding table tren P1
```
mininet> p1 vtysh --vty_socket /tmp/frr_p1 -c "show mpls forwarding-table"
```
**Ket qua mong muon:**
```
 Local  Outgoing    Prefix            Nexthop     Outgoing interface
 label  label       or Tunnel Id      
 16     Pop         10.255.0.3/32     10.0.13.1   p1-eth0
 17     17          10.255.0.4/32     10.0.12.2   p1-eth1
 ...
```

### Kiem tra OSPF routing table
```
mininet> pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show ip route ospf"
```
**Ket qua mong muon:** Thay routes den 10.255.0.1, 10.255.0.2, 10.255.0.4

---

## BUOC 4 – Traceroute (xac nhan duong di qua MPLS)

### Site A → Site C (qua: CE1 → PE1 → P1 → P2 → PE2 → CE3)
```
mininet> hA1 traceroute -n -w 2 192.168.30.11
```
**Ket qua mong muon:**
```
traceroute to 192.168.30.11, 30 hops max
 1  192.168.10.1    ~1ms    (CE1 LAN gateway)
 2  172.16.1.1      ~5ms    (PE1 WAN interface)
 3  10.0.12.2       ~6ms    (P2 via MPLS)
 4  172.16.3.2      ~11ms   (CE3)
 5  192.168.30.11   ~12ms   (hC1 - dich)
```

### Site B → Site A
```
mininet> hB1 traceroute -n -w 2 192.168.10.11
```

---

## BUOC 5 – Do hieu nang tu dong

### Chay performance_test.py (2 lenh rieng biet)
```
mininet> py exec(open('scripts/performance_test.py').read(), globals())
mininet> py full_test(net)
```
**Ket qua mong muon:**
```
[1] PING TESTS ...
  Ping A->B: RTT avg≈12ms | Loss=0%
  Ping A->C: RTT avg≈12ms | Loss=0%
  Ping B->C: RTT avg≈12ms | Loss=0%

[2] IPERF TCP ...
  B->A TCP: ~90-94 Mbps  (gioi han WAN 100Mbps)
  C->A TCP: ~90-94 Mbps
  C->B TCP: ~90-94 Mbps

[3] IPERF UDP ...
  B->A UDP: ~49 Mbps | Jitter<1ms | Loss<1%
  C->A UDP: ~49 Mbps | Jitter<1ms | Loss<1%

[4] TRACEROUTE ...  (xem duong di)
[5] MPLS STATE ... (LDP binding, OSPF neighbor)
```

---

## BUOC 6 – Thoat va tao bao cao Excel

```
mininet> exit
```
Sau do (ngoai terminal):
```bash
python3 scripts/generate_excel_report.py
# → results/performance_report_YYYYMMDD_HHMMSS.xlsx
```

---

## TROUBLESHOOTING

| Van de | Nguyen nhan | Fix |
|---|---|---|
| Ping cross-site fail | FRR chua hoi tu | Doi them 30s roi thu lai |
| `show mpls ldp neighbor` trong | LDP module chua load | `sudo modprobe mpls_router` |
| iPerf khong ket noi | iperf server chua start | Script tu khoi dong, cho 1-2s |
| `py` syntax error | Dung `;` trong CLI | Tach ra 2 lenh `py` rieng |
| vtysh khong chay | FRR chua san sang | Cho them 10s sau convergence |
