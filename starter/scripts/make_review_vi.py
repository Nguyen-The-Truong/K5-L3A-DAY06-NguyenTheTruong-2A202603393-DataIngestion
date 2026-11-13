"""Builds results/audit/REVIEW_VI.md: a Vietnamese review sheet for the audit labels.

Start/end snippets come from the real chunks in coherence_samples.csv; the Vietnamese gist and
reasons are hand-written from reading each chunk. Scores shown are the CSV scores.
"""
import csv
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2] / "results" / "audit"

GIST = {  # row index -> (tóm tắt nội dung, lý do cho điểm)
    0: ("Nói về thu thập dữ liệu cần phương pháp có hệ thống để đảm bảo chất lượng; nguồn gồm CSDL nội bộ, kho bên ngoài, website...", "Bắt đầu giữa cụm từ, kết thúc giữa từ nhưng vẫn đọc hiểu được."),
    1: ("Cùng đoạn trên nhưng lấy trọn cả đoạn văn.", "Trọn một đoạn, bắt đầu và kết thúc ở đầu/cuối câu."),
    2: ("Cuối ví dụ cluster sampling (bắt đầu giữa từ 'presentative') và định nghĩa lấy mẫu thuận tiện, cụt ở 'exploratory'.", "Bắt đầu giữa từ, kết thúc cụt, nhưng phần định nghĩa vẫn hiểu."),
    3: ("Trọn ví dụ cluster sampling và định nghĩa đầy đủ của lấy mẫu thuận tiện.", "Hai ý đều trọn vẹn."),
    4: ("Giữa danh sách thư viện Python xử lý văn bản: cuối mục tokenization, TextBlob, SpaCy; cụt giữa câu.", "Đầu giữa từ, cuối giữa câu."),
    5: ("Bắt đầu 'This library...' (không nói tên thư viện), rồi SpaCy, câu tổng kết 'Overall', và mở sang chủ đề mới Regular Expressions.", "Thiếu tên thư viện ở đầu; lẫn hai chủ đề."),
    6: ("Mảnh chú thích hình + lời giải: phát hiện outlier tháng 3/1990, số nhảy từ ~5.400 lên 9.50(0) thì bị cụt.", "Đầu giữa chú thích hình, cuối cụt giữa số."),
    7: ("Đề bài Example 2.6 trọn vẹn, chú thích hình, mở đầu lời giải, cụt ở 'March 28,'.", "Đề bài đủ nhưng phần lời giải (câu trả lời) bị cụt do hết trang."),
    8: ("Danh sách mã one-hot, kế đó là các ô bảng bị xáo trộn ('Removing special Simplifying the...'); cắt giữa từ cả hai đầu.", "Cắt cả hai đầu và bảng lộn xộn nên khó hiểu."),
    9: ("Khái niệm one-hot đầy đủ, nhưng kèm các ô bảng bị xáo trộn.", "Khái niệm trọn, phần bảng lộn xộn."),
    10: ("Đầu chương 3: thống kê dùng trong y khoa, kỹ thuật...; cụt ở 'signi'.", "Đầu giữa câu, cuối giữa từ."),
    11: ("Các đoạn trọn về vai trò của thống kê với người tiêu dùng (ví dụ mua nhà); chỉ cụt vế cuối do hết trang.", "Đoạn trọn, chỉ cụt phần rất cuối."),
    12: ("Lời bình về kết quả DataFrame.describe(): cột 'Unnamed: 0' chỉ là mã định danh; kết thúc bằng chú thích hình.", "Bắt đầu giữa câu; chưa rõ đang nói dataset nào."),
    13: ("Bắt đầu giữa câu 'summarize data. Recall that describe()...', có chú thích hình, kết bằng tiêu đề lửng 'EXPLORING FURTHER'.", "Đầu giữa câu, cuối là tiêu đề lửng."),
    14: ("Bắt đầu giữa từ; câu 'dùng 1.5 làm ngưỡng' và tiêu đề EXAMPLE 3.12; công thức bị mất khi trích PDF.", "Đầu giữa từ; công thức thiếu."),
    15: ("Đoạn trọn về phát hiện outlier bằng IQR, câu 'ngưỡng 1.5', và trọn đề bài + dữ liệu Example 3.12 (công thức mất do trích PDF).", "Trọn ý; thiếu công thức là lỗi của việc trích PDF, không phải của cách chia chunk."),
    16: ("Xác suất có điều kiện (sinh viên tốt nghiệp ngành điều dưỡng); cắt giữa từ cả hai đầu, công thức mất.", "Cắt cả hai đầu; thiếu công thức."),
    17: ("Bắt đầu 'We can now use this equation...' (công thức nằm ở chunk trước, không có ở đây), rồi tính xác suất.", "Thiếu công thức/ngữ cảnh ở chunk trước."),
    18: ("Bắt đầu rõ 'In Example 3.24...', kết quả xác suất nhị thức 18/20 = 0.271; cụt ở 'shows th'.", "Câu đầu rõ nhưng cuối cụt."),
    19: ("Ghi chú về giai thừa (ký hiệu bị mất), đề Example 3.25, lời giải thiếu công thức.", "Ký hiệu và công thức mất nhưng vẫn đoán được ý."),
}

