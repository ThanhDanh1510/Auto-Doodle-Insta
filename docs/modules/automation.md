# ⚡ Phân Hệ `src.automation` - Hardware Automation & Stroke Execution

Phân hệ [`src.automation`](file:///d:/AutoDoodle/src/automation) chịu trách nhiệm tương tác trực tiếp với hệ điều hành Windows, điều khiển chuột siêu tốc qua Win32 Native API, tính toán tọa độ dải màu Instagram Popover và thực thi quy trình vẽ tự động.

---

## 1. Cấu Trúc Module

```text
src/automation/
├── __init__.py              # Package API: FastDrawer, win32_move, win32_press, ...
├── input_driver.py          # Direct Win32 user32.mouse_event & PyAutoGUI fallback
├── spectrum_navigator.py    # 3-Page Instagram Spectrum Swatch & Popover Hue-to-XY Mapping
└── stroke_executor.py       # FastDrawer canvas execution, page swiping & event loop
```

---

## 2. Chi Tiết Các Thành Phần

### 2.1. Trình Điều Khiển Chuột Win32 Native (`input_driver.py`)
- Trên Windows, thay vì gọi `pyautogui` (bị độ trễ lớn và overhead của Python), AutoDoodle Pro gọi trực tiếp API `user32.dll` thông qua `ctypes`:
  - `user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)`
  - `user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)`
  - `user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)`
- Tọa độ được chuẩn hóa sang thang đo $0 .. 65535$:
  $$nx = \operatorname{int}\left(x \times \frac{65535}{\text{SCREEN\_WIDTH}}\right)$$
  $$ny = \operatorname{int}\left(y \times \frac{65535}{\text{SCREEN\_HEIGHT}}\right)$$
- Tốc độ thực thi đạt **120+ FPS**, không bị giật lag hay mất nét khi vẽ nhanh.

### 2.2. Điều Hướng Dải Màu Instagram Spectrum (`spectrum_navigator.py`)
Thực hiện ánh xạ màu RGB bất kỳ sang tọa độ tương đối $(X_{\%}, Y_{\%})$ trên thanh Popover gradient của Instagram DM:

#### Trang 1 (Rainbow Spectrum - Cầu vồng)
- 9 Swatches với khoảng cách $0.125$:
  - $x=0.000$: Đen / Nâu thẫm
  - $x=0.125$: Xanh dương
  - $x=0.250$: Xanh lá
  - $x=0.375$: Vàng
  - $x=0.500$: Cam
  - $x=0.625$: Đỏ san hô
  - $x=0.750$: Hồng đậm
  - $x=0.875$: Tím
  - $x=1.000$: Đỏ tươi

#### Trang 2 (Warm Spectrum - Tông ấm / Da)
- Tối ưu cho màu cánh hoa pastel, tone da, nude, hồng phấn dịu:
  - $x=0.000$: Hồng đất (Dusty Rose)
  - $x=0.125$: Hồng phấn (Pale Pink)
  - $x=0.250$: Beige nhạt (Cream Beige)
  - $x=0.375$: Cam đào (Peach)
  - $x=0.500$: Nâu sáng / Vàng đất (Ochre)
  - $x=0.625$: Nâu đất (Dark Brown)
  - $x=0.750$: Đen xám (Off-black)
  - $x=0.875$: Xám thẫm
  - $x=1.000$: Xám vừa

#### Trang 3 (Gray Spectrum - Đơn sắc)
- Ánh xạ độ sáng Luma sang trục X ($X = 1.0 - \text{Luma}$).

#### Phân loại chế độ Hybrid (`choose_best_page_for_color`)
- Màu cánh hoa mờ dịu ($S \le 0.65, V \ge 0.40$) $\to$ Trang 2 Warm.
- Màu nhấn đậm sắc, đốm hạt thẫm ($S > 0.65$ hoặc $V < 0.40$) $\to$ Trang 1 Rainbow.
- Màu đơn sắc trung tính ($S < 0.08$) $\to$ Trang 3 Gray.

### 2.3. Động Cơ Thực Thi `FastDrawer` (`stroke_executor.py`)
Lớp `FastDrawer` quản lý toàn bộ vòng đời vẽ tranh:
- **Hotkeys kiểm soát**: Lắng nghe `SPACE` (Tạm dừng/Tiếp tục) và `Q` (Dừng khẩn cấp).
- **Quy trình chọn màu Instagram**:
  1. Di chuyển chuột tới nút tròn swatch trên thanh màu (`swatch_y`).
  2. Nhấn giữ chuột trái **1.2 giây** để kích hoạt popover gradient bung lên.
  3. Kéo chuột mượt mà hướng lên trên vào vùng tọa độ $Y$ mục tiêu (`popover_y`).
  4. Giữ **0.5 giây** để Instagram khóa màu.
  5. Nhả chuột và bắt đầu vẽ lớp màu đó.
- **Vuốt chuyển trang (`swipe_spectrum_page`)**: Tự động thực hiện thao tác kéo ngang trên thanh swatch để lật trang màu (Page 1 $\leftrightarrow$ Page 2 $\leftrightarrow$ Page 3).
- **Vẽ nét nội suy (`smooth_drag_to`)**: Nội suy từng bước nhỏ `step_size=2.0px` với độ trễ `point_delay=0.002s` đảm bảo nét vẽ mượt mà, không bị gãy góc.
