import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()

    # Slide 1: Title
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "BÁO CÁO ĐỒ ÁN THIẾT KẾ MẠNG"
    subtitle.text = "Đề tài: Thiết kế và triển khai mạng Metro Ethernet sử dụng MPLS\nSinh viên: Huỳnh Nguyễn Quốc Việt - 52300267\nGVHD: ThS. Lê Viết Thanh"

    # Slide 2: Cấu trúc thư mục dự án
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "1. Cấu trúc thư mục & Tổ chức mã nguồn"
    content = slide.placeholders[1]
    content.text = (
        "- tkm_cuoi_ky_52300267/\n"
        "  + configs/: Chứa các file cấu hình mẫu (Templates) cho FRR (OSPF, LDP).\n"
        "  + scripts/: Các công cụ tự động hóa (Vẽ sơ đồ, Đo hiệu năng).\n"
        "  + baocao/: Toàn bộ mã nguồn LaTeX của bài báo cáo.\n"
        "  + main_topology.py: File logic chính để xây dựng mạng trên Mininet.\n"
        "- Lý do chọn: Kiến trúc Modular, tách biệt giữa Logic mạng và Cấu hình dịch vụ."
    )

    # Slide 3: Sơ đồ mạng tổng thể
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "2. Sơ đồ mạng & Kiến trúc hệ thống"
    content = slide.placeholders[1]
    content.text = (
        "- MPLS Backbone: Gồm 2 Router lõi (P) và 2 Router biên (PE).\n"
        "- 3 Chi nhánh (Sites) với 3 kiến trúc LAN đặc thù:\n"
        "  + Site A: Flat Network (Đơn giản).\n"
        "  + Site B: 3-Tier Architecture (Core-Dist-Access).\n"
        "  + Site C: Leaf-Spine Architecture (Hiện đại, tối ưu cho Data Center).\n"
        "- Kết nối: Các chi nhánh kết nối về ISP qua đường truyền WAN 100Mbps."
    )

    # Slide 4: Chức năng các thiết bị
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "3. Vai trò các thiết bị trong hệ thống"
    content = slide.placeholders[1]
    content.text = (
        "- Router P (Provider): Chuyển mạch nhãn tốc độ cao trong mạng lõi.\n"
        "- Router PE (Provider Edge): Gán/Gỡ nhãn (Push/Pop) khi dữ liệu vào/ra mạng lõi.\n"
        "- Router CE (Customer Edge): Định tuyến tĩnh, làm Gateway cho mạng LAN.\n"
        "- Switches: OVS Switches giả lập L2, Site C bật STP để chống Loop.\n"
        "- Hosts: Các máy trạm giả lập luồng dữ liệu (Ping, iPerf)."
    )

    # Slide 5: Chiến lược cấu hình
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "4. Cách thức cấu hình hệ thống"
    content = slide.placeholders[1]
    content.text = (
        "- Mạng lõi (P/PE): Chạy OSPF Area 0 để thông tuyến IP và LDP để trao đổi nhãn.\n"
        "- Kết nối CE-PE: Sử dụng Định tuyến tĩnh (Static Route) trỏ về Default Gateway.\n"
        "- Tự động hóa: Sử dụng Python để sinh file cấu hình FRR động từ Templates.\n"
        "- Cơ chế Redistribution: PE quảng bá các đường mạng LAN của khách hàng vào OSPF thông qua lệnh 'redistribute kernel'."
    )

    # Slide 6: Kiểm tra kết nối & Chuyển mạch nhãn
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "5. Kết quả kiểm tra & Ý nghĩa"
    content = slide.placeholders[1]
    content.text = (
        "- Lệnh Ping: Đạt 0% Packet Loss giữa tất cả các Site (A, B, C).\n"
        "- Lệnh Traceroute: Hiển thị sự hiện diện của nhãn MPLS tại các hop mạng lõi.\n"
        "- Ý nghĩa: Chứng minh gói tin không đi theo định tuyến IP truyền thống mà đang được chuyển mạch nhãn nhanh chóng và an toàn."
    )

    # Slide 7: Phân tích hiệu năng
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "6. Phân tích kết quả đo lường"
    content = slide.placeholders[1]
    content.text = (
        "- Thông lượng (Throughput): Đạt ~100Mbps (xuyên Backbone) và ~190Mbps (nội bộ PE).\n"
        "- Độ trễ (Delay): Ổn định ở mức ~26ms cho các chi nhánh cách xa nhau.\n"
        "- So sánh: Leaf-Spine cho thấy băng thông ổn định nhất khi tải nặng.\n"
        "- MPLS giúp giảm tải xử lý cho các Router lõi bằng cách gỡ nhãn tại chặng áp chót (PHP)."
    )

    # Slide 8: Kết luận
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "7. Kết luận"
    content = slide.placeholders[1]
    content.text = (
        "- Đồ án đã triển khai thành công mô hình Metro Ethernet MPLS thực tế.\n"
        "- Giải quyết được bài toán kết nối đa chi nhánh có kiến trúc LAN khác biệt.\n"
        "- Hệ thống hoạt động ổn định, hiệu năng cao và đáp ứng đủ các tiêu chuẩn kỹ thuật.\n"
        "- Nắm vững kỹ năng sử dụng Mininet, FRRouting và các công cụ đo lường mạng."
    )

    save_path = "baocao/thuyet_minh_do_an.pptx"
    prs.save(save_path)
    print(f"Presentation saved to {save_path}")

if __name__ == "__main__":
    create_presentation()
