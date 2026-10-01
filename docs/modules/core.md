# 📦 Phân Hệ `src.core` - Data Models & Constants

Phân hệ [`src.core`](file:///d:/AutoDoodle/src/core) định nghĩa các cấu trúc dữ liệu nền tảng, kiểu dữ liệu tĩnh (`TypedDict`, `Tuple`), hằng số hệ thống và bảng màu mặc định của Instagram DM.

---

## 1. Cấu Trúc File & Vai Trò

```text
src/core/
├── __init__.py       # Re-export các kiểu dữ liệu và hằng số dùng chung
├── constants.py      # Bảng màu chuẩn Instagram Story DM & Enum SpectrumPage
└── models.py         # Kiểu dữ liệu TypedDict: Point2D, ContourPoints, LayerInfo, ...
```

---

## 2. Chi Tiết Kiểu Dữ Liệu (`models.py`)

Các định nghĩa kiểu dữ liệu trong [`src/core/models.py`](file:///d:/AutoDoodle/src/core/models.py) đảm bảo tính an toàn kiểu (Type Safety) và hỗ trợ kiểm tra tĩnh qua Pyright:

```python
Point2D = Tuple[int, int]
ContourPoints = List[Point2D]
RGBColor = Tuple[int, int, int]

class PaletteItem(TypedDict):
    name: str
    rgb: RGBColor
    pct: float

class ColorGroup(TypedDict):
    name: str
    rgb: RGBColor
    pct: float
    contours: List[ContourPoints]

class LayerInfo(TypedDict):
    name: str
    rgb: RGBColor
    area: int
    contours: List[ContourPoints]

class ImageInfo(TypedDict):
    height: int
    width: int
    center_x: float
    center_y: float

class ProcessStats(TypedDict):
    total_contours: int
    color_groups_count: int
    original_points: int
    simplified_points: int
    reduction_percent: float
```

---

## 3. Bảng Màu Chuẩn Instagram DM (`constants.py`)

Instagram DM cung cấp thanh 9 ô màu cơ bản trên thanh công cụ vẽ:

| STT | Tên Màu | Mã HEX | Giá Trị RGB | Tọa Độ X Chuẩn Hóa (`pct`) |
|---|---|---|---|---|
| **1** | Đen (Black) | `#000000` | `RGB(0, 0, 0)` | `0.05` |
| **2** | Xanh dương (Blue) | `#0095F6` | `RGB(0, 149, 246)` | `0.16` |
| **3** | Xanh lá (Green) | `#09BB5F` | `RGB(9, 187, 95)` | `0.28` |
| **4** | Vàng (Yellow) | `#FFCC00` | `RGB(255, 204, 0)` | `0.39` |
| **5** | Cam (Orange) | `#FF9500` | `RGB(255, 149, 0)` | `0.50` |
| **6** | Đỏ san hô (Coral) | `#FF3B30` | `RGB(255, 59, 48)` | `0.61` |
| **7** | Hồng đậm (Magenta) | `#FF2D55` | `RGB(255, 45, 85)` | `0.72` |
| **8** | Tím (Purple) | `#AF52DE` | `RGB(175, 82, 222)` | `0.84` |
| **9** | Đỏ (Red) | `#FF0000` | `RGB(255, 0, 0)` | `0.95` |

### Enum Chế Độ Trang Dải Màu (`SpectrumPage`)
- `AUTO = 0`: Tự động phân tích toàn bộ palette của ảnh để chọn trang tối ưu.
- `PAGE1_RAINBOW = 1`: Trang 1 (Cầu vồng - 9 màu sặc sỡ).
- `PAGE2_WARM = 2`: Trang 2 (Tông ấm / Tone da / Hồng pastel).
- `PAGE3_GRAY = 3`: Trang 3 (Dải đơn sắc Xám / Đen / Trắng).
- `HYBRID = 4`: Chế độ lai - tự động vuốt chuyển trang ngang cho từng lớp màu.
