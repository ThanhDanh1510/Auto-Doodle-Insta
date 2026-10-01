# 🧠 Phân Hệ `src.vision` - Computer Vision & Painting Engine

Phân hệ [`src.vision`](file:///d:/AutoDoodle/src/vision) chứa toàn bộ các thuật toán xử lý ảnh, trích xuất biên, lượng tử hóa màu sắc (Color Quantization), đơn giản hóa đa giác và thuật toán tô màu kín vùng đặc.

---

## 1. Cấu Trúc Module

```text
src/vision/
├── __init__.py          # Package API: quantize_colors_kmeans, generate_sketch_contours, ...
├── color_matcher.py     # CIE-Lab RGB <-> Lab conversion & Delta-E Euclidean distance
├── edge_detector.py     # Canny, Bilateral Filter, Gaussian + Adaptive Thresholding
├── fill_engine.py       # Dense Zig-Zag Scanline filling & full painting layers generator
├── optimizer.py         # Greedy TSP Nearest-Neighbor stroke sequencing
├── pipeline.py          # High-level entry point generate_sketch_contours()
├── quantizer.py         # K-Means clustering, white region skipping & masking
└── simplifier.py        # Ramer-Douglas-Peucker (RDP) polygon approximation
```

---

## 2. Chi Tiết Các Thành Phần

### 2.1. Lượng Tử Hóa K-Means (`quantizer.py`)
Sử dụng thuật toán K-Means Clustering (`cv2.kmeans`) với khởi tạo thông minh `cv2.KMEANS_PP_CENTERS`:
- **Đầu vào**: Ảnh BGR thực tế và số lượng màu $K$ (mặc định $K=8 \sim 12$).
- **Đầu ra**: 
  - Ảnh đã lượng tử hóa màu (`quantized_image_bgr`).
  - Danh sách palette $K$ màu RGB.
  - Ma trận nhãn 2 chiều (`labels_2d`).
  - Danh sách tâm cụm màu (`centers_bgr`).
- **Lọc màu trắng**: Hàm `is_near_white(rgb, threshold=240)` bỏ qua các vùng màu trắng (vì nền canvas Instagram đã có sẵn màu trắng).

### 2.2. Trích Xuất Biên Đa Chế Độ (`edge_detector.py`)
Hỗ trợ 3 bộ lọc biên linh hoạt:
1. **Canny Tiêu Chuẩn (`canny`)**: Làm mờ Gaussian $\to$ Lọc Canny song ngưỡng kép (`canny_lower`, `canny_upper`). Thích hợp cho ảnh nét, tương phản cao.
2. **Lọc Biên Song Phương (`bilateral`)**: Sử dụng `cv2.bilateralFilter(gray, 9, 75, 75)` để làm mịn nhiễu bề mặt nhưng giữ nguyên cạnh sắc nét. Phù hợp cho ảnh chân dung/chụp thực tế.
3. **Ngưỡng Thích Nghi (`adaptive`)**: `cv2.adaptiveThreshold` kết hợp Canny để tách biên ảnh có ánh sáng không đồng đều hoặc chữ viết tay.

### 2.3. Đơn Giản Hóa Đa Giác RDP (`simplifier.py`)
Thuật toán **Ramer-Douglas-Peucker (RDP)** (`cv2.approxPolyDP`) giảm thiểu số điểm dư thừa trên đường cong với sai số tối đa $\epsilon$ (`epsilon_val`):
- Giảm $70\% - 90\%$ số điểm điều khiển chuột.
- Giữ vững hình dạng tổng thể và góc nhọn của nét vẽ.

### 2.4. Tối Ưu Hóa Hành Trình Nét Vẽ TSP (`optimizer.py`)
Giải bài toán Người bán hàng du lịch (Traveling Salesperson Problem) theo chiến thuật tham lam (**Greedy Nearest-Neighbor**):
- Tìm nét vẽ tiếp theo có đầu mút gần nhất với vị trí kết thúc của nét vẽ hiện tại.
- Tự động **đảo ngược chiều vẽ** (`stroke[::-1]`) nếu điểm cuối của nét tiếp theo gần hơn điểm đầu.
- Giúp giảm tới $60\%$ thời gian nhấc bút di chuyển chuột trên màn hình.

### 2.5. Tô Màu Vùng Kín Zig-Zag (`fill_engine.py`)
Tạo ra các nét vẽ đan khít nhau theo chiều ngang (Scanlines):
- **Khoảng cách bước** `step=2px`: Đảm bảo phủ kín màu $100\%$ không để lộ vệt trắng.
- **Cơ chế Zig-Zag**: Đảo chiều quét luân phiên (Trái $\to$ Phải rồi Phải $\to$ Trái) để đầu bút không phải quay ngược lại đầu dòng.
- **Đóng viền ngoài (`generate_edge_strokes_for_mask`)**: Vẽ thêm đường viền chu vi bao quanh vùng tô giúp mép màu sắc nét.
- **Thứ tự vẽ theo diện tích (`sort_layers_by_area`)**: Sắp xếp các lớp màu có diện tích lớn vẽ trước (lớp nền), chi tiết nhỏ vẽ sau (nét điểm xuyết).

### 2.6. Khoảng Cách Màu Chuẩn CIE-Lab (`color_matcher.py`)
Chuyển đổi hệ màu RGB sang không gian màu tri giác **CIE-Lab** qua `cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)`. Khoảng cách $\Delta E$ Euclidean giữa 2 vector $L^*a^*b^*$ phản ánh chính xác sự khác biệt màu sắc theo mắt người nhìn, vượt trội hơn so với khoảng cách RGB thông thường.
