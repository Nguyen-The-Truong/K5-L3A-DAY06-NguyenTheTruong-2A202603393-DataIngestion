# Bản review nhãn audit (tiếng Việt)

Đọc từng mục, thấy hợp lý thì bỏ qua; muốn đổi điểm thì nhắn số mục và điểm mới (ví dụ: *mục 9 → 1*). Điểm là **đề xuất của Claude**, bạn chỉ cần đồng ý hoặc sửa.

## 1. Coherence (mạch lạc của chunk): 20 chunk

Thang: **0** = bị cắt giữa ý, thiếu chủ thể nên không hiểu; **1** = hiểu một phần, thiếu ngữ cảnh; **2** = tự hiểu được, giữ trọn ý.

A = chunk cố định 500 ký tự (hay cắt giữa câu); B/C = chunk theo đoạn văn. Mỗi vị trí có một cặp A và B để so sánh.

**Mục 1** (vị trí p067-s2.0, trang 67, mục 2.0, chiến lược **A**, 499 ký tự)  
- Bắt đầu: `ever-increasing volume of data, a robust approach to data collection i`  
- Kết thúc: ` user-generated information. And it requires meticulous planning and e`  
- Nội dung: Nói về thu thập dữ liệu cần phương pháp có hệ thống để đảm bảo chất lượng; nguồn gồm CSDL nội bộ, kho bên ngoài, website...  
- Điểm đề xuất: **1** — Bắt đầu giữa cụm từ, kết thúc giữa từ nhưng vẫn đọc hiểu được.

**Mục 2** (vị trí p067-s2.0, trang 67, mục 2.0, chiến lược **B**, 605 ký tự)  
- Bắt đầu: `With today’s ever-increasing volume of data, a robust approach to data`  
- Kết thúc: `he accuracy, comprehensiveness, and reliability of the collected data.`  
- Nội dung: Cùng đoạn trên nhưng lấy trọn cả đoạn văn.  
- Điểm đề xuất: **2** — Trọn một đoạn, bắt đầu và kết thúc ở đầu/cuối câu.

**Mục 3** (vị trí p073-s2.2, trang 73, mục 2.2, chiến lược **A**, 499 ký tự)  
- Bắt đầu: `presentative sample of the state's student population without having t`  
- Kết thúc: `ce sampling is effortless to achieve, and it is useful for exploratory`  
- Nội dung: Cuối ví dụ cluster sampling (bắt đầu giữa từ 'presentative') và định nghĩa lấy mẫu thuận tiện, cụt ở 'exploratory'.  
- Điểm đề xuất: **1** — Bắt đầu giữa từ, kết thúc cụt, nhưng phần định nghĩa vẫn hiểu.

**Mục 4** (vị trí p073-s2.2, trang 73, mục 2.2, chiến lược **B**, 882 ký tự)  
- Bắt đầu: `An example of cluster sampling would be a study on the effectiveness o`  
- Kết thúc: `ng is effortless to achieve, and it is useful for exploratory studies.`  
- Nội dung: Trọn ví dụ cluster sampling và định nghĩa đầy đủ của lấy mẫu thuận tiện.  
- Điểm đề xuất: **2** — Hai ý đều trọn vẹn.

**Mục 5** (vị trí p080-s2.3, trang 80, mục 2.3, chiến lược **A**, 499 ký tự)  
- Bắt đầu: `ng of characters into smaller units called tokens, which can be words,`  
- Kết thúc: `-source library for natural language processing. It provides efficient`  
- Nội dung: Giữa danh sách thư viện Python xử lý văn bản: cuối mục tokenization, TextBlob, SpaCy; cụt giữa câu.  
- Điểm đề xuất: **1** — Đầu giữa từ, cuối giữa câu.

