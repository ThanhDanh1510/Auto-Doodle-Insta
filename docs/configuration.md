# ⚙️ Hướng Dẫn Cấu Hình Chi Tiết (`config.json`)

Toàn bộ các tham số điều khiển, ngưỡng thuật toán thị giác và tọa độ hiệu chuẩn của AutoDoodle Pro được lưu trữ tập trung tại file [config.json](file:///d:/AutoDoodle/config.json).

---

## 1. Cấu Trúc File Cấu Hình Mẫu

```json
{
  "default_image_path": "assets/samples/Lily.png",
  "drawing_speed": 0.0,
  "stop_key": "q",
  "pause_key": "space",
  "ui_confidence": 0.8,
  "draw_button_y_offset": 75,
  "thickness_adjust_y_offset": 20,
  "scale_margin": 0.9,
  "plus_icons": [
    "assets/icons/plus_icon.png"
  ],
  "slider_handles": [
    "assets/icons/thickness_slider_handle.png",
    "assets/icons/thickness_slider_handle_alt.png"
  ],
  "fast_drawing_mode": true,
  "color_mode": "full_painting",
  "epsilon": 1.91,
  "min_contour_length": 4,
  "canny_lower": 54,
  "canny_upper": 120,
  "blur_kernel": 5,
  "edge_mode": "canny",
  "optimize_path": true,
  "point_delay": 0.006,
  "stroke_delay": 0.02,
  "step_size": 4.0,
  "color_bar_info": [
    840,
    964,
    333,
    66,
    1030,
    986
  ],
  "num_painting_colors": 11,
  "spectrum_page": 4
}
```

---

## 2. Bảng Giải Thích Toàn Bộ Tham Số (Parameter Reference)

### 2.1. Cấu Hình Đường Dẫn & Phần Cứng
| Khóa (Key) | Kiểu dữ liệu | Giá trị mặc định | Giải thích chi tiết |
| :--- | :--- | :--- | :--- |
| `default_image_path` | `string` | `"assets/samples/Lily.png"` | Đường dẫn tới bức ảnh mặc định được nạp khi khởi động ứng dụng. |
| `fast_drawing_mode` | `boolean` | `true` | Bật/tắt chế độ điều khiển chuột Win32 Native C-API (tốc độ $120\text{ FPS}$). |
| `stop_key` | `string` | `"q"` | Phím nóng khẩn cấp toàn cục để hủy tiến trình vẽ ngay lập tức. |
| `pause_key` | `string` | `"space"` | Phím nóng toàn cục để Tạm dừng / Tiếp tục vẽ. |
| `ui_confidence` | `float` | `0.8` | Ngưỡng tin cậy của thuật toán Template Matching khi tìm nút bấm UI. |
| `scale_margin` | `float` | `0.9` | Tỉ lệ lề an toàn để ảnh không bị vẽ sát mép viền canvas ($90\%$). |

---

### 2.2. Cấu Hình Thuật Toán Xử Lý Nét Vẽ (Edge & Simplification)
| Khóa (Key) | Kiểu dữ liệu | Khoảng khuyến nghị | Giải thích chi tiết |
| :--- | :--- | :--- | :--- |
| `color_mode` | `string` | `"full_painting"` | Chế độ vẽ: `"full_painting"` (Tranh sơn dầu đầy đủ màu), `"monochrome"` (Phác thảo đen trắng), `"spectrum"` (Phác thảo đa màu). |
| `num_painting_colors` | `integer` | `6 - 12` | Số lượng màu chủ đạo phân cụm bằng K-Means trong chế độ Full Painting. |
| `spectrum_page` | `integer` | `4` | Trang dải màu Instagram: `1` (Rainbow), `2` (Warm), `3` (Gray), `4` (Hybrid tự vuốt trang), `0` (Tự động nhận diện). |
| `epsilon` | `float` | `0.2 - 2.5` | Hệ số đơn giản hóa RDP. Càng lớn thì nét vẽ càng nhanh và ít điểm. |
| `min_contour_length` | `integer` | `2 - 6` | Số điểm tối thiểu để giữ lại một nét vẽ (lọc bỏ nhiễu hạt tấm). |
| `canny_lower` | `integer` | `20 - 80` | Ngưỡng dưới của bộ lọc viền Canny. |
| `canny_upper` | `integer` | `80 - 180` | Ngưỡng trên của bộ lọc viền Canny. |
| `blur_kernel` | `integer` | `3, 5, 7` | Kích thước ma trận làm mờ Gaussian (phải là số lẻ). |
| `edge_mode` | `string` | `"canny"` | Thuật toán trích viền: `"canny"`, `"bilateral"`, hoặc `"adaptive"`. |
| `optimize_path` | `boolean` | `true` | Bật/tắt giải thuật Greedy TSP tối ưu thứ tự nét vẽ. |

---

### 2.3. Cấu Hình Tốc Độ Di Chuột (Motion & Timing)
| Khóa (Key) | Kiểu dữ liệu | Giá trị chuẩn | Giải thích chi tiết |
| :--- | :--- | :--- | :--- |
| `step_size` | `float` | `2.0 - 4.0` | Bước nhảy pixel khi nội suy đường cong chuột ($2\text{px}$ cho độ mịn tối đa). |
| `point_delay` | `float` | `0.002 - 0.006` | Thời gian nghỉ (giây) giữa các điểm trên cùng một nét vẽ. |
| `stroke_delay` | `float` | `0.01 - 0.02` | Thời gian nghỉ (giây) giữa hai nét vẽ độc lập khi nhấc bút. |
| `color_bar_info` | `array` | `[x, y, w, h, ...]` | Mảng tọa độ hiệu chuẩn vùng dải màu Instagram Popover. |

---

## 3. Các Hồ Sơ Thiết Lập Sẵn (Recommended Presets)

### Profile 1: 🎨 Full Painting Masterpiece (Tái tạo tranh màu chi tiết)
Dành cho tranh vẽ chân dung, hoa lá, phong cảnh nhiều màu sắc:
```json
{
  "color_mode": "full_painting",
  "num_painting_colors": 11,
  "spectrum_page": 4,
  "point_delay": 0.006,
  "stroke_delay": 0.02,
  "step_size": 4.0
}
```

### Profile 2: 🎯 Ultra Detail Sketch (Phác thảo chì siêu nét)
Dành cho hình vẽ anime, manga, hoạt hình đường viền đậm:
```json
{
  "color_mode": "monochrome",
  "edge_mode": "canny",
  "canny_lower": 30,
  "canny_upper": 100,
  "epsilon": 0.3,
  "min_contour_length": 2,
  "optimize_path": true
}
```

### Profile 3: ⚡ Super Fast Line Art (Vẽ tốc độ cao trong 15-30 giây)
Dành cho biểu trưng, logo, hình vẽ phác nhanh:
```json
{
  "color_mode": "monochrome",
  "epsilon": 1.9,
  "min_contour_length": 5,
  "point_delay": 0.001,
  "stroke_delay": 0.005,
  "step_size": 5.0
}
```
