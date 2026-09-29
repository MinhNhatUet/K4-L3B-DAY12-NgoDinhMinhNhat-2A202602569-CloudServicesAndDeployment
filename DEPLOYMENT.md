# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Ngô Đình Minh Nhật |
| Mã học viên | 2A202602569 |
| Repo | https://github.com/MinhNhatUet/K4-L3B-DAY12-NgoDinhMinhNhat-2A202602569--CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | Chưa có — chưa triển khai cloud |
| Platform | Render — Blueprint đã chuẩn bị, chờ tài khoản để triển khai |
| Ngày deploy | Chưa triển khai |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | Chưa xác minh | platform tự gán, không khai báo trong Blueprint |
| `AGENT_API_KEY` | Chưa xác minh | Blueprint yêu cầu nhập trong dashboard, không nằm trong repo |
| `REDIS_URL` | Chưa xác minh | Blueprint tham chiếu connectionString của Render Key Value |
| `RATE_LIMIT_PER_MINUTE` | Chưa xác minh | Blueprint cấu hình 10 |
| `MONTHLY_BUDGET_USD` | Chưa xác minh | Blueprint cấu hình 10.0 |
| `LOG_LEVEL` | Chưa xác minh | Blueprint cấu hình INFO |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i <URL>/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i <URL>/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST <URL>/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST <URL>/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST <URL>/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:

```
Chưa có output cloud. Chỉ bổ sung sau khi deploy và gọi URL thật.
```

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/health.png` — kết quả gọi `/health` từ trình duyệt hoặc curl

---

## Nếu Dùng Phương Án Dự Phòng

Không đăng ký được tài khoản cloud? Vẫn nộp được bài, nhưng CP5 tối đa 60% điểm:

1. Đặt `LOCAL_FALLBACK=true` trong `.env`
2. Chạy `docker compose up -d` rồi kiểm tra `docker compose ps`
3. Chụp màn hình vào `screenshots/`
4. Chạy `pytest tests/test_cp5.py -v` — bộ test sẽ tự chuyển sang kiểm tra
   `http://localhost:8000`
5. Ghi rõ lý do không deploy được vào phần dưới đây:

```
Chưa kích hoạt fallback. Đang chờ lựa chọn của học viên; môi trường hiện
chưa có CLI/token Render hoặc Railway. Chưa có ảnh dashboard và health.
```
