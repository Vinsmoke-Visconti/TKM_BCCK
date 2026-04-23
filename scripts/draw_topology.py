#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script ve so do mang tu dong bang NetworkX va Matplotlib.
Ban cap nhat: Khung anh rong hon, Tieng Viet co dau, khong bi chong cheo.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
import networkx as nx

# Load font Roboto ho tro tieng Viet hoan hao
try:
    fm.fontManager.addfont('docs/fonts/Roboto-Regular.ttf')
    fm.fontManager.addfont('docs/fonts/Roboto-Bold.ttf')
    plt.rcParams['font.family'] = 'Roboto'
except Exception as e:
    print(f"[WARNING] Khong load duoc font Roboto: {e}")
    plt.rcParams['font.family'] = 'sans-serif'

def main():
    print("[INFO] Đang tạo sơ đồ mạng nâng cao bằng Matplotlib & NetworkX...")
    G = nx.Graph()

    # Khai báo tọa độ (X, Y)
    pos = {}
    
    # 1. MPLS Backbone
    pos['P1']  = (4, 5)
    pos['P2']  = (6, 5)
    pos['PE1'] = (3, 5)
    pos['PE2'] = (7, 5)
    
    # 2. Customer Edges
    pos['CE1'] = (2, 6.5)
    pos['CE2'] = (2, 3.5)
    pos['CE3'] = (8, 5)

    # 3. Site A - Flat Network (Top Left)
    pos['sA']  = (1, 6.5)
    pos['hA1'] = (0, 7.5)
    pos['hA2'] = (0, 6.5)
    pos['hA3'] = (0, 5.5)

    # 4. Site B - 3-Tier (Bottom Left)
    pos['sBcore']  = (1, 3.5)
    pos['sBdist1'] = (0, 4.2)
    pos['sBdist2'] = (0, 2.8)
    pos['hB1']     = (-1, 4.5)
    pos['hB2']     = (-1, 3.9)
    pos['hB3']     = (-1, 3.1)
    pos['hB4']     = (-1, 2.5)

    # 5. Site C - Leaf Spine (Right)
    pos['spine1'] = (9, 6)
    pos['spine2'] = (9, 4)
    pos['leaf1']  = (10, 6.5)
    pos['leaf2']  = (10, 5)
    pos['leaf3']  = (10, 3.5)
    pos['hC1']    = (11, 6.5)
    pos['hC2']    = (11, 5)
    pos['hC3']    = (11, 3.5)

    for node in pos.keys():
        G.add_node(node)

    edges = [
        ('PE1', 'P1'), ('P1', 'P2'), ('P2', 'PE2'),
        ('CE1', 'PE1'), ('CE2', 'PE1'), ('CE3', 'PE2'),
        ('sA', 'CE1'), ('hA1', 'sA'), ('hA2', 'sA'), ('hA3', 'sA'),
        ('sBcore', 'CE2'), ('sBdist1', 'sBcore'), ('sBdist2', 'sBcore'),
        ('hB1', 'sBdist1'), ('hB2', 'sBdist1'), ('hB3', 'sBdist2'), ('hB4', 'sBdist2'),
        ('leaf1', 'spine1'), ('leaf1', 'spine2'),
        ('leaf2', 'spine1'), ('leaf2', 'spine2'),
        ('leaf3', 'spine1'), ('leaf3', 'spine2'),
        ('spine1', 'CE3'), ('spine2', 'CE3'),
        ('hC1', 'leaf1'), ('hC2', 'leaf2'), ('hC3', 'leaf3')
    ]
    G.add_edges_from(edges)

    colors = []
    node_sizes = []
    for node in G.nodes():
        if node.startswith('P'):
            colors.append('#E74C3C') 
            node_sizes.append(1400)
        elif node.startswith('CE'):
            colors.append('#F39C12') 
            node_sizes.append(1200)
        elif node.startswith('h'):
            colors.append('#3498DB') 
            node_sizes.append(700)
        else:
            colors.append('#2ECC71') 
            node_sizes.append(900)

    # Nới rộng figure size để chứa được bảng và text box
    fig, ax = plt.subplots(figsize=(24, 14), facecolor='white')
    
    # --- VẼ CÁC KHUNG CHỮ NHẬT (REGIONS) ---
    # Site A (Top Left)
    ax.add_patch(Rectangle((-0.5, 5.0), 3.0, 3.0, fill=True, color='#D6EAF8', alpha=0.5, zorder=0))
    plt.text(1.0, 7.8, "Site A: Flat Network\n(192.168.10.0/24)", fontsize=13, fontweight='bold', color='#154360', ha='center')

    # Site B (Bottom Left)
    ax.add_patch(Rectangle((-1.5, 2.0), 4.0, 3.0, fill=True, color='#D5F5E3', alpha=0.5, zorder=0))
    plt.text(0.5, 2.0, "Site B: 3-Tier Architecture\n(192.168.20.0/24)", fontsize=13, fontweight='bold', color='#145A32', ha='center')

    # Site C (Right)
    ax.add_patch(Rectangle((7.5, 3.0), 4.0, 4.0, fill=True, color='#FCF3CF', alpha=0.5, zorder=0))
    plt.text(9.5, 7.2, "Site C: Leaf-Spine\n(192.168.30.0/24)", fontsize=13, fontweight='bold', color='#7D6608', ha='center')

    # MPLS Backbone (Center)
    ax.add_patch(Rectangle((2.5, 4.3), 5.0, 1.4, fill=True, color='#FADBD8', alpha=0.5, zorder=0))
    plt.text(5.0, 5.8, "MPLS LDP Backbone\n(OSPF Area 0)", fontsize=13, fontweight='bold', color='#7B241C', ha='center')

    # --- VẼ ĐỒ THỊ ---
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors, node_size=node_sizes, 
            font_size=10, font_weight='bold', edge_color='#7F8C8D', width=2.5)

    # --- BẢNG CHÚ THÍCH IP (LEGEND TABLE) ---
    ip_table_data = [
        ["Phân vùng", "Thiết bị / Vùng", "Subnet / IP Address", "Ghi chú"],
        ["Backbone", "PE1 - P1", "10.0.13.0/30", "Kết nối Core ISP"],
        ["Backbone", "P1 - P2", "10.0.12.0/30", "Kết nối Core ISP"],
        ["Backbone", "P2 - PE2", "10.0.24.0/30", "Kết nối Core ISP"],
        ["Backbone", "Loopback (P/PE)", "10.255.0.x / 32", "Dùng cho OSPF & LDP Router-ID"],
        ["WAN Links", "CE1 - PE1", "172.16.1.0/30", "Uplink Site A (100Mbps)"],
        ["WAN Links", "CE2 - PE1", "172.16.2.0/30", "Uplink Site B (100Mbps)"],
        ["WAN Links", "CE3 - PE2", "172.16.3.0/30", "Uplink Site C (100Mbps)"],
        ["LAN Site A", "Gateway CE1", "192.168.10.1", "Mạng nội bộ Site A"],
        ["LAN Site B", "Gateway CE2", "192.168.20.1", "Mạng nội bộ Site B"],
        ["LAN Site C", "Gateway CE3", "192.168.30.1", "Mạng nội bộ Site C"],
    ]
    
    # Di dời bảng xuống cực thấp ở góc phải (giảm chiều cao xuống để không đè vào đồ thị)
    table = plt.table(cellText=ip_table_data[1:], colLabels=ip_table_data[0], 
                      loc='bottom', cellLoc='left', bbox=[0.55, 0.05, 0.45, 0.22])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2C3E50')
        else:
            cell.set_facecolor('#F8F9F9')

    # --- CHÚ THÍCH CÁCH HOẠT ĐỘNG ---
    operation_text = (
        "NGUYÊN LÝ HOẠT ĐỘNG CỦA SƠ ĐỒ:\n\n"
        "1. Định tuyến nội bộ (IGP):\n"
        "   - OSPF Area 0 được cấu hình trên các Router PE và P để học đường đi giữa các Loopback IP.\n"
        "   - Router CE sử dụng Static Route trỏ về PE, và PE redistribute (phân phối) vào OSPF.\n\n"
        "2. Chuyển mạch nhãn (MPLS Label Switching):\n"
        "   - LDP tự động gán và phân phối Nhãn (Label) cho các prefix học được từ OSPF.\n"
        "   - Khi Site A gửi gói tin sang Site C, PE1 (Ingress LSR) sẽ gắn nhãn vào gói tin (Push).\n"
        "   - P1, P2 (Transit LSR) chỉ chuyển tiếp dựa trên nhãn ở Layer 2.5 mà không cần đọc IP (Swap).\n"
        "   - P2 (Penultimate Hop Popping) gỡ nhãn trước khi đến PE2, giúp PE2 xử lý nhanh hơn.\n\n"
        "3. Kiến trúc LAN:\n"
        "   - Site A: Dùng mạng phẳng (Flat) phù hợp cho quy mô nhỏ.\n"
        "   - Site B: Mô hình 3 lớp (Core-Dist-Access) có tính sẵn sàng cao.\n"
        "   - Site C: Kiến trúc Leaf-Spine hiện đại, phù hợp Data Center và Scale-Out."
    )
    
    # Di dời text box xuống góc trái, đảm bảo y âm sâu để không đè vào site B
    plt.text(-1.5, -2.5, operation_text, fontsize=12,
             bbox=dict(facecolor='#EAECEE', alpha=0.9, edgecolor='#7F8C8D', boxstyle='round,pad=1.5'))

    # Dịch title lên trên một chút cho cân đối
    plt.text(5.0, 9.5, "SƠ ĐỒ KIẾN TRÚC MẠNG METRO ETHERNET MPLS TỔNG THỂ", 
             fontsize=24, fontweight='bold', color='#1A5276', ha='center')
    
    # Ẩn trục tọa độ
    ax.axis('off')
    
    # Thiết lập giới hạn trục y mở rộng xuống dưới (-4) để chứa vừa nguyên lý hoạt động
    ax.set_xlim(-2, 12)
    ax.set_ylim(-3.5, 10.0)

    os.makedirs("docs", exist_ok=True)
    out_file = "docs/network_topology.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"[OK] Đã lưu sơ đồ mạng độ phân giải 300dpi tại: {out_file}")

if __name__ == '__main__':
    main()
