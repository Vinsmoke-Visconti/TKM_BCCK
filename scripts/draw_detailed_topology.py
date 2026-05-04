#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
draw_detailed_topology.py
-------------------------
Ve chi tiet so do topology mang Metro Ethernet MPLS
(Bao gom P, PE, CE, va 3 kien truc LAN: Flat, 3-Tier, Leaf-Spine)
bang matplotlib.
"""
import os, sys
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch
except ImportError:
    print('[ERROR] pip3 install matplotlib'); sys.exit(1)

# Thu muc luu anh
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'docs')
os.makedirs(RESULTS_DIR, exist_ok=True)

def draw():
    fig, ax = plt.subplots(figsize=(22, 14))
    ax.set_xlim(0, 22); ax.set_ylim(0, 14)
    ax.axis('off')
    # Nền màu tối Dark Blue
    fig.patch.set_facecolor('#0D1B2A')
    ax.set_facecolor('#0D1B2A')

    # Color palette
    C = {
        'isp_core': '#E74C3C', 'isp_edge': '#E67E22', 'ce': '#8E44AD',
        'sw_flat': '#16A085', 
        'sw_core': '#2980B9', 'sw_dist': '#27AE60', 'sw_access': '#16A085',
        'sw_spine': '#D35400', 'sw_leaf': '#F39C12',
        'host': '#2C3E50', 'text': 'white', 'link': '#7F8C8D', 'bg': '#111822'
    }

    def box(x, y, w, h, color, label, sublabel='', fontsize=9):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                               boxstyle='round,pad=0.08',
                               facecolor=color, edgecolor='white',
                               linewidth=1.2, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y + (0.15 if sublabel else 0), label,
                ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color='white', zorder=4)
        if sublabel:
            ax.text(x, y - 0.25, sublabel,
                    ha='center', va='center', fontsize=7.5,
                    color='#BDC3C7', zorder=4)

    def link(x1, y1, x2, y2, color='#7F8C8D', lw=1.5, label='', ls='-', zorder=2, label_offset_y=0.1):
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, linestyle=ls, zorder=zorder)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + label_offset_y, label, fontsize=7.5,
                    color='#F1C40F', zorder=5, ha='center', va='bottom',
                    bbox=dict(boxstyle='round', facecolor='#0D1B2A', edgecolor='none', alpha=0.6, pad=0.1))

    def draw_bg_box(x, y, w, h, title, color='#1A252F', edge='#34495E'):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                               boxstyle='round,pad=0.2',
                               facecolor=color, edgecolor=edge,
                               linewidth=2, zorder=1, alpha=0.7)
        ax.add_patch(rect)
        ax.text(x, y + h/2 - 0.4, title, ha='center', va='top', 
                fontsize=12, fontweight='bold', color='white', zorder=2, alpha=0.9)

    # --- TITLE ---
    ax.text(11, 13.5,
            'METRO ETHERNET MPLS TOPOLOGY - MULTI-BRANCH ENTERPRISE',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='white', zorder=5)
    ax.text(11, 13.1,
            'OSPF | LDP (MPLS Label Switching) | Flat, 3-Tier, Leaf-Spine',
            ha='center', va='center', fontsize=11, color='#BDC3C7', zorder=5)

    # --- ISP BACKGROUND ---
    draw_bg_box(11, 10.8, 14.5, 3.2, 'ISP Backbone (MPLS / OSPF Area 0)', color=C['bg'], edge=C['isp_core'])

    # --- ISP CORE (P) ---
    box(8.5, 11.4, 2.4, 0.8, C['isp_core'], 'P1 (Core)', 'IP: 10.255.0.1 (lo)\neth0: 10.0.13.2 | eth1: 10.0.12.1')
    box(13.5, 11.4, 2.4, 0.8, C['isp_core'], 'P2 (Core)', 'IP: 10.255.0.2 (lo)\neth0: 10.0.24.2 | eth1: 10.0.12.2')
    link(8.5+1.2, 11.4, 13.5-1.2, 11.4, color=C['isp_core'], lw=3, label='10.0.12.0/30 (1 Gbps)', label_offset_y=0.1)

    # --- ISP EDGE (PE) ---
    box(5, 9.8, 2.4, 0.8, C['isp_edge'], 'PE1 (Edge)', 'IP: 10.255.0.3 (lo)\neth0: 10.0.13.1 | eth1: 172.16.1.1')
    box(17, 9.8, 2.4, 0.8, C['isp_edge'], 'PE2 (Edge)', 'IP: 10.255.0.4 (lo)\neth0: 10.0.24.1 | eth1: 172.16.3.1\neth2: 172.16.2.1')
    
    link(5, 9.8+0.4, 8.5-0.5, 11.4-0.4, color=C['isp_edge'], lw=2.5, label='10.0.13.0/30')
    link(17, 9.8+0.4, 13.5+0.5, 11.4-0.4, color=C['isp_edge'], lw=2.5, label='10.0.24.0/30')

    # --- CUSTOMER EDGE (CE) ---
    box(3, 7.8, 2.2, 0.8, C['ce'], 'CE1 (Site A GW)', 'eth0: 172.16.1.2\neth1: 192.168.10.1')
    box(11, 7.8, 2.2, 0.8, C['ce'], 'CE2 (Site B GW)', 'eth0: 172.16.2.2\neth1: 192.168.20.1')
    box(19, 7.8, 2.2, 0.8, C['ce'], 'CE3 (Site C GW)', 'eth0: 172.16.3.2\neth1: 192.168.30.1')

    link(3, 7.8+0.4, 5-0.5, 9.8-0.4, color=C['ce'], lw=2, label='172.16.1.0/30')
    link(11, 7.8+0.4, 17-0.8, 9.8-0.4, color=C['ce'], lw=2, label='172.16.2.0/30')
    link(19, 7.8+0.4, 17+0.8, 9.8-0.4, color=C['ce'], lw=2, label='172.16.3.0/30')

    # --- SITE A (FLAT NETWORK) ---
    draw_bg_box(3, 3.8, 4.8, 5.8, 'Site A: Flat Network', color='#0A151C', edge=C['sw_flat'])
    box(3, 5.8, 1.8, 0.7, C['sw_flat'], 's1 (Switch)', 'OVS L2\n(Standalone)')
    link(3, 7.8-0.4, 3, 5.8+0.35, color=C['sw_flat'], lw=2)

    box(1.5, 3.2, 1.3, 0.6, C['host'], 'hA1', '192.168.10.11', 8.5)
    box(3.0, 3.2, 1.3, 0.6, C['host'], 'hA2', '192.168.10.12', 8.5)
    box(4.5, 3.2, 1.3, 0.6, C['host'], 'hA3', '192.168.10.13', 8.5)
    link(3, 5.8-0.35, 1.5, 3.2+0.3, color=C['link'])
    link(3, 5.8-0.35, 3.0, 3.2+0.3, color=C['link'])
    link(3, 5.8-0.35, 4.5, 3.2+0.3, color=C['link'])

    # --- SITE B (3-TIER NETWORK) ---
    draw_bg_box(11, 3.8, 8.8, 5.8, 'Site B: 3-Tier Network', color='#0A151C', edge=C['sw_core'])
    box(11, 5.8, 1.8, 0.7, C['sw_core'], 's2 (Core)', 'OVS L2')
    link(11, 7.8-0.4, 11, 5.8+0.35, color=C['sw_core'], lw=2)

    box(9, 4.4, 1.8, 0.7, C['sw_dist'], 's3 (Dist)', 'OVS L2')
    box(13, 4.4, 1.8, 0.7, C['sw_dist'], 's4 (Dist)', 'OVS L2')
    link(11-0.2, 5.8-0.35, 9, 4.4+0.35, color=C['sw_core'])
    link(11+0.2, 5.8-0.35, 13, 4.4+0.35, color=C['sw_core'])

    box(9, 3.0, 1.8, 0.7, C['sw_access'], 's5 (Access)', 'OVS L2')
    box(13, 3.0, 1.8, 0.7, C['sw_access'], 's6 (Access)', 'OVS L2')
    link(9, 4.4-0.35, 9, 3.0+0.35, color=C['sw_dist'])
    link(13, 4.4-0.35, 13, 3.0+0.35, color=C['sw_dist'])

    box(8, 1.6, 1.3, 0.6, C['host'], 'hB1', '192.168.20.11', 8.5)
    box(10, 1.6, 1.3, 0.6, C['host'], 'hB2', '192.168.20.12', 8.5)
    box(12, 1.6, 1.3, 0.6, C['host'], 'hB3', '192.168.20.13', 8.5)
    box(14, 1.6, 1.3, 0.6, C['host'], 'hB4', '192.168.20.14', 8.5)
    link(9-0.2, 3.0-0.35, 8, 1.6+0.3, color=C['link'])
    link(9+0.2, 3.0-0.35, 10, 1.6+0.3, color=C['link'])
    link(13-0.2, 3.0-0.35, 12, 1.6+0.3, color=C['link'])
    link(13+0.2, 3.0-0.35, 14, 1.6+0.3, color=C['link'])

    # --- SITE C (LEAF-SPINE NETWORK) ---
    draw_bg_box(19, 3.8, 6.2, 5.8, 'Site C: Leaf-Spine (STP Enabled)', color='#0A151C', edge=C['sw_spine'])
    box(17.5, 5.0, 1.8, 0.7, C['sw_spine'], 's7 (Spine)', 'OVS L2')
    box(20.5, 5.0, 1.8, 0.7, C['sw_spine'], 's8 (Spine)', 'OVS L2')
    link(19, 7.8-0.4, 17.5, 5.0+0.35, color=C['sw_spine'], lw=2)

    box(16.5, 3.0, 1.6, 0.7, C['sw_leaf'], 's9 (Leaf)', 'OVS L2')
    box(19.0, 3.0, 1.6, 0.7, C['sw_leaf'], 's10 (Leaf)', 'OVS L2')
    box(21.5, 3.0, 1.6, 0.7, C['sw_leaf'], 's11 (Leaf)', 'OVS L2')

    # Full mesh connections Spine to Leaf
    for spine_x in [17.5, 20.5]:
        for leaf_x in [16.5, 19.0, 21.5]:
            link(spine_x, 5.0-0.35, leaf_x, 3.0+0.35, color=C['sw_leaf'], lw=1.2, zorder=1)

    box(16.5, 1.6, 1.3, 0.6, C['host'], 'hC1', '192.168.30.11', 8.5)
    box(19.0, 1.6, 1.3, 0.6, C['host'], 'hC2', '192.168.30.12', 8.5)
    box(21.5, 1.6, 1.3, 0.6, C['host'], 'hC3', '192.168.30.13', 8.5)
    link(16.5, 3.0-0.35, 16.5, 1.6+0.3, color=C['link'])
    link(19.0, 3.0-0.35, 19.0, 1.6+0.3, color=C['link'])
    link(21.5, 3.0-0.35, 21.5, 1.6+0.3, color=C['link'])

    # --- SUBNET LABELS ---
    ax.text(3, 0.6, 'Subnet: 192.168.10.0/24\nGW: 192.168.10.1', ha='center', fontsize=8.5, color='#16A085',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#16A085', lw=1.5))
    ax.text(11, 0.6, 'Subnet: 192.168.20.0/24\nGW: 192.168.20.1', ha='center', fontsize=8.5, color='#2980B9',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#2980B9', lw=1.5))
    ax.text(19, 0.6, 'Subnet: 192.168.30.0/24\nGW: 192.168.30.1', ha='center', fontsize=8.5, color='#D35400',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1B2A', edgecolor='#D35400', lw=1.5))

    # --- LEGEND ---
    legend_items = [
        mpatches.Patch(color=C['isp_core'], label='P Router (ISP Core Backbone)'),
        mpatches.Patch(color=C['isp_edge'], label='PE Router (ISP Edge - Label Push/Pop)'),
        mpatches.Patch(color=C['ce'],       label='CE Router (Customer Edge Gateway)'),
        mpatches.Patch(color=C['sw_core'],  label='OVS Core/Dist Switch (Site B)'),
        mpatches.Patch(color=C['sw_spine'], label='OVS Spine Switch (Site C)'),
        mpatches.Patch(color=C['sw_leaf'],  label='OVS Leaf/Access/Flat Switch'),
        mpatches.Patch(color=C['host'],     label='End Host (Client Linux Network Namespace)'),
    ]
    ax.legend(handles=legend_items, loc='lower left', fontsize=9.5,
              facecolor='#1A252F', edgecolor='white',
              labelcolor='white', framealpha=0.9, bbox_to_anchor=(0.015, 0.015))

    plt.tight_layout()
    out = os.path.join(RESULTS_DIR, 'network_detailed_topology.png')
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'[OK] Sơ đồ mạng chi tiết đã được tạo thành công tại: {out}')
    return out

if __name__ == '__main__':
    draw()
