# Tự chấm ngày 2026-09-29

## Toàn bộ test

Lệnh: `python -X utf8 -m pytest tests/ -v -p no:cacheprovider --tb=short`.

Kết quả: **84 passed, 5 skipped, 1 failed, 12 errors**.

Một failure và 12 setup errors đều thuộc `tests/test_bonus_cicd.py`: chưa triển khai workflow GitHub Actions và chưa có badge. Không sửa hoặc bỏ test để làm suite xanh. Các test bắt buộc được thực thi đều pass; Docker build và kiểm tra dung lượng đã chạy thật.

## Điểm phần bắt buộc

Lệnh: `python -X utf8 grade.py --no-bonus`.

| Nội dung | Kết quả | Điểm bộ chấm trả về |
|----------|---------|---------------------|
| CP1 | 13 passed | 15/15 |
| CP2 | 16 passed | 15/15 |
| CP3 | 22 passed | 20/20 |
| CP4 | 19 passed | 20/20 |
| CP5 | 8 passed, 5 skipped | 15/15 |
| Exercises | 10/10 câu, không còn placeholder | 15/15 |
| Tổng bắt buộc | Không tính bonus | **100/100** |

Đây là kết quả của `grade.py` nguyên bản: mẫu số là số pass cộng số fail, không gồm skip. Không coi các test skip là đã đạt: CP5 bỏ qua bốn test local fallback vì dùng Render và một test `/ask` có key vì chưa cấu hình `DEPLOY_API_KEY`. Test có xác thực trên cloud vẫn chưa được kiểm chứng. Nội dung exercises còn được giảng viên đánh giá thủ công; 100/100 ở đây không phải cam kết điểm chấm cuối cùng.

## Bằng chứng thực nghiệm

- Image `agent:single` dùng các lệnh starter: Docker hiển thị **1.73GB**.
- Image `agent:multi` dùng Dockerfile hiện tại: **309MB**.
- Thay comment trong `app/main.py` không làm chạy lại `pip install`; source được khôi phục sau kiểm tra cache.
- Log `/ask` thực tế từ test tích hợp được ghi trong câu 2.
- Ba agent chia sẻ history, dữ liệu còn sau restart; Redis dừng thì health 200, ready 503 (lần kiểm tra CP4).
- Render public URL và hai ảnh đã được lưu trong `DEPLOYMENT.md`.

`-X utf8` dùng cho Python trên Windows để đọc/ghi output Unicode ổn định, không đổi cách tính điểm. `Dockerfile.single` chỉ phục vụ so sánh, không dùng để deploy.
