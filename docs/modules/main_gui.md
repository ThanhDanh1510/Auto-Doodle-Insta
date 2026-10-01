# 🖥️ Module `main.py` - Giao Diện Người Dùng & Trung Tâm Điều Phối

File [main.py](file:///d:/AutoDoodle/main.py) là entry point chính của ứng dụng AutoDoodle Pro, xây dựng trên nền tảng **Tkinter** kết hợp với **ttkbootstrap** mang lại giao diện Dark Mode hiện đại, mượt mà và trực quan.

---

## 1. Bố Cục Giao Diện (UI Layout Structure)

Cửa sổ ứng dụng sử dụng `ttk.Panedwindow(orient=HORIZONTAL)` chia làm hai khu vực làm việc chính:

```
+-----------------------------------------------------------------------------------+
| AutoDoodle Pro - Full Spectrum Painting Engine                        [_] [X]     |
+----------------------------------------+------------------------------------------+
| 👈 BẢNG ĐIỀU KHIỂN (LEFT PANEL)        | 👉 BẢNG XEM TRƯỚC & TRẠNG THÁI (RIGHT)   |
|                                        |                                          |
| 1. Image Selection                     | 🖼️ Live Masterpiece Reconstruction       |
|    [ Browse Image... ] [ Lily.png ]    |    Preview Canvas                        |
|                                        |    (Hiển thị ảnh phác thảo/màu thực tế)  |
| 2. Reconstruction Mode & Presets       |                                          |
|    [🎨 Full Painting] [🎯 Ultra Sketch]|                                          |
|    [🖊️ Outline]                        |                                          |
|                                        | 📊 Layers: 11 | Strokes: 2,450           |
| 3. Fine Controls & Color Quantization  |                                          |
|    - Drawing Engine Mode (Combobox)    | ---------------------------------------- |
|    - Instagram Spectrum Page (Combobox)| [======== Tiến độ vẽ (Progress Bar) ===] |
|    - Number of Colors (Slider 4-16)    | Status: Ready                            |
|    - Edge Sensitivity Low/High         |                                          |
|    - Line Simplification (Epsilon)     | ---------------------------------------- |
|    - Optimize Path Order (TSP Toggle)  | 📜 Console Output Log Stream             |
|                                        |    (Bắt log theo thời gian thực)         |
| 4. Calibration & Execution             |                                          |
|    [x] Win32 Native Hardware Input     |                                          |
|    [ 1. Calibrate Canvas ]             |                                          |
|    [ Calibrate Spectrum Bar ]          |                                          |
|    [ 2. Start Full Image Reconstruction]                                          |
|    Hotkeys: Pause = SPACE | Stop = Q   |                                          |
+----------------------------------------+------------------------------------------+
```

---

## 2. Các Cơ Chế & Kỹ Thuật Đặc Sắc

### 2.1. Cơ Chế Debounce Cập Nhật Live Preview (`_update_preview`)
Khi người dùng kéo các thanh trượt (Sliders), nếu mỗi chuyển động chuột đều gọi lại toàn bộ thuật toán OpenCV / K-Means thì giao diện sẽ bị đơ cục bộ. Hệ thống áp dụng kỹ thuật **Debouncing**:

```python
def on_setting_changed(self, *args):
    if self.preview_debounce_timer:
        self.root.after_cancel(self.preview_debounce_timer)
    self.preview_debounce_timer = self.root.after(300, self._update_preview)
```
- Khi người dùng đang kéo slider liên tục, timer sẽ bị hủy.
- Chỉ khi người dùng dừng tay $300\text{ms}$, pipeline `generate_sketch_contours` mới được kích hoạt, đảm bảo độ mượt mà tuyệt đối 60 FPS cho giao diện.

---

### 2.2. Trình Điều Hướng Luồng Log Bất Đồng Bộ (`QueueRedirector`)
Toàn bộ thông điệp in ra từ `print()` trong các module thuật toán hoặc tiến trình chạy nền được chuyển hướng luồng qua `queue.Queue`:

```python
class QueueRedirector:
    def __init__(self, q):
        self.queue = q
        self.ansi_escape = re.compile(r'\033\[[0-9;]*m')

    def write(self, text):
        cleaned = self.ansi_escape.sub('', text)
        if cleaned:
            self.queue.put(cleaned)
```
Giao diện Tkinter chạy một hàm thăm dò `_poll_console_queue()` mỗi $100\text{ms}$ để đẩy dòng text mới vào widget `ScrolledText`, loại bỏ mã ANSI color và ngăn chặn hoàn toàn hiện tượng xung đột đa luồng (UI Thread Crash).

---

### 2.3. Quy Trình Hiệu Chuẩn Bằng Chuột (Interactive Calibration)
1. **Hiệu chuẩn Canvas (`start_calibration`)**:
   - Sử dụng thư viện `mouse` để bắt 2 sự kiện click chuột trái liên tiếp.
   - Tính toán tự động kích thước $W, H$, tọa độ trung tâm $C_x, C_y$ và lưu vào bộ nhớ.
2. **Hiệu chuẩn Spectrum Bar (`start_color_bar_calibration`)**:
   - Hướng dẫn người dùng click vào các điểm mốc trên Instagram DM:
     - Điểm 1: Góc trên-trái popover gradient.
     - Điểm 2: Góc dưới-phải popover gradient.
     - Điểm 3: Tâm của hàng swatch tròn màu gốc.
   - Ghi tự động cấu hình vào [config.json](file:///d:/AutoDoodle/config.json).

---

### 2.4. Khớp Mẫu Tự Động (Template Matching Automation - `locate_robust`)
Hệ thống hỗ trợ tự động tìm kiếm các nút bấm trên màn hình thông qua OpenCV / PyAutoGUI template matching:
```python
def locate_robust(image_list):
    for image_file in image_list:
        if not os.path.exists(image_file):
            continue
        coords = pyautogui.locateCenterOnScreen(image_file, confidence=0.8)
        if coords:
            return coords
    return None
```
- Tìm icon nút vẽ `draw_button.png`.
- Tìm icon dấu cộng `plus_icon.png`.
- Tìm thanh trượt kích thước bút `thickness_slider_handle.png` để tự động điều chỉnh nét vẽ.
