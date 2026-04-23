#!/bin/bash
# run_all.sh – Script tien ich chay toan bo do an
# Chay: chmod +x run_all.sh && sudo ./run_all.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================"
echo " Metro Ethernet MPLS – TKM Cuoi Ky – MSSV: 52300267"
echo "======================================================"

# 1. Kiem tra quyen root
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Can quyen root. Chay: sudo ./run_all.sh"
    exit 1
fi

# 2. Cai openpyxl neu chua co
python3 -c "import openpyxl" 2>/dev/null || {
    echo "[INFO] Cai dat openpyxl..."
    pip3 install openpyxl -q
}

# 3. Load MPLS modules
echo "[INFO] Load MPLS kernel modules..."
modprobe mpls_router 2>/dev/null || true
modprobe mpls_iptunnel 2>/dev/null || true

# 4. Don dep tien trinh cu
echo "[INFO] Don dep tien trinh cu..."
pkill -f "python3 main_topology" 2>/dev/null || true
pkill -f zebra 2>/dev/null || true
pkill -f ospfd 2>/dev/null || true
pkill -f ldpd  2>/dev/null || true
mn -c 2>/dev/null || true
sleep 1

# 5. Tao thu muc ket qua
mkdir -p results /tmp/tkm_results

# 6. Tao Task Excel
echo "[INFO] Tao task list Excel..."
python3 scripts/create_task_excel.py

# 7. Chay topology
echo "[INFO] Khoi dong topology Mininet..."
echo "       Sau khi CLI xuat hien, chay:"
echo "       py exec(open('scripts/performance_test.py').read(), globals()); full_test(net)"
echo ""
python3 main_topology.py

# 8. Sau khi thoat Mininet, tao bao cao Excel
echo "[INFO] Tao bao cao Excel hieu nang..."
python3 scripts/generate_excel_report.py

echo ""
echo "[DONE] Hoan thanh! Xem ket qua trong thu muc results/"
ls -la results/
