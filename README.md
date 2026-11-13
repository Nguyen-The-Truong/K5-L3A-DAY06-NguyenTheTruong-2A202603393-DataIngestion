# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Bắt đầu nhanh

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |

[data/format-example.json](data/format-example.json) chỉ minh họa định dạng, không phải corpus đủ điều kiện. Phần xử lý và benchmark do bạn tự hiện thực; không bắt buộc xây chatbot.

---

## Bài làm (Nguyễn Thế Trường — Day 06)

**Corpus:** *Principles of Data Science* (OpenStax, CC BY-NC-SA 4.0), Chương 2 và 3, 74 trang nội dung (`data/manifest.json`). PDF **không** nằm trong repo.
**Stack:** `intfloat/multilingual-e5-small` (local, 384 chiều) + Chroma 1.5.9 (lưu tại `starter/chroma_db/`, cosine). Không cần Docker hay API key.
**Báo cáo:** [report/individual/2A2026033933_NguyenTheTruong.md](report/individual/2A2026033933_NguyenTheTruong.md) — các nhãn trong `results/audit/` do Claude đề xuất và được tác giả nhận làm nhãn của mình (nguy cơ thiên lệch được nêu trong báo cáo).

### Setup và chạy (từ thư mục gốc repo, Python 3.10+)

```bash
python -m pip install -r starter/requirements.txt          # có thể chậm vì kéo torch
mkdir -p data/raw
curl -L -o data/raw/principles-of-data-science.pdf \
  https://assets.openstax.org/oscms-prodcms/media/documents/Principles-of-Data-Science-WEB.pdf
python -X utf8 benchmark/build_questions.py                # ghi benchmark/questions.json (24 câu)
python -X utf8 benchmark/verify_evidence.py                # kiểm tra evidence nằm trên trang gold
cd starter
python -X utf8 -m src.run                                  # ingest A/B, chạy A/B/C, ghi ../results/
python -X utf8 -m src.audit                                # tạo bảng audit ../results/audit/
python -X utf8 scripts/check_reingest.py                   # kiểm tra nạp lại / xóa chunk cũ
```

Kết quả: `results/traces.jsonl` (top-3 từng câu), `results/run_summary.json` (cấu hình, phiên bản, thời gian, Hit@1/Hit@3), `results/audit/*.csv`, `artifacts/experiment_log.csv`. Cấu trúc code: `starter/src/{ingestion,corpus,chunking,embeddings,store,evaluation,run,audit}.py`.

**Demo (sau khi đã chạy `src.run`):** giao diện web `python -X utf8 scripts/demo_ui.py` rồi mở http://127.0.0.1:8000; hoặc dòng lệnh `python -X utf8 scripts/demo_query.py "What is stratified sampling?" --strategy C --section 2.2`. Bản review nhãn bằng tiếng Việt: `results/audit/REVIEW_VI.md`; tính lại số audit: `python -X utf8 scripts/summarize_audit.py`. Các file pgvector/Docker trong `starter/` không được dùng.
