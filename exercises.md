# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Các câu trả lời dưới đây dựa trên các lần chạy và kiểm tra trong workspace.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Ngô Đình Minh Nhật — Mã học viên: 2A202602569

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu quên nhập `AGENT_API_KEY` khi tạo service Render, app phải dừng trước khi nhận traffic. Nếu dùng khóa mặc định `changeme`, người biết mã nguồn có thể dùng khóa đó để gọi API. Trong kiểm tra CP1, bỏ biến secret và bỏ việc đọc `.env` làm `Settings` báo `ValidationError`; kiểm tra lifespan cũng dừng ngay ở bước đọc cấu hình. Nhờ vậy lỗi cấu hình được phát hiện lúc deploy, thay vì sau khi service đã công khai.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng log thật thu được khi test tích hợp gọi `/ask` hai lần với cùng user (store dùng Redis giả của fixture, không phải log cloud):

```json
{"user_id": "sv-test", "tokens_in": 3, "tokens_out": 37, "cost_usd": 2.265e-05, "event": "ask_completed", "level": "info", "timestamp": "2026-09-29T04:05:05.686463+00:00"}
```

Thứ nhất, có thể lọc theo `event`, `user_id` và khoảng thời gian để đếm các lượt hoàn thành của một user. Thứ hai, có thể cộng `cost_usd`, `tokens_in` và `tokens_out` để theo dõi mức sử dụng. Chuỗi “đã trả lời xong” không chứa các dữ liệu đó. JSON được in trên một dòng, timestamp có múi giờ UTC; `ensure_ascii=False` giữ nội dung tiếng Việt dễ đọc.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f Dockerfile.single -t agent:single .
docker build -t agent:multi .
docker images agent --format "{{.Repository}}:{{.Tag}} {{.Size}}"
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.73 GB (xấp xỉ 1730 MB theo đơn vị thập phân) |
| Multi-stage | 309 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Đo bằng Docker trên máy làm bài ngày 2026-09-29. `Dockerfile.single` khôi phục các lệnh của starter ở commit `a790628`, dùng `python:3.11`; Dockerfile hiện tại dùng hai stage trên `python:3.11-slim`. Cả hai dùng cùng source, requirements và `.dockerignore` hiện tại để không đưa secret vào image so sánh.

