#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
performance_test.py
-------------------
Script do luong hieu nang mang Metro MPLS:
  - Ping (Delay, Packet Loss, Jitter)
  - iPerf (Throughput)
  - Traceroute (Duong di goi tin)

Chay TRONG Mininet CLI:
  py exec(open('scripts/performance_test.py').read())

Hoac chay truc tiep tu run() da tich hop trong main_topology.py
"""

import os
import re
import time
import json
import subprocess
from datetime import datetime


RESULTS_DIR = '/tmp/tkm_results'

def ensure_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------
def run_ping(src, dst_ip, count=20, interval=0.2):
    """
    Chay ping tu host src den dst_ip.
    Tra ve dict: {rtt_min, rtt_avg, rtt_max, rtt_mdev, loss_pct}
    """
    cmd = f'ping -c {count} -i {interval} -W 2 {dst_ip}'
    out = src.cmd(cmd)

    result = {
        'src': src.name,
        'dst': dst_ip,
        'sent': count,
        'loss_pct': 100.0,
        'rtt_min': None,
        'rtt_avg': None,
        'rtt_max': None,
        'rtt_mdev': None,
    }

    # Parse packet loss
    m = re.search(r'(\d+)% packet loss', out)
    if m:
        result['loss_pct'] = float(m.group(1))

    # Parse RTT
    m = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', out)
    if m:
        result['rtt_min']  = float(m.group(1))
        result['rtt_avg']  = float(m.group(2))
        result['rtt_max']  = float(m.group(3))
        result['rtt_mdev'] = float(m.group(4))

    return result, out


def run_iperf(server_host, client_host, duration=10, udp=False):
    """
    Chay iperf giua server va client.
    Tra ve dict: {bandwidth_mbps, jitter_ms (UDP only), loss_pct (UDP only)}
    """
    # Khoi dong server
    if udp:
        server_host.cmd(f'iperf -s -u -p 5201 &')
    else:
        server_host.cmd(f'iperf -s -p 5201 &')
    time.sleep(1)

    # Chay client
    if udp:
        out = client_host.cmd(
            f'iperf -c {server_host.IP()} -p 5201 -t {duration} -u -b 50M'
        )
    else:
        out = client_host.cmd(
            f'iperf -c {server_host.IP()} -p 5201 -t {duration}'
        )

    # Dung server
    server_host.cmd('pkill -f "iperf -s" 2>/dev/null || true')

    result = {
        'src': client_host.name,
        'dst': server_host.name,
        'mode': 'UDP' if udp else 'TCP',
        'bandwidth_mbps': None,
        'jitter_ms': None,
        'loss_pct': None,
    }

    # Parse TCP bandwidth
    m = re.search(r'([\d.]+)\s+Mbits/sec', out)
    if m:
        result['bandwidth_mbps'] = float(m.group(1))

    # Parse UDP jitter & loss
    if udp:
        m = re.search(r'([\d.]+)\s+ms\s+\d+/\d+\s+\(([\d.]+)%\)', out)
        if m:
            result['jitter_ms'] = float(m.group(1))
            result['loss_pct']  = float(m.group(2))

    return result, out


def run_traceroute(src, dst_ip):
    """Chay traceroute va tra ve output."""
    out = src.cmd(f'traceroute -n -w 2 {dst_ip}')
    return out


# ---------------------------------------------------------------
def full_test(net):
    """
    Thuc hien bo kiem tra day du va luu ket qua.
    Goi ham nay tu Mininet run() sau khi mang san sang.
    """
    ensure_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report = {
        'timestamp': timestamp,
        'ping_results': [],
        'iperf_tcp': [],
        'iperf_udp': [],
        'traceroutes': {},
    }

    hA1 = net.get('hA1')
    hB1 = net.get('hB1')
    hC1 = net.get('hC1')

    # ---- PING TEST ----
    print('\n[1] PING TESTS - Do Delay & Packet Loss')
    pairs = [
        (hA1, '192.168.20.11', 'A->B'),
        (hA1, '192.168.30.11', 'A->C'),
        (hB1, '192.168.30.11', 'B->C'),
    ]
    for src, dst_ip, label in pairs:
        print(f'  Ping {label} ({src.name} -> {dst_ip})...')
        r, raw = run_ping(src, dst_ip, count=30)
        r['label'] = label
        report['ping_results'].append(r)
        print(f'    RTT avg={r["rtt_avg"]} ms | Loss={r["loss_pct"]}%')
        with open(f'{RESULTS_DIR}/ping_{label.replace("->","_")}_{timestamp}.txt', 'w') as f:
            f.write(raw)

    # ---- IPERF TCP ----
    print('\n[2] IPERF TCP - Do Throughput')
    tcp_pairs = [
        (hB1, hA1, 'B->A TCP'),
        (hC1, hA1, 'C->A TCP'),
        (hC1, hB1, 'C->B TCP'),
    ]
    for server, client, label in tcp_pairs:
        print(f'  iPerf TCP {label}...')
        r, raw = run_iperf(server, client, duration=10, udp=False)
        r['label'] = label
        report['iperf_tcp'].append(r)
        print(f'    Bandwidth: {r["bandwidth_mbps"]} Mbps')
        with open(f'{RESULTS_DIR}/iperf_tcp_{label.replace(" ","_")}_{timestamp}.txt', 'w') as f:
            f.write(raw)

    # ---- IPERF UDP ----
    print('\n[3] IPERF UDP - Do Jitter & Loss')
    udp_pairs = [
        (hB1, hA1, 'B->A UDP'),
        (hC1, hA1, 'C->A UDP'),
    ]
    for server, client, label in udp_pairs:
        print(f'  iPerf UDP {label}...')
        r, raw = run_iperf(server, client, duration=10, udp=True)
        r['label'] = label
        report['iperf_udp'].append(r)
        print(f'    Bandwidth: {r["bandwidth_mbps"]} Mbps | Jitter: {r["jitter_ms"]} ms | Loss: {r["loss_pct"]}%')
        with open(f'{RESULTS_DIR}/iperf_udp_{label.replace(" ","_")}_{timestamp}.txt', 'w') as f:
            f.write(raw)

    # ---- TRACEROUTE ----
    print('\n[4] TRACEROUTE - Xem duong di goi tin')
    tr_pairs = [
        (hA1, '192.168.20.11', 'A_to_B'),
        (hA1, '192.168.30.11', 'A_to_C'),
    ]
    for src, dst_ip, label in tr_pairs:
        print(f'  Traceroute {label}...')
        tr_out = run_traceroute(src, dst_ip)
        report['traceroutes'][label] = tr_out
        print(tr_out)
        with open(f'{RESULTS_DIR}/traceroute_{label}_{timestamp}.txt', 'w') as f:
            f.write(tr_out)

    # ---- MPLS STATE ----
    print('\n[5] MPLS STATE - Kiem tra trang thai MPLS')
    pe1 = net.get('pe1')
    p1  = net.get('p1')
    ldp_out  = pe1.cmd('vtysh -c "show mpls ldp binding" 2>/dev/null || echo "FRR not ready"')
    ospf_out = pe1.cmd('vtysh -c "show ip ospf neighbor" 2>/dev/null || echo "FRR not ready"')
    mpls_fwd = p1.cmd('vtysh -c "show mpls forwarding-table" 2>/dev/null || echo "FRR not ready"')
    with open(f'{RESULTS_DIR}/mpls_state_{timestamp}.txt', 'w') as f:
        f.write('=== LDP BINDINGS (PE1) ===\n')
        f.write(ldp_out + '\n\n')
        f.write('=== OSPF NEIGHBORS (PE1) ===\n')
        f.write(ospf_out + '\n\n')
        f.write('=== MPLS FORWARDING TABLE (P1) ===\n')
        f.write(mpls_fwd + '\n')

    # Luu JSON tong hop
    with open(f'{RESULTS_DIR}/full_report_{timestamp}.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # In bang tong ket
    print_summary(report)
    return report


def print_summary(report):
    """In bang tong ket hieu nang."""
    print('\n' + '='*70)
    print('  BANG THONG KE HIEU NANG MANG METRO ETHERNET MPLS')
    print('='*70)
    print(f'  Thoi gian do: {report["timestamp"]}')
    print()

    print('  [PING - RTT & PACKET LOSS]')
    print(f'  {"Huong":<12} {"RTT Min":>10} {"RTT Avg":>10} {"RTT Max":>10} {"Jitter":>10} {"Loss":>8}')
    print('  ' + '-'*62)
    for r in report['ping_results']:
        print(
            f'  {r.get("label",""):<12} '
            f'{str(r["rtt_min"])+" ms":>10} '
            f'{str(r["rtt_avg"])+" ms":>10} '
            f'{str(r["rtt_max"])+" ms":>10} '
            f'{str(r["rtt_mdev"])+" ms":>10} '
            f'{str(r["loss_pct"])+"%":>8}'
        )

    print()
    print('  [IPERF TCP - THROUGHPUT]')
    print(f'  {"Huong":<14} {"Bandwidth":>15}')
    print('  ' + '-'*32)
    for r in report['iperf_tcp']:
        bw = f'{r["bandwidth_mbps"]} Mbps' if r['bandwidth_mbps'] else 'N/A'
        print(f'  {r.get("label",""):<14} {bw:>15}')

    print()
    print('  [IPERF UDP - JITTER & LOSS]')
    print(f'  {"Huong":<14} {"Bandwidth":>14} {"Jitter":>10} {"Loss":>8}')
    print('  ' + '-'*50)
    for r in report['iperf_udp']:
        bw  = f'{r["bandwidth_mbps"]} Mbps' if r['bandwidth_mbps'] else 'N/A'
        jit = f'{r["jitter_ms"]} ms' if r['jitter_ms'] else 'N/A'
        ls  = f'{r["loss_pct"]}%' if r['loss_pct'] is not None else 'N/A'
        print(f'  {r.get("label",""):<14} {bw:>14} {jit:>10} {ls:>8}')

    print()
    print(f'  Ket qua chi tiet luu tai: {RESULTS_DIR}/')
    print('='*70)


if __name__ == '__main__':
    print('[INFO] Chay script nay tu ben trong Mininet CLI:')
    print('  py exec(open("performance_test.py").read(), globals()); full_test(net)')