**Mục 6** (vị trí p080-s2.3, trang 80, mục 2.3, chiến lược **B**, 871 ký tự)  
- Bắt đầu: `This library provides a simple interface for most natural language pro`  
- Kết thúc: `rted by the re module (function), and their syntax is similar to other`  
- Nội dung: Bắt đầu 'This library...' (không nói tên thư viện), rồi SpaCy, câu tổng kết 'Overall', và mở sang chủ đề mới Regular Expressions.  
- Điểm đề xuất: **1** — Thiếu tên thư viện ở đầu; lẫn hai chủ đề.

**Mục 7** (vị trí p088-s2.4, trang 88, mục 2.4, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `.2 US Retail Employment with Outliers (Data source: Bureau of Labor St`  
- Kết thúc: `g this month shows a significant jump from approximately 5,400 to 9,50`  
- Nội dung: Mảnh chú thích hình + lời giải: phát hiện outlier tháng 3/1990, số nhảy từ ~5.400 lên 9.50(0) thì bị cụt.  
- Điểm đề xuất: **1** — Đầu giữa chú thích hình, cuối cụt giữa số.

**Mục 8** (vị trí p088-s2.4, trang 88, mục 2.4, chiến lược **B**, 854 ký tự)  
- Bắt đầu: `EXAMPLE 2.6  Problem  Starting in 1939, the United States Bureau of La`  
- Kết thúc: `ppears that an outlier is present in the employment data for March 28,`  
- Nội dung: Đề bài Example 2.6 trọn vẹn, chú thích hình, mở đầu lời giải, cụt ở 'March 28,'.  
- Điểm đề xuất: **1** — Đề bài đủ nhưng phần lời giải (câu trả lời) bị cụt do hết trang.

**Mục 9** (vị trí p097-s2.4, trang 97, mục 2.4, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `encoded vectors for these words would be: great: [1, 0, 0, 0, 0, 0, 0]`  
- Kết thúc: `s a text with @special# text for analysis characters and punctuation c`  
- Nội dung: Danh sách mã one-hot, kế đó là các ô bảng bị xáo trộn ('Removing special Simplifying the...'); cắt giữa từ cả hai đầu.  
- Điểm đề xuất: **0** — Cắt cả hai đầu và bảng lộn xộn nên khó hiểu.

**Mục 10** (vị trí p097-s2.4, trang 97, mục 2.4, chiến lược **B**, 975 ký tự)  
- Bắt đầu: `Encoding Converting text into a numerical representation for machine l`  
- Kết thúc: `ters!*” and the output: “Hello this is a text with special characters”`  
- Nội dung: Khái niệm one-hot đầy đủ, nhưng kèm các ô bảng bị xáo trộn.  
- Điểm đề xuất: **1** — Khái niệm trọn, phần bảng lộn xộn.

**Mục 11** (vị trí p113-s3.0, trang 113, mục 3.0, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `medical and engineering analysis. Statistical analysis is an essential`  
- Kết thúc: `arketing strategies. As a consumer, statistical analysis plays a signi`  
- Nội dung: Đầu chương 3: thống kê dùng trong y khoa, kỹ thuật...; cụt ở 'signi'.  
- Điểm đề xuất: **1** — Đầu giữa câu, cuối giữa từ.

**Mục 12** (vị trí p113-s3.0, trang 113, mục 3.0, chiến lược **B**, 823 ký tự)  
- Bắt đầu: `Statistical analysis is an essential aspect of data science, involving`  
- Kết thúc: ` descriptive statistics, which refers to the collection, organization,`  
- Nội dung: Các đoạn trọn về vai trò của thống kê với người tiêu dùng (ví dụ mua nhà); chỉ cụt vế cuối do hết trang.  
- Điểm đề xuất: **2** — Đoạn trọn, chỉ cụt phần rất cuối.

**Mục 13** (vị trí p120-s3.1, trang 120, mục 3.1, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `are $410.14 million, and the median earnings are $309.35 million. Note`  
- Kết thúc: `Figure 3.2 The Output of DataFrame.describe() with the Movie Profit Da`  
- Nội dung: Lời bình về kết quả DataFrame.describe(): cột 'Unnamed: 0' chỉ là mã định danh; kết thúc bằng chú thích hình.  
- Điểm đề xuất: **1** — Bắt đầu giữa câu; chưa rõ đang nói dataset nào.

**Mục 14** (vị trí p120-s3.1, trang 120, mục 3.1, chiến lược **B**, 1000 ký tự)  
- Bắt đầu: `summarize data. Recall that the method describe() is defined for a Dat`  
- Kết thúc: ` with the Movie Profit Dataset  EXPLORING FURTHER  Working with Python`  
- Nội dung: Bắt đầu giữa câu 'summarize data. Recall that describe()...', có chú thích hình, kết bằng tiêu đề lửng 'EXPLORING FURTHER'.  
- Điểm đề xuất: **1** — Đầu giữa câu, cuối là tiêu đề lửng.

**Mục 15** (vị trí p127-s3.3, trang 127, mục 3.3, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `iles and the IQR to calculate a lower and an upper bound for outliers.`  
- Kết thúc: `a cutoff value to identify outliers in a dataset. EXAMPLE 3.12 Problem`  
- Nội dung: Bắt đầu giữa từ; câu 'dùng 1.5 làm ngưỡng' và tiêu đề EXAMPLE 3.12; công thức bị mất khi trích PDF.  
- Điểm đề xuất: **1** — Đầu giữa từ; công thức thiếu.

**Mục 16** (vị trí p127-s3.3, trang 127, mục 3.3, chiến lược **B**, 963 ký tự)  
- Bắt đầu: `To detect outliers, you can use the quartiles and the IQR to calculate`  
- Kết thúc: `9950, 479000, 488800, 529000, 575000, 639000, 659000, 1095000, 5500000`  
- Nội dung: Đoạn trọn về phát hiện outlier bằng IQR, câu 'ngưỡng 1.5', và trọn đề bài + dữ liệu Example 3.12 (công thức mất do trích PDF).  
- Điểm đề xuất: **2** — Trọn ý; thiếu công thức là lỗi của việc trích PDF, không phải của cách chia chunk.

**Mục 17** (vị trí p134-s3.4, trang 134, mục 3.4, chiến lược **A**, 500 ký tự)  
- Bắt đầu: `ndomly chosen graduate obtained a nursing degree. The reduced sample s`  
- Kết thúc: `at the graduate is in the age group of 23 and older. The probability o`  
- Nội dung: Xác suất có điều kiện (sinh viên tốt nghiệp ngành điều dưỡng); cắt giữa từ cả hai đầu, công thức mất.  
- Điểm đề xuất: **1** — Cắt cả hai đầu; thiếu công thức.

**Mục 18** (vị trí p134-s3.4, trang 134, mục 3.4, chiến lược **B**, 859 ký tự)  
- Bắt đầu: `We can now use this equation to calculate the probability that a rando`  
- Kết thúc: ` can substitute these probabilities into the formula for , as follows:`  
- Nội dung: Bắt đầu 'We can now use this equation...' (công thức nằm ở chunk trước, không có ở đây), rồi tính xác suất.  
- Điểm đề xuất: **1** — Thiếu công thức/ngữ cảnh ở chunk trước.

**Mục 19** (vị trí p141-s3.5, trang 141, mục 3.5, chiến lược **A**, 499 ký tự)  
- Bắt đầu: `In Example 3.24, the parameters of the binomial experiment are: Substi`  
- Kết thúc: `ows the values of the random variable , and the vertical axis shows th`  
- Nội dung: Bắt đầu rõ 'In Example 3.24...', kết quả xác suất nhị thức 18/20 = 0.271; cụt ở 'shows th'.  
- Điểm đề xuất: **1** — Câu đầu rõ nhưng cuối cụt.

**Mục 20** (vị trí p141-s3.5, trang 141, mục 3.5, chiến lược **B**, 808 ký tự)  
- Bắt đầu: `Note: The notation is read as factorial and is a mathematical notation`  
- Kết thúc: `dicate that the surgery was successful is 0.271, or approximately 27%.`  
- Nội dung: Ghi chú về giai thừa (ký hiệu bị mất), đề Example 3.25, lời giải thiếu công thức.  
- Điểm đề xuất: **1** — Ký hiệu và công thức mất nhưng vẫn đoán được ý.

**Trung bình hiện tại:** A = 9/10 = 0.90; B = 14/10 = 1.40 (C dùng chunk của B).

## 2. Grounding (đủ bằng chứng để trả lời): 5 câu test × 3 chiến lược

Thang: **0** = top-3 không có bằng chứng; **1** = có nhưng thiếu điều kiện/ngữ cảnh; **2** = đủ để trả lời và truy được nguồn. Cả 15 trường hợp đều được chấm **2** vì chunk chứa câu bằng chứng nằm trong top-3. Vì tất cả đều 2 nên mục này không phân biệt được chiến lược.

| Câu | Câu hỏi (VN) | Bằng chứng (VN) | A | B | C |
|---|---|---|---|---|---|
| t01 | Lấy mẫu phân tầng (stratified sampling) là gì? | Chia tổng thể thành các nhóm con (theo tuổi, khu vực, thu nhập, học vấn) rồi lấy mẫu ngẫu nhiên từ mỗi tầng theo tỷ lệ của tầng. | hạng 1 (p73) | hạng 2 (hạng 1 là ví dụ p76) | như B |
| t02 | Nhược điểm chính của lấy mẫu thuận tiện (convenience sampling)? | Có thể không đại diện cho tổng thể vì dễ bị thiên lệch chọn mẫu. | hạng 1 (p73) | hạng 1 (p73) | như B |
| t03 | Loại nén dữ liệu nào xóa vĩnh viễn dữ liệu bị coi là thừa? | Nén có mất mát (lossy compression). | hạng 1 (p98) | hạng 1 (p98) | như B |
| t04 | Ngưỡng thường dùng với IQR để xác định outlier là bao nhiêu? (filter mục 3.3) | Thường dùng 1.5 làm ngưỡng. (Công thức đầy đủ bị mất khi trích PDF, nhưng câu hỏi chỉ hỏi giá trị ngưỡng.) | hạng 1 (p127) | hạng 2 (hạng 1 là định nghĩa IQR) | hạng 2, mọi kết quả thuộc mục 3.3 |
| t05 | Giá trị z-score nào bị xem là outlier? (filter mục 3.3) | z-score nhỏ hơn -3 hoặc lớn hơn +3. (Chữ 'z' bị mất khi trích PDF, chỉ còn '-score'.) | hạng 1 (p128) | hạng 1 (p128) | hạng 1, mọi kết quả thuộc mục 3.3 |

## 3. Metadata: 45 bản ghi (5 câu × top-3 × A/B/C)

Kết quả: **45/45** đúng. Cách kiểm tra:

1. Script tự động kiểm tra: đoạn văn của chunk có thật trên đúng trang PDF được ghi (45/45).
2. `source`, `chapter`, `section` khớp mục lục PDF; các trang nằm ở ranh giới hai mục (76, 86, 98) đã đọc tay.
3. Với C, các kết quả có filter (t04, t05) đều đúng mục 3.3.

Tự kiểm tra thử 1 dòng nếu muốn: mở `metadata_audit.csv`, lấy một dòng bất kỳ (ví dụ trang 127), mở PDF ở trang vật lý 127 (số in trên sách = 117) và xem đoạn văn có đúng ở đó và đúng thuộc mục 3.3 không.

Hạn chế: kiểm tra metadata chủ yếu do script làm; trường hữu ích để lọc là `section` (phân biệt được các mục có chủ đề trùng như outlier ở 2.4/3.1/3.3).
