# Graph Algorithms Visualizer

Ứng dụng web trực quan hóa các thuật toán đồ thị, hỗ trợ tìm Cây khung nhỏ nhất (MST) và Đường đi ngắn nhất (Shortest Path).

## Tổng Quan Dự Án

- **Backend:** Xây dựng bằng **Flask** (Python) kết hợp với thư viện **NetworkX** để xử lý tính toán đồ thị.
- **Frontend:** Sử dụng **Vis.js** để vẽ và tương tác với đồ thị, cùng với HTML/CSS/JS cơ bản.
- **Tính năng chính:**
  - Tìm và tô màu Cây khung nhỏ nhất (MST) bằng thuật toán Kruskal/Prim.
  - Tìm Đường đi ngắn nhất giữa 2 đỉnh bằng thuật toán Dijkstra.
  - Hỗ trợ 3 cách nhập dữ liệu: 
    1. Nhập văn bản (Text Input).
    2. Vẽ trực tiếp trên giao diện (GUI Interactive).
    3. Đọc file chuẩn Matrix Market (`.mtx`).

## Cấu Trúc Thư Mục
``` 
.
├── static/ # Tài nguyên tĩnh (Frontend) 
│ ├── style.css
│ └── script.js
├── templates/ # Giao diện HTML 
│ └── index.html 
└── app.py # File chính khởi chạy Server Flask 
```

## Cài đặt và Chạy

1. Clone repository:
```bash
git clone https://github.com/DuySakura/GraphAlgorithmsVisualizer.git
```
2. Di chuyển vào thư mục dự án:
```bash
cd GraphAlgorithmsVisualizer
```
3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
4. Chạy server:
```bash
python -u app.py
```