# Báo Cáo Lab MLOps — CI/CD cho AI Systems

**Họ tên:** Đoàn Minh Hiếu
**Buổi:** Day 21 — Track 2: CI/CD for AI Systems
**Repo:** https://github.com/doanminhhieu14052005-sketch/Day21_Track2_2A202600841_DoanMinhHieu

---

## 1. Bộ siêu tham số đã chọn và lý do

Mô hình: `RandomForestClassifier` phân loại chất lượng rượu vang (3 lớp) trên 12 đặc trưng hóa học.

Ở Bước 1, em chạy nhiều thí nghiệm trên MLflow với tập `train_phase1.csv` (2998 mẫu) và so sánh `accuracy` trên tập `eval.csv` (500 mẫu, held-out). Kết quả cho thấy chỉ với phase1, mô hình chạm trần ở khoảng **0.68** — không vượt được ngưỡng chất lượng 0.70 dù tinh chỉnh siêu tham số.

Sau khi bổ sung dữ liệu phase2 (Bước 3, tổng 5996 mẫu) và tinh chỉnh lại, bộ siêu tham số tốt nhất được chọn:

| Siêu tham số | Giá trị | Lý do |
|---|---|---|
| `n_estimators` | 300 | Nhiều cây hơn giúp giảm phương sai, ổn định kết quả; vượt 300 không cải thiện thêm. |
| `max_depth` | 25 | Đủ sâu để học quan hệ phi tuyến nhưng vẫn hạn chế overfit so với để `None`. |
| `max_features` | `sqrt` | Tăng đa dạng giữa các cây (mỗi nút xét √(số đặc trưng)), cho accuracy cao nhất trong grid search. |
| `min_samples_split` | 2 | Giá trị mặc định, cho kết quả tốt nhất. |

**Kết quả cuối cùng:** `accuracy = 0.758`, `f1_score = 0.757` trên tập đánh giá — vượt ngưỡng 0.70.

**Bài học chính:** với tập dữ liệu này, *thêm dữ liệu huấn luyện* (2998 → 5996 mẫu) là đòn bẩy hiệu quả hơn hẳn việc chỉ tinh chỉnh siêu tham số — đúng tinh thần của vòng lặp huấn luyện liên tục trong MLOps.

---

## 2. So sánh accuracy giữa Bước 2 và Bước 3

| Chỉ số | Bước 2 (2998 mẫu) | Bước 3 (5996 mẫu) |
|---|---|---|
| accuracy | 0.678 | 0.758 |
| f1_score | 0.676 | 0.757 |

Ở Bước 2, accuracy 0.678 < 0.70 nên **eval gate tự động chặn deploy** (đúng hành vi mong muốn). Ở Bước 3, sau khi bổ sung dữ liệu, accuracy vượt ngưỡng nên pipeline tự động triển khai mô hình mới lên VM — không cần thao tác thủ công.

---

## 3. Khó khăn gặp phải và cách giải quyết

**Khó khăn lớn nhất — GitHub Actions luôn lỗi `dvc pull` ở job Train.**

- *Triệu chứng:* job Train báo lỗi `403 Forbidden` khi kéo dữ liệu từ GCS. Ban đầu tưởng là lỗi xác thực service account nên đã thử nhiều cách (đổi cách ghi key, dùng `google-github-actions/auth`, set `credentialpath`, set `projectname`...) nhưng đều không khỏi.
- *Nguyên nhân thật:* chẩn đoán bằng cách tải trực tiếp object từ bucket bằng chính service account đó — phát hiện service account **xác thực và liệt kê object thành công**, nhưng khi đọc nội dung thì Google trả về nguyên văn: *"The billing account for the owning project is disabled."* Tức **project GCP cũ (`triagehealth`) đã bị tắt billing**, khiến mọi thao tác đọc dữ liệu bị chặn. Đây không phải lỗi code/auth.
- *Cách giải quyết:* chuyển toàn bộ hạ tầng sang một project GCP mới có billing hoạt động (`calm-streamer-499804-e6`): tạo bucket mới, service account mới với quyền `storage.objectAdmin`, đẩy lại dữ liệu, cập nhật `.dvc/config` và các GitHub Secrets. Sau đó pipeline `dvc pull` chạy thành công.

**Khó khăn phụ:**
- Biến môi trường trong file systemd service bị đặt sai tên (`CLOUD_BUCKET` thay vì `GCS_BUCKET` mà `serve.py` đọc) → đã sửa lại cho khớp.
- Dòng `dvc remote modify projectname <project cũ>` trong workflow vô tình ép billing về lại project đã chết lúc chạy CI → đã gỡ bỏ.

---

## 4. Kết quả đạt được

- Cả 4 job GitHub Actions (Unit Test, Train, Eval, Deploy) hoàn thành thành công (xanh).
- Eval gate hoạt động đúng: chặn deploy khi accuracy < 0.70, cho phép deploy khi đạt.
- API serving trên Cloud VM trả kết quả đúng:
  - `GET /health` → `{"status": "ok"}`
  - `POST /predict` → `{"prediction": 0, "label": "thấp"}`
- Bổ sung dữ liệu mới chỉ bằng một lần `git push` (commit file `.dvc`) đã kích hoạt toàn bộ pipeline huấn luyện lại và triển khai lại hoàn toàn tự động.