GROUND = [  # câu hỏi VN, bằng chứng VN, vị trí chunk chứa bằng chứng A/B/C
    ("t01", "Lấy mẫu phân tầng (stratified sampling) là gì?",
     "Chia tổng thể thành các nhóm con (theo tuổi, khu vực, thu nhập, học vấn) rồi lấy mẫu ngẫu nhiên từ mỗi tầng theo tỷ lệ của tầng.", "hạng 1 (p73)", "hạng 2 (hạng 1 là ví dụ p76)", "như B"),
    ("t02", "Nhược điểm chính của lấy mẫu thuận tiện (convenience sampling)?",
     "Có thể không đại diện cho tổng thể vì dễ bị thiên lệch chọn mẫu.", "hạng 1 (p73)", "hạng 1 (p73)", "như B"),
    ("t03", "Loại nén dữ liệu nào xóa vĩnh viễn dữ liệu bị coi là thừa?",
     "Nén có mất mát (lossy compression).", "hạng 1 (p98)", "hạng 1 (p98)", "như B"),
    ("t04", "Ngưỡng thường dùng với IQR để xác định outlier là bao nhiêu? (filter mục 3.3)",
     "Thường dùng 1.5 làm ngưỡng. (Công thức đầy đủ bị mất khi trích PDF, nhưng câu hỏi chỉ hỏi giá trị ngưỡng.)", "hạng 1 (p127)", "hạng 2 (hạng 1 là định nghĩa IQR)", "hạng 2, mọi kết quả thuộc mục 3.3"),
    ("t05", "Giá trị z-score nào bị xem là outlier? (filter mục 3.3)",
     "z-score nhỏ hơn -3 hoặc lớn hơn +3. (Chữ 'z' bị mất khi trích PDF, chỉ còn '-score'.)", "hạng 1 (p128)", "hạng 1 (p128)", "hạng 1, mọi kết quả thuộc mục 3.3"),
]


def snippet(text, n=70):
    t = text.replace(" ⏎ ", " ").strip()
    return t[:n], t[-n:]


def main():
    coh = list(csv.DictReader(open(AUDIT / "coherence_samples.csv", encoding="utf-8-sig")))
    meta = list(csv.DictReader(open(AUDIT / "metadata_audit.csv", encoding="utf-8-sig")))
    out = ["# Bản review nhãn audit (tiếng Việt)\n",
           "Đọc từng mục, thấy hợp lý thì bỏ qua; muốn đổi điểm thì nhắn số mục và điểm mới (ví dụ: *mục 9 → 1*). "
           "Điểm là **đề xuất của Claude**, bạn chỉ cần đồng ý hoặc sửa.\n",
           "## 1. Coherence (mạch lạc của chunk): 20 chunk\n",
           "Thang: **0** = bị cắt giữa ý, thiếu chủ thể nên không hiểu; **1** = hiểu một phần, thiếu ngữ cảnh; **2** = tự hiểu được, giữ trọn ý.\n",
           "A = chunk cố định 500 ký tự (hay cắt giữa câu); B/C = chunk theo đoạn văn. Mỗi vị trí có một cặp A và B để so sánh.\n"]
    for i, r in enumerate(coh):
        head, tail = snippet(r["chunk_text"])
        gist, why = GIST[i]
        out.append(f"**Mục {i + 1}** (vị trí {r['position']}, trang {r['page']}, mục {r['section']}, chiến lược **{r['strategy']}**, {r['n_chars']} ký tự)  \n"
                   f"- Bắt đầu: `{head}`  \n- Kết thúc: `{tail}`  \n- Nội dung: {gist}  \n"
                   f"- Điểm đề xuất: **{r['score_0_2']}** — {why}\n")
    a = [int(r["score_0_2"]) for r in coh if r["strategy"] == "A"]
    b = [int(r["score_0_2"]) for r in coh if r["strategy"] == "B"]
    out.append(f"**Trung bình hiện tại:** A = {sum(a)}/10 = {sum(a)/10:.2f}; B = {sum(b)}/10 = {sum(b)/10:.2f} (C dùng chunk của B).\n")
    out += ["## 2. Grounding (đủ bằng chứng để trả lời): 5 câu test × 3 chiến lược\n",
            "Thang: **0** = top-3 không có bằng chứng; **1** = có nhưng thiếu điều kiện/ngữ cảnh; **2** = đủ để trả lời và truy được nguồn. "
            "Cả 15 trường hợp đều được chấm **2** vì chunk chứa câu bằng chứng nằm trong top-3. Vì tất cả đều 2 nên mục này không phân biệt được chiến lược.\n",
            "| Câu | Câu hỏi (VN) | Bằng chứng (VN) | A | B | C |", "|---|---|---|---|---|---|"]
    for g in GROUND:
        out.append(f"| {g[0]} | {g[1]} | {g[2]} | {g[3]} | {g[4]} | {g[5]} |")
    ok = sum(r["manual_metadata_ok"] == "True" for r in meta)
    out += ["", "## 3. Metadata: 45 bản ghi (5 câu × top-3 × A/B/C)\n",
            f"Kết quả: **{ok}/45** đúng. Cách kiểm tra:\n",
            "1. Script tự động kiểm tra: đoạn văn của chunk có thật trên đúng trang PDF được ghi (45/45).",
            "2. `source`, `chapter`, `section` khớp mục lục PDF; các trang nằm ở ranh giới hai mục (76, 86, 98) đã đọc tay.",
            "3. Với C, các kết quả có filter (t04, t05) đều đúng mục 3.3.\n",
            "Tự kiểm tra thử 1 dòng nếu muốn: mở `metadata_audit.csv`, lấy một dòng bất kỳ (ví dụ trang 127), mở PDF ở trang vật lý 127 "
            "(số in trên sách = 117) và xem đoạn văn có đúng ở đó và đúng thuộc mục 3.3 không.\n",
            "Hạn chế: kiểm tra metadata chủ yếu do script làm; trường hữu ích để lọc là `section` (phân biệt được các mục có chủ đề trùng như outlier ở 2.4/3.1/3.3).\n"]
    (AUDIT / "REVIEW_VI.md").write_text("\n".join(out), encoding="utf-8")
    print("written", AUDIT / "REVIEW_VI.md")


if __name__ == "__main__":
    main()