Phần chênh lệch chủ yếu đến từ base image đầy đủ chứa nhiều công cụ và thư viện hệ điều hành hơn bản slim. Bản đầu còn giữ pip cache và copy cả build context được phép; runtime mới chỉ nhận virtualenv, `app/` và `utils/`, cài dependency với `--no-cache-dir`. Không thể quy toàn bộ mức giảm cho multi-stage: đổi base image cũng đóng góp lớn, và bài này không cài compiler riêng ở builder.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Đã thêm tạm một comment trong `app/main.py`, build tag `agent:cache-check`, rồi khôi phục nguyên file. Output ghi `CACHED` ở các bước tạo virtualenv, copy requirements, `pip install`, tạo user và copy virtualenv sang runtime. `COPY app/`, `COPY utils/` phía sau và bước xuất image chạy lại. Nếu `COPY . .` đứng trước `RUN pip install`, một thay đổi source làm layer copy đổi, khiến bước cài dependency phía sau mất cache dù requirements không đổi.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Nếu lỗi Python cho phép thực thi lệnh tùy ý, kẻ tấn công có quyền của process ứng dụng. Với root trong container, họ có nhiều khả năng sửa file hệ thống hoặc khai thác cấu hình nguy hiểm như mount Docker socket, volume host nhạy cảm, hay lỗi kernel để tiến tới quyền trên host. Root trong container không tự động đồng nghĩa root trên host; vẫn cần đường khai thác hoặc cấu hình sai đó. `USER agent` làm process chạy UID 10001, đã xác minh bằng `os.getuid()` trong container, nên giảm quyền ngay khi app bị chiếm. Cách này không thay thế việc tránh privileged mode và mount nguy hiểm.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Với bộ đếm theo phút đồng hồ, user có thể gửi 10 request ở giây 59 của phút trước và 10 request ở giây 00 của phút sau: tổng 20 request trong khoảng 2 giây. Sliding window luôn xét 60 giây gần nhất nên 10 request đầu vẫn được tính. Trong test bổ sung, hai request cùng timestamp vẫn được lưu thành hai member nhờ UUID; request tiếp theo bị 429 và có `Retry-After: 60`. Đến mốc 60 giây, các entry cũ được loại khỏi cửa sổ. UUID tránh ghi đè member, nhưng tự nó không làm chuỗi kiểm tra rồi thêm trở thành một thao tác nguyên tử khi nhiều request chạy đồng thời.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Rate limit đo số lượt gọi trong 60 giây, còn cost guard đo tiền đã dùng theo user và tháng UTC. Ví dụ mới gọi một lượt trong phút nhưng đã tiêu 9.99 USD và dự kiến tốn thêm 0.02 USD thì rate limit cho qua, cost guard với budget 10 USD phải trả 402. Ngược lại, user còn nhiều tiền nhưng đã gọi đủ 10 lượt trong 60 giây thì lần thứ 11 bị 429. Trong test HTTP, tài khoản có chi phí 999 USD bị 402 và mock LLM không được gọi. Hiện `/ask` gọi `guard.check(user_id)` với ước tính mặc định 0, rồi ghi chi phí thật sau LLM; vì vậy không bảo đảm request kế tiếp hoặc các request đồng thời tuyệt đối không vượt budget.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Nếu dùng chung một endpoint kiểm tra Redis: Redis mất kết nối → probe của cả ba container thất bại → load balancer có thể loại cả ba khỏi danh sách → nếu liveness đạt ngưỡng lỗi, orchestrator có thể restart cả ba dù process vẫn chạy tốt. Restart app không sửa được Redis, nên có thể tạo vòng lặp restart. Có xảy ra trong đúng 30 giây hay không còn phụ thuộc interval và ngưỡng probe; Docker HEALTHCHECK một mình cũng không tự restart container. Khi dừng Redis trong stack thử nghiệm, kết quả thực tế là `/health` vẫn 200, `/ready` là 503 với `redis: false`, đúng với việc tách hai mục đích.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Đã chạy ba agent với `docker-compose.scale.yml` để tránh ba container cùng chiếm host port 8000. Các request tuần tự cùng user `cp4-scale-check` gửi lần lượt tới ba agent có `history_length` là 0, 2, 4. Sau khi restart agent thứ nhất, Redis vẫn chứa 6 message; TTL kiểm tra được xấp xỉ 7 ngày. Mỗi lượt hỏi thêm hai message, còn response báo độ dài lịch sử trước lượt đó. Nếu dùng dict Python riêng cho từng process, ba request đầu tới ba agent có thể đều báo 0; các lần sau có thể thấy 2, 0, 4 tùy instance, và restart sẽ mất lịch sử của instance đó. Với Redis, chỉ giữ 20 message mới nhất nên độ dài không tăng vô hạn.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Khi thử Railway CLI, `railway init` báo `Failed to fetch` tới `https://backboard.railway.com/graphql/v2`, kèm `tcp connect error` và `os error 10060`. Sau đó `railway add --database redis` và `railway up` báo chưa có project được link. Thông báo cho thấy kết nối API bị timeout trước khi khởi tạo/liên kết project hoàn tất; chưa có căn cứ kết luận lỗi do Dockerfile hay xác định chính xác firewall nào chặn. Cách xử lý thực tế là chuyển sang Render, deploy Blueprint từ GitHub và cấu hình secret trên dashboard. Service `https://day12-agent-5us0.onrender.com` đã Live; gọi thật cho kết quả `/health` 200, `/ready` 200 với Redis true, và `/ask` không key trả 401. Hai ảnh minh chứng nằm trong `screenshots/`.
