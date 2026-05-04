#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import os
import glob

# Tim file JSON moi nhat
files = glob.glob('/tmp/tkm_results/full_report_*.json')
if not files:
    print("Khong tim thay file JSON")
    exit(1)
latest_json = sorted(files)[-1]

with open(latest_json, 'r') as f:
    data = json.load(f)

os.makedirs('baocao/image', exist_ok=True)

# 1. Chart Throughput
labels = [r['label'] for r in data['iperf_tcp']]
values = [r['bandwidth_mbps'] for r in data['iperf_tcp']]

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, values, color=['#3498db', '#e74c3c', '#2ecc71'])
plt.title('So sanh Bang thong TCP (Throughput) giua cac chi nhanh', fontsize=14, fontweight='bold')
plt.ylabel('Mbps', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval} Mbps', ha='center', va='bottom', fontweight='bold')

plt.savefig('baocao/image/chart_throughput.png')
print("Da luu baocao/image/chart_throughput.png")

# 2. Chart Delay (RTT Avg)
labels = [r['label'] for r in data['ping_results']]
values = [r['rtt_avg'] for r in data['ping_results']]

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, values, color=['#f1c40f', '#e67e22', '#1abc9c'])
plt.title('So sanh Do tre trung binh (RTT Avg) giua cac chi nhanh', fontsize=14, fontweight='bold')
plt.ylabel('ms', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval} ms', ha='center', va='bottom', fontweight='bold')

plt.savefig('baocao/image/chart_delay.png')
print("Da luu baocao/image/chart_delay.png")
