# Auto-Doodle-Insta

Auto-Doodle-Insta (AutoDoodle Pro) is an optimized, high-performance Python application that automatically draws any image as a vector sketch or full-spectrum colored painting directly inside **Instagram DMs** (or any other canvas app running on an Android emulator like BlueStacks).

---

## 🏗️ Project Architecture (Cấu trúc dự án)

```text
Auto-Doodle-Insta/
├── assets/                          # Graphic & UI static resources
│   ├── icons/                       # App icons & bot template matching images
│   │   ├── icon.ico                 # App Window Icon
│   │   ├── draw_button.png          # Template for draw button detection
│   │   ├── plus_icon.png            # Template for '+' button detection
│   │   ├── thickness_slider_handle.png
│   │   └── thickness_slider_handle_alt.png
│   └── samples/                     # Test & sample images
│       └── Lily.png
│
├── docs/                            # Full technical documentation & module guides
│   ├── modules/                     # Detailed module docs (drawer, painter_engine, ...)
│   ├── architecture.md              # System architecture & coordinate systems
│   ├── configuration.md             # config.json reference & presets
│   └── index.md                     # Documentation index
│
├── src/                             # Core Python modules
│   ├── __init__.py
│   ├── drawer.py                    # Win32 Native Fast Mouse Engine & Color Swatch Navigator
│   ├── image_processor.py           # Canny Edge, RDP Simplification & TSP Path Optimizer
│   └── painter_engine.py            # Color Quantization, Slicing & Spectrum Mapping Engine
│
├── tests/                           # Unit tests, color analysis & lab experiment scripts
│   ├── __init__.py
│   ├── list_preview_colors.py
│   ├── test_mapping.py
│   ├── test_hybrid_mode.py
│   ├── test_layer_pages.py
│   └── ...
│
├── outputs/                         # Output renders, previews & test artifacts (git-ignored)
│   ├── preview_quantized.png
│   ├── sketch.png
│   └── sketch_*.png
│
├── main.py                          # GUI Application Entry Point (Tkinter / ttkbootstrap)
├── config.json                      # Bot & drawing configurations
├── requirements.txt                 # Dependencies
└── README.md                        # Documentation
```

> 📖 **Xem toàn bộ tài liệu kỹ thuật chuyên sâu tại**: [docs/index.md](file:///d:/AutoDoodle/docs/index.md)

---

## Key Features & Speed Improvements

- **⚡ Win32 Native Fast Drawing Engine (`src/drawer.py`)**: Uses Windows direct API calls (`mouse_event` / `SendInput`) to execute mouse strokes **10x–50x faster** than PyAutoGUI.
- **🎨 Full-Spectrum Multi-Layer Painting (`src/painter_engine.py`)**: K-Means clustering color quantization with automatic Instagram DM palette spectrum mapping.
- **📉 Ramer-Douglas-Peucker (RDP) Simplification**: Automatically simplifies dense edge points by 70%–90% while preserving sharp line detail (`epsilon` parameter).
- **🗺️ Greedy TSP Path Optimization**: Reorders contours by endpoint proximity to minimize pen-up mouse travel distance across the canvas.
- **🖼️ Live Sketch Preview & Controls**: Interactive UI with real-time vector preview canvas, Canny edge sliders, smoothness control, noise filtering, and a live progress bar.

---

## 1. Prerequisites & Setup

1. **Python 3.8+**: Make sure Python is installed and added to your system PATH.
2. **Android Emulator (e.g. BlueStacks)**: Instagram app running and logged in.
3. **Install Requirements**:
   ```sh
   pip install -r requirements.txt
   ```

---

## 2. Quick Start

Run the main application:
```sh
python main.py
```

### Step-by-Step Usage:
1. **Select Image**: Click **"Browse Image..."** to select any PNG/JPG file.
2. **Tune Sketch Settings**: Adjust sliders (**Canny High/Low**, **Smoothness**, **Min Length**) with **Live Sketch Preview** updating in real time.
3. **Calibrate Canvas**: Click **"1. Calibrate Canvas Area"**, then click the **top-left** and **bottom-right** corners of your emulator's drawing canvas.
4. **Start Drawing**: Click **"2. Start Drawing!"**. When prompted, select your color in Instagram DM and click your mouse anywhere to unleash the bot.

---

## 3. Hotkeys & Controls

- **PAUSE / RESUME**: Press **`SPACE`** to pause drawing (e.g., to change colors or pen thickness), then press **`SPACE`** again to resume.
- **EMERGENCY STOP**: Press **`Q`** at any time to immediately cancel drawing and release mouse buttons.