# 🎨 Module `painter_engine.py` - Bộ Khởi Tạo Tranh Sơn Dầu / Full-Color Painting

Module [src/painter_engine.py](file:///d:/AutoDoodle/src/painter_engine.py) là trái tim của chế độ **"Full Painting Reconstruction"**, chịu trách nhiệm chuyển đổi bất kỳ bức ảnh màu thực tế (chân dung, phong cảnh, tĩnh vật) thành các lớp tô màu đặc và viền nét vector tối ưu, sẵn sàng để vẽ tự động trên Instagram canvas.

---

## 1. Quy Trình Xử Lý Đa Lớp (Full Painting Pipeline)

```mermaid
flowchart TD
    A[🖼️ Ảnh gốc BGR] --> B[Bilateral Filter Làm mịn ảnh 9x50x50]
    B --> C[K-Means Clustering: Phân cụm num_colors]
    C --> D[Tạo Bảng màu Palette RGB & Ma trận Nhãn 2D]
    
    subgraph LoopLayers["Vòng lặp từng lớp màu k = 0 .. num_colors-1"]
        D --> E{Kiểm tra is_near_white?}
        E -->|Đúng (Gần Trắng)| Skip[Bỏ qua lớp - Canvas đã có nền trắng]
        E -->|Sai| F[Tạo Binary Mask cho màu k]
        F --> G[Lọc Connected Components < min_region_area]
        G --> H[Morphological Close: Đóng khe hở nhỏ 3x3]
        H --> I[Quét nét Dense Fill Zig-Zag step=2px]
        H --> J[Trích xuất đường viền bao quanh Edge Strokes]
        I --> K[Gộp nét Fill + Edge thành Contours lớp]
        J --> K
    end
    
    K --> L[Sắp xếp các lớp theo Diện tích Giảm dần]
    L --> M[📦 Trả về layers, img_info, preview_canvas]
```

---

## 2. Chi Tiết Các Hàm Cốt Lõi (Core Functions)

### 2.1. `quantize_colors_kmeans(image_bgr, num_colors=12)`
Lượng tử hóa màu sắc của bức ảnh thành $N$ màu chủ đạo bằng thuật toán phân cụm K-Means.

- **Đầu vào**:
  - `image_bgr`: Mảng NumPy ảnh không gian BGR `(H, W, 3)`.
  - `num_colors`: Số lượng cụm màu mục tiêu (mặc định $8 \dots 12$).
- **Nguyên lý hoạt động**:
  1. Trải phẳng mảng 3 chiều thành ma trận $M \times 3$ kiểu `float32`.
  2. Áp dụng tiêu chuẩn dừng `cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER` (30 vòng lặp hoặc độ hội tụ $\epsilon \le 0.5$).
  3. Khởi tạo tâm cụm thông minh `cv2.KMEANS_PP_CENTERS`.
  4. Trích xuất danh sách màu tâm cụm dạng RGB và ma trận nhãn 2 chiều `labels_2d`.
- **Đầu ra**: `(quantized_image_bgr, palette_rgb_list, labels_2d, centers_bgr)`.

---

### 2.2. `is_near_white(rgb, threshold=240)`
Kiểm tra xem một màu có thuộc dải trắng / gần trắng hay không.

```python
def is_near_white(rgb, threshold=240):
    r, g, b = rgb
    return r >= threshold and g >= threshold and b >= threshold
```
- **Ý nghĩa thực tế**: Trên Instagram DM Canvas, phông nền mặc định đã là màu trắng tinh khiết. Việc bỏ qua các mảng trắng giúp:
  - Giảm $30\% - 50\%$ tổng số nét vẽ và thời gian chạy.
  - Tránh hiện tượng đầu bút đè lên nhau gây xơ nét.

---

### 2.3. `generate_fill_strokes_for_mask(mask, step=2)`
Tạo các nét tô ngang siêu mịn (Dense Scanline Fill) lấp đầy các vùng kín của mask.

- **Thuật toán quét dòng & đảo chiều Zig-zag**:
  1. Áp dụng toán tử hình thái học `cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_3x3)` để hàn gắn các vi điểm hở.
  2. Quét ma trận theo từng bước `step` (mặc định $2\text{px}$).
  3. Sử dụng đạo hàm rời rạc `np.diff` để xác định tọa độ bắt đầu `starts` và kết thúc `ends` của từng chuỗi pixel liên tục trên mỗi dòng.
  4. Đổi chiều luân phiên giữa các dòng (`direction = 1` từ trái sang phải, `direction = -1` từ phải sang trái) để tối thiểu hóa quãng đường nhấc bút.
- **Đầu ra**: Danh sách các nét vẽ `[[ (x1, y), (x2, y), ... ], ...]`.

---

### 2.4. `generate_edge_strokes_for_mask(mask, epsilon=1.2)`
Trích xuất đường viền bao quanh của mảng màu để đảm bảo ranh giới giữa các mảng màu luôn sắc nét, không bị răng cưa.

- **Nguyên lý**:
  1. Tìm đường bao ngoài bằng `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`.
  2. Đơn giản hóa đa giác bằng `cv2.approxPolyDP(cnt, epsilon=1.2, True)`.
  3. Đóng kín đường nét bằng cách nối điểm cuối về lại điểm đầu `pts.append(pts[0])`.

---

### 2.5. `sort_layers_by_area(layers)`
Sắp xếp thứ tự vẽ các lớp màu theo nguyên tắc hội họa chuyên nghiệp:

$$\text{Diện tích lớp } L_1 \ge \text{Diện tích lớp } L_2 \ge \dots \ge \text{Diện tích lớp } L_n$$

> [!IMPORTANT]
> **Quy tắc nền tảng**: Các mảng màu nền rộng lớn (Background, bầu trời, mảng da lớn) được vẽ trước để tạo phông nền. Sau đó, các mảng chi tiết nhỏ (mắt, nhụy hoa, viền đổ bóng đậm) sẽ được vẽ đè lên trên, tạo chiều sâu thị giác hoàn hảo cho tác phẩm.

---

### 2.6. `generate_full_painting_layers(image_path, num_colors=12, fill_step=2, min_region_area=20)`
Hàm điều phối toàn bộ pipeline, kết hợp K-Means, lọc nhiễu diện tích nhỏ `cv2.connectedComponentsWithStats`, quét nét fill và viền.

- **Trả về**:
  - `layers`: Danh sách dictionary `[ {"name": ..., "rgb": (r, g, b), "area": int, "contours": [...]}, ... ]`.
  - `img_info`: Thông tin kích thước và tâm ảnh `{"height", "width", "center_x", "center_y"}`.
  - `preview_canvas`: Ảnh BGR lượng tử hóa làm hình mẫu trực quan trên GUI.
