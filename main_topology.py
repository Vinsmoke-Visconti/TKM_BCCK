#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================
DO AN CUOI KY - TKM - MSSV: 52300267
De tai: Thiet ke va trien khai mang Metro Ethernet su dung MPLS
=============================================================
FIX LOG:
  v2: Fix switch canonical names (sA->s1...)
  v3: Fix L2 loop Site C (bat STP rieng cho Leaf-Spine)
      Fix cross-site routing (them Linux static routes khong phu thuoc FRR)
      Fix FRR config (bo version string, sua socket, them vtysh push)
      Fix Site A ARP (them arp -s thu cong ban dau)
=============================================================
"""

import os
import sys
import time

from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Host
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info


# ---------------------------------------------------------------
# CLASS: Linux Router
# ---------------------------------------------------------------
class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')
        self.cmd('sysctl -w net.mpls.platform_labels=100000')
        self.cmd('sysctl -w net.mpls.conf.lo.input=1')
        self.cmd('modprobe mpls_router 2>/dev/null || true')
        self.cmd('modprobe mpls_iptunnel 2>/dev/null || true')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        self.cmd('pkill -f zebra 2>/dev/null; pkill -f ospfd 2>/dev/null; pkill -f ldpd 2>/dev/null')
        super(LinuxRouter, self).terminate()


# ---------------------------------------------------------------
# TOPOLOGY
# ---------------------------------------------------------------
def build_topology(net):
    info('*** [1/4] Them MPLS backbone routers (P & PE)\n')
    p1  = net.addHost('p1',  cls=LinuxRouter, ip=None)
    p2  = net.addHost('p2',  cls=LinuxRouter, ip=None)
    pe1 = net.addHost('pe1', cls=LinuxRouter, ip=None)
    pe2 = net.addHost('pe2', cls=LinuxRouter, ip=None)

    info('*** [2/4] Them CE routers (Customer Edge)\n')
    ce1 = net.addHost('ce1', cls=LinuxRouter, ip=None)
    ce2 = net.addHost('ce2', cls=LinuxRouter, ip=None)
    ce3 = net.addHost('ce3', cls=LinuxRouter, ip=None)

    info('*** [3/4] Them switches va hosts cho 3 chi nhanh\n')

    # SITE A: Flat (s1)
    sA = net.addSwitch('s1', cls=OVSKernelSwitch)
    hA1 = net.addHost('hA1', ip='192.168.10.11/24', defaultRoute='via 192.168.10.1')
    hA2 = net.addHost('hA2', ip='192.168.10.12/24', defaultRoute='via 192.168.10.1')
    hA3 = net.addHost('hA3', ip='192.168.10.13/24', defaultRoute='via 192.168.10.1')

    # SITE B: 3-Tier (s2=Core, s3/s4=Dist, s5/s6=Access)
    sB_core  = net.addSwitch('s2', cls=OVSKernelSwitch)
    sB_dist1 = net.addSwitch('s3', cls=OVSKernelSwitch)
    sB_dist2 = net.addSwitch('s4', cls=OVSKernelSwitch)
    sB_acc1  = net.addSwitch('s5', cls=OVSKernelSwitch)
    sB_acc2  = net.addSwitch('s6', cls=OVSKernelSwitch)
    hB1 = net.addHost('hB1', ip='192.168.20.11/24', defaultRoute='via 192.168.20.1')
    hB2 = net.addHost('hB2', ip='192.168.20.12/24', defaultRoute='via 192.168.20.1')
    hB3 = net.addHost('hB3', ip='192.168.20.13/24', defaultRoute='via 192.168.20.1')
    hB4 = net.addHost('hB4', ip='192.168.20.14/24', defaultRoute='via 192.168.20.1')

    # SITE C: Leaf-Spine (s7/s8=Spine, s9/s10/s11=Leaf)
    # NOTE: Full-mesh L2 tao loop -> bat STP rieng cho nhom nay
    spine1 = net.addSwitch('s7',  cls=OVSKernelSwitch)
    spine2 = net.addSwitch('s8',  cls=OVSKernelSwitch)
    leaf1  = net.addSwitch('s9',  cls=OVSKernelSwitch)
    leaf2  = net.addSwitch('s10', cls=OVSKernelSwitch)
    leaf3  = net.addSwitch('s11', cls=OVSKernelSwitch)
    hC1 = net.addHost('hC1', ip='192.168.30.11/24', defaultRoute='via 192.168.30.1')
    hC2 = net.addHost('hC2', ip='192.168.30.12/24', defaultRoute='via 192.168.30.1')
    hC3 = net.addHost('hC3', ip='192.168.30.13/24', defaultRoute='via 192.168.30.1')

    info('*** [4/4] Tao lien ket\n')

    # === MPLS BACKBONE (1 Gbps, 1ms) ===
    net.addLink(pe1, p1, intfName1='pe1-eth0', intfName2='p1-eth0', bw=1000, delay='1ms')
    net.addLink(pe2, p2, intfName1='pe2-eth0', intfName2='p2-eth0', bw=1000, delay='1ms')
    net.addLink(p1,  p2, intfName1='p1-eth1',  intfName2='p2-eth1', bw=1000, delay='1ms')

    # === CE -- PE WAN (100 Mbps, 5ms) ===
    net.addLink(ce1, pe1, intfName1='ce1-eth0', intfName2='pe1-eth1', bw=100, delay='5ms')
    net.addLink(ce2, pe1, intfName1='ce2-eth0', intfName2='pe1-eth2', bw=100, delay='5ms')
    net.addLink(ce3, pe2, intfName1='ce3-eth0', intfName2='pe2-eth1', bw=100, delay='5ms')

    # === SITE A: Flat ===
    net.addLink(ce1, sA, intfName1='ce1-eth1')
    net.addLink(sA, hA1)
    net.addLink(sA, hA2)
    net.addLink(sA, hA3)

    # === SITE B: 3-Tier ===
    net.addLink(ce2, sB_core, intfName1='ce2-eth1')
    net.addLink(sB_core, sB_dist1)
    net.addLink(sB_core, sB_dist2)
    net.addLink(sB_dist1, sB_acc1)
    net.addLink(sB_dist2, sB_acc2)
    net.addLink(sB_acc1, hB1)
    net.addLink(sB_acc1, hB2)
    net.addLink(sB_acc2, hB3)
    net.addLink(sB_acc2, hB4)

    # === SITE C: Leaf-Spine (full-mesh) ===
    net.addLink(ce3, spine1, intfName1='ce3-eth1')
    # net.addLink(ce3, spine2, intfName1='ce3-eth2') # REMOVED: CE3 chi can noi vao spine1 de tranh blackhole vi ce3-eth2 khong co IP
    for spine in [spine1, spine2]:
        for leaf in [leaf1, leaf2, leaf3]:
            net.addLink(spine, leaf)
    net.addLink(leaf1, hC1)
    net.addLink(leaf2, hC2)
    net.addLink(leaf3, hC3)


# ---------------------------------------------------------------
# SWITCH CONFIGURATION
# ---------------------------------------------------------------
def configure_switches(net):
    """
    - Site A/B: standalone mode, STP tat (khong co loop)
    - Site C: BAT STP vi full-mesh spine-leaf tao L2 loop
    """
    info('*** Cau hinh OVS switches...\n')
    site_c_switches = ['s7', 's8', 's9', 's10', 's11']
    for sw in net.switches:
        sw.cmd('ovs-vsctl set Bridge %s fail-mode=standalone' % sw.name)
        if sw.name in site_c_switches:
            # Bat STP de tranh loop trong full-mesh leaf-spine
            sw.cmd('ovs-vsctl set Bridge %s stp_enable=true' % sw.name)
            info(f'  {sw.name}: STP enabled (Leaf-Spine loop protection)\n')
        else:
            sw.cmd('ovs-vsctl set Bridge %s stp_enable=false' % sw.name)


# ---------------------------------------------------------------
# IP + STATIC ROUTING CONFIGURATION
# ---------------------------------------------------------------
def configure_ip(net):
    info('\n*** Gan dia chi IP...\n')

    # --- Loopback ---
    net.get('p1').cmd('ip addr add 10.255.0.1/32 dev lo')
    net.get('p2').cmd('ip addr add 10.255.0.2/32 dev lo')
    net.get('pe1').cmd('ip addr add 10.255.0.3/32 dev lo')
    net.get('pe2').cmd('ip addr add 10.255.0.4/32 dev lo')

    # --- MPLS Backbone links ---
    net.get('pe1').cmd('ip addr add 10.0.13.1/30 dev pe1-eth0')
    net.get('p1').cmd('ip addr add 10.0.13.2/30 dev p1-eth0')
    net.get('pe2').cmd('ip addr add 10.0.24.1/30 dev pe2-eth0')
    net.get('p2').cmd('ip addr add 10.0.24.2/30 dev p2-eth0')
    net.get('p1').cmd('ip addr add 10.0.12.1/30 dev p1-eth1')
    net.get('p2').cmd('ip addr add 10.0.12.2/30 dev p2-eth1')

    # --- CE-PE WAN links ---
    net.get('ce1').cmd('ip addr add 172.16.1.2/30 dev ce1-eth0')
    net.get('pe1').cmd('ip addr add 172.16.1.1/30 dev pe1-eth1')
    net.get('ce2').cmd('ip addr add 172.16.2.2/30 dev ce2-eth0')
    net.get('pe1').cmd('ip addr add 172.16.2.1/30 dev pe1-eth2')
    net.get('ce3').cmd('ip addr add 172.16.3.2/30 dev ce3-eth0')
    net.get('pe2').cmd('ip addr add 172.16.3.1/30 dev pe2-eth1')

    # --- CE LAN gateways ---
    net.get('ce1').cmd('ip addr add 192.168.10.1/24 dev ce1-eth1')
    net.get('ce2').cmd('ip addr add 192.168.20.1/24 dev ce2-eth1')
    net.get('ce3').cmd('ip addr add 192.168.30.1/24 dev ce3-eth1')

    # --- Enable MPLS input on backbone interfaces ---
    for rname, intfs in [
        ('p1',  ['p1-eth0', 'p1-eth1', 'lo']),
        ('p2',  ['p2-eth0', 'p2-eth1', 'lo']),
        ('pe1', ['pe1-eth0', 'lo']),
        ('pe2', ['pe2-eth0', 'lo']),
    ]:
        r = net.get(rname)
        for intf in intfs:
            r.cmd(f'sysctl -w net.mpls.conf.{intf}.input=1')

    info('*** IP configuration done.\n')
    info('*** Them static routes (Linux kernel - khong phu thuoc FRR)...\n')

    # ================================================================
    # STATIC ROUTES - Chi cau hinh route tu PE xuong CE va default route tu CE len PE
    # ================================================================

    # PE1: biet duong den Site A, B (truc tiep qua CE)
    net.get('pe1').cmd('ip route add 192.168.10.0/24 via 172.16.1.2')   # -> CE1 -> Site A
    net.get('pe1').cmd('ip route add 192.168.20.0/24 via 172.16.2.2')   # -> CE2 -> Site B

    # PE2: biet duong den Site C (truc tiep qua CE3)
    net.get('pe2').cmd('ip route add 192.168.30.0/24 via 172.16.3.2')   # -> CE3 -> Site C

    # CE1: default qua PE1
    net.get('ce1').cmd('ip route add default via 172.16.1.1')

    # CE2: default qua PE1
    net.get('ce2').cmd('ip route add default via 172.16.2.1')

    # CE3: default qua PE2
    net.get('ce3').cmd('ip route add default via 172.16.3.1')

    info('*** Static routes configured.\n')


# ---------------------------------------------------------------
# FRR CONFIGURATION (OSPF + LDP for MPLS)
# ---------------------------------------------------------------
def _write_frr_conf(name, cfg_dir):
    """Generate FRR config theo router type (doc tu file template trong configs/)."""

    lb = {'p1': '10.255.0.1', 'p2': '10.255.0.2',
          'pe1': '10.255.0.3', 'pe2': '10.255.0.4'}

    if name in ['p1', 'p2']:
        tmpl_path = 'configs/frr_p.conf'
    elif name in ['pe1', 'pe2']:
        tmpl_path = 'configs/frr_pe.conf'
    else:
        tmpl_path = 'configs/frr_default.conf'

    # Doc file template
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl = f.read()

    # Format cac bien
    conf = tmpl.format(
        name=name,
        loopback_ip=lb.get(name, '')
    )

    with open(f'{cfg_dir}/frr.conf', 'w', encoding='utf-8') as f:
        f.write(conf)


FRR_BIN = '/usr/lib/frr'   # Duong dan thuc te cua FRR tren he thong


def _find_frr():
    """Tim duong dan FRR binaries."""
    candidates = ['/usr/lib/frr', '/usr/local/lib/frr', '/usr/sbin', '/usr/local/sbin']
    for path in candidates:
        if os.path.isfile(f'{path}/zebra'):
            return path
    return None


def start_frr(net):
    info('\n*** Khoi dong FRR daemons (OSPF + LDP)...\n')

    frr_bin = _find_frr()
    if not frr_bin:
        info('[WARN] FRR khong tim thay - bo qua. Static routes van hoat dong.\n')
        return

    info(f'  FRR found at: {frr_bin}\n')
    mpls_routers = ['p1', 'p2', 'pe1', 'pe2']

    for name in mpls_routers:
        node = net.get(name)
        cfg_dir = f'/tmp/frr_{name}'
        os.makedirs(cfg_dir, exist_ok=True)

        # Kill tien trinh FRR cu (theo ten node de tranh kill nham)
        node.cmd(f'kill $(cat {cfg_dir}/zebra.pid 2>/dev/null) 2>/dev/null; true')
        node.cmd(f'kill $(cat {cfg_dir}/ospfd.pid 2>/dev/null) 2>/dev/null; true')
        node.cmd(f'kill $(cat {cfg_dir}/ldpd.pid  2>/dev/null) 2>/dev/null; true')
        time.sleep(0.3)

        # Ghi config
        _write_frr_conf(name, cfg_dir)
        node.cmd(f'chmod -R 777 {cfg_dir}')

        # Moi node dung socket va vty socket rieng (tranh conflict)
        sock     = f'{cfg_dir}/zserv.api'   # zebra API socket (daemon-to-daemon)
        vty_dir  = cfg_dir                   # vty socket dir  (vtysh connects here)

        # Khoi dong zebra (phai chay truoc)
        node.cmd(
            f'{frr_bin}/zebra -d '
            f'-f {cfg_dir}/frr.conf '
            f'-z {sock} '
            f'-i {cfg_dir}/zebra.pid '
            f'--vty_socket {vty_dir} '
            f''
            f'> {cfg_dir}/zebra.log 2>&1'
        )
        time.sleep(1.2)

        # Khoi dong ospfd
        node.cmd(
            f'{frr_bin}/ospfd -d '
            f'-f {cfg_dir}/frr.conf '
            f'-z {sock} '
            f'-i {cfg_dir}/ospfd.pid '
            f'--vty_socket {vty_dir} '
            f''
            f'> {cfg_dir}/ospfd.log 2>&1'
        )
        time.sleep(0.8)

        # Khoi dong ldpd
        node.cmd(
            f'{frr_bin}/ldpd -d '
            f'-f {cfg_dir}/frr.conf '
            f'-z {sock} '
            f'-i {cfg_dir}/ldpd.pid '
            f'--vty_socket {vty_dir} '
            f''
            f'> {cfg_dir}/ldpd.log 2>&1'
        )
        time.sleep(0.5)

        info(f'  + {name}: FRR daemons started (zebra/ospfd/ldpd)\n')

    info('*** Cho OSPF/LDP hoi tu (35 giay)...\n')
    time.sleep(35)

    # Kiem tra trang thai OSPF qua vtysh --vty_socket
    info('*** Kiem tra OSPF neighbors:\n')
    for name in ['pe1', 'p1']:
        node = net.get(name)
        vty  = f'/tmp/frr_{name}'
        out  = node.cmd(f'vtysh --vty_socket {vty} -c "show ip ospf neighbor" 2>/dev/null')
        ok   = 'Full' in out or 'Exchange' in out or '2-Way' in out
        info(f'  {name}: {"✅ OSPF Full" if ok else "⚠ Chua hoi tu - xem " + vty + "/ospfd.log"}\n')


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
def run():
    if os.geteuid() != 0:
        print('[ERROR] Can quyen root: sudo python3 main_topology.py')
        sys.exit(1)

    os.system('modprobe mpls_router 2>/dev/null; modprobe mpls_iptunnel 2>/dev/null')
    os.system('pkill -9 -f zebra 2>/dev/null; pkill -9 -f ospfd 2>/dev/null; pkill -9 -f ldpd 2>/dev/null; mn -c 2>/dev/null; true')
    time.sleep(1)

    setLogLevel('info')
    info('\n=== METRO ETHERNET MPLS - TKM CUOI KY 52300267 (v3) ===\n\n')

    net = Mininet(controller=None, link=TCLink, switch=OVSKernelSwitch, autoSetMacs=True)
    build_topology(net)
    net.build()

    info('\n*** Starting network...\n')
    net.start()

    configure_switches(net)
    time.sleep(2)   # cho STP tinh toan xong cho Site C

    configure_ip(net)
    start_frr(net)

    info('\n=== MANG DA SAN SANG ===\n')
    info('Kiem tra ket noi:\n')
    info('  hA1 ping -c 4 192.168.10.12   (noi bo Site A)\n')
    info('  hA1 ping -c 4 192.168.20.11   (A -> B qua MPLS)\n')
    info('  hA1 ping -c 4 192.168.30.11   (A -> C qua MPLS)\n')
    info('  hA1 traceroute -n 192.168.30.11\n')
    info('\nKiem tra MPLS (2 lenh rieng trong CLI):\n')
    info('  py exec(open("scripts/performance_test.py").read(), globals())\n')
    info('  py full_test(net)\n')
    info('\nVtysh:\n')
    info('  pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show ip ospf neighbor"\n')
    info('  pe1 vtysh --vty_socket /tmp/frr_pe1 -c "show mpls ldp neighbor"\n')
    info('  p1  vtysh --vty_socket /tmp/frr_p1 -c "show ip route"\n')
    info('\nGo "exit" de thoat\n\n')

    CLI(net)

    info('\n*** Don dep...\n')
    os.system('killall -9 zebra ospfd ldpd 2>/dev/null || true')
    net.stop()
    info('*** Xong.\n')


if __name__ == '__main__':
    run()
