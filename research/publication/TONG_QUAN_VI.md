# Tài trợ vốn theo doanh thu cho người bán thương mại điện tử

**Bối cảnh, vấn đề, sản phẩm và nghiên cứu**

Lê Hữu Hoàng · Tháng 8 năm 2026
lehuuhoang1909@gmail.com

> **Phạm vi của tài liệu này.** Mọi con số trong đây là **kết quả mô phỏng** theo các giả định được nêu rõ. Nghiên cứu này **không sử dụng bất kỳ dữ liệu doanh thu, dữ liệu trả nợ hay kết quả vỡ nợ thực tế nào**. Đây không phải là bằng chứng về hành vi của người bán thật, không phải khuyến nghị tín dụng, và không phải một dịch vụ cho vay.

---

## 1. Vấn đề

Một người bán trên Shopee hoặc Lazada cần vốn lưu động. Họ nhập hàng trước, bán sau, và khoảng trống giữa hai việc đó là nơi tiền bị kẹt.

Ngân hàng thường không cho vay. Không phải vì người bán làm ăn kém, mà vì **hồ sơ tín dụng mỏng hoặc không có** — không có lịch sử CIC, không có tài sản thế chấp, không có báo cáo tài chính được kiểm toán. Theo cách chấm điểm truyền thống, người bán này gần như vô hình.

Nhưng có một điều nền tảng thương mại điện tử ghi lại liên tục: **doanh thu**. Từng đơn hàng, từng ngày, từng tháng. Đây là dữ liệu mà ngân hàng không có nhưng nền tảng thì có sẵn.

> **Lưu ý quan trọng, nêu rõ ngay từ đầu.** Việc bên cấp vốn có thể tiếp cận dữ liệu giao dịch của người bán là **một giả định thiết kế của nghiên cứu này**, không phải điều đã được chứng minh. Nghiên cứu không khẳng định các nền tảng tại Việt Nam cho phép truy cập dữ liệu đó, và cũng không đưa ra con số nào về tỷ lệ người bán Việt Nam thiếu hồ sơ CIC — chúng tôi không tìm được nguồn nào chứng minh điều đó.

---

## 2. Cơ chế hợp đồng

Thay vì trả một khoản cố định hằng tháng, người bán trả **một tỷ lệ cố định trên doanh thu thực nhận**, cho đến khi đạt mức trần đã thỏa thuận.

| Ký hiệu | Ý nghĩa |
|---|---|
| `A` | Số tiền ứng trước |
| `r` | Tỷ lệ trích trên doanh thu thuần mỗi tháng |
| `f` | Hệ số trần (giá của hợp đồng) |
| `C = A × f` | **Mức trần hợp đồng** — thu đến đây thì dừng |

Tháng bán tốt, trả nhiều. Tháng ế, trả ít. Khi tổng đã trả chạm `C`, hợp đồng kết thúc.

Điều này nghe có vẻ hiển nhiên là tốt cho người bán. Nghiên cứu cho thấy nó **không đơn giản như vậy** — và đó chính là lý do nghiên cứu tồn tại.

---

## 3. Sản phẩm demo

Có một bản demo đang chạy tại **sellerflow-production.up.railway.app**.

Người bán nhập số liệu hoạt động, hệ thống trả về: số tiền ứng đề xuất, tỷ lệ trích, mức trần hoàn trả, các kịch bản suy giảm doanh thu, và danh sách rủi ro kèm bằng chứng cho từng mục.

**Bản demo này là gì và không là gì:**

- Là **bản trình diễn kỹ thuật**. Không nắm giữ vốn, không cấp tín dụng, không đưa ra bất kỳ cam kết cho vay nào.
- Tính đến tháng 8/2026, **chưa sử dụng dữ liệu của bất kỳ người bán bên ngoài nào**. Cơ sở dữ liệu chỉ chứa bản ghi trình diễn và dữ liệu kiểm thử.
- Chưa kết nối API với bất kỳ nền tảng nào. Số liệu là **người dùng tự khai và chưa được xác minh**.
- Mô hình chấm điểm rủi ro là **thành phần phụ, chưa được kiểm chứng**. Chỉ số AUC 0,92 từng được báo cáo đã bị **rút lại** vì lỗi vòng lặp logic: nhãn huấn luyện được sinh ra từ chính các biến mà mô hình sử dụng, nên chỉ số đó đo lại công thức của chính nó chứ không đo khả năng dự báo.

Toàn bộ phần tính toán tài chính là **số học thuần túy, tất định** — không có mô hình nào can thiệp vào công thức. Nhưng cần nói rõ: đường chấm điểm đang hoạt động **quyết định hạng rủi ro**, và mọi điều khoản đều bám theo hạng đó. Ở mức doanh thu 200 triệu/tháng, trần hoàn trả là **414.000.000 đ** ở hạng Thấp so với **249.600.000 đ** ở hạng Trung bình; hạng Cao thì không có khoản ứng nào. Một tuyên bố trước đây rằng "các con số giống nhau dù chạy đường nào" là **sai và đã được rút lại**.

---

## 4. Nghiên cứu: câu hỏi đặt ra

Hình thức này **có tốt hơn khoản vay thông thường không, và tốt hơn cho ai?**

Trả lời câu hỏi này bằng dữ liệu thực đòi hỏi quan sát **cùng một người bán** dưới **cả hai hợp đồng** trên **cùng một đường doanh thu**. Điều đó không tồn tại — mỗi người bán chỉ ký một hợp đồng.

Vì vậy nghiên cứu dùng **mô phỏng ghép cặp**: 10 kịch bản doanh thu × 4 loại hợp đồng × 500 đường mô phỏng. Cả bốn hợp đồng chạy trên **đúng cùng một đường doanh thu**, nên khi so sánh, khác biệt duy nhất là **thời điểm trả tiền**, chứ không lẫn với giá.

Cái giá của phương pháp này cũng rõ ràng: **quá trình sinh doanh thu là do chúng tôi định nghĩa**. Kết quả mô tả cơ chế hợp đồng dưới các giả định đã nêu, không mô tả hành vi người bán thật.

---

## 5. Ba phát hiện

### 5.1 Giá và cấu trúc là hai câu hỏi tách rời — và người ta thường nhập chúng làm một

Đây là đóng góp chính, và tôi rút ra được vì **tự mình mắc lỗi đó trước**.

Một bản nháp đầu từng viết: hợp đồng theo doanh thu "đắt gấp khoảng 2,3 lần lãi vay thông thường". Câu đó **đã bị rút lại**, vì nó cố định một hệ số trần rồi coi kết quả như thuộc tính của cấu trúc.

Giữ **nguyên quy tắc trả tiền**, chỉ đổi giá từ `f = 1,20` sang `f* = 1,0945`, thì kết luận về chi phí **đảo chiều**. Cùng một cấu trúc, hai kết luận trái ngược.

Nói cách khác: bất kỳ ai trích một tỷ lệ chi phí ở **một** mức giá đều đang mô tả **lựa chọn giá đó**, không phải bản chất của hình thức tài trợ theo doanh thu.

### 5.2 Đây là một sự đánh đổi, không phải một chiến thắng

Trong kịch bản suy giảm nghiêm trọng, ở `f = 1,20`:

| | Người bán | Bên cấp vốn |
|---|---|---|
| Hợp đồng theo doanh thu | **giảm 6,85 tháng** có gánh nặng trả nợ vượt 15% doanh thu | thu hồi **65,46%** mục tiêu sau 12 tháng |
| Khoản trả cố định tương đương | 6,85 tháng vượt ngưỡng | thu hồi **92,31%** |

Hai cột là **cùng một cơ chế nhìn từ hai phía**. Báo cáo một cột mà giấu cột kia là bán hàng, không phải đo lường.

Và chiều của nó **không cố định**: tùy đường doanh thu thực tế, thu hồi theo doanh thu có thể **nhanh hơn hoặc chậm hơn** khoản cố định. Cả hai chiều đều xuất hiện trong thư viện kịch bản. Không được phát biểu như một quy luật chung.

### 5.3 Nó **không** ngăn được vỡ nợ

Đây là phần dễ bị nói quá nhất, nên nói thẳng.

Nếu người bán **đóng cửa vĩnh viễn trước khi trả hết**, phần còn lại **không thu được**. Không có cơ chế nào cứu được điều đó.

| Kịch bản | Không thu hồi đủ, `f = 1,20` | Không thu hồi đủ, `f* = 1,0945` |
|---|---|---|
| Đóng cửa từ tháng 7 | **100,0%** | **100,0%** |
| Đóng cửa từ tháng 13 | **76,2%** | **7,6%** |
| Ngừng tạm thời 3 tháng | 2,0% | **0,0%** |

Hai điều cần nhấn mạnh:

1. Câu "trả theo doanh thu thì kéo dài kỳ hạn thay vì vỡ nợ" là **sai** và đã bị rút khỏi mọi tài liệu. Đóng cửa từ tháng 7 khiến **100% đường mô phỏng** không thu hồi đủ, ở **cả hai** mức giá.
2. **"Không thu hồi đủ" không phải là "mất vốn".** Đó là hiện tượng cắt cụt quan sát trong cửa sổ 24 tháng, không phải tỷ lệ vỡ nợ — nghiên cứu này không mô hình hóa hành vi vỡ nợ trên bất kỳ hợp đồng nào. Sự phân biệt này được xây dựng vào sản phẩm một cách rõ ràng, để con số 76,2% không bị đọc nhầm thành tỷ lệ mất vốn.

Riêng dòng "đóng cửa từ tháng 13": con số dịch chuyển **gấp mười lần** chỉ vì đổi giá, trong khi quy tắc trả tiền giữ nguyên. Đó lại chính là phát hiện 5.1, xuất hiện lần nữa trong thống kê rủi ro.

---

## 6. Cách kiểm chứng

Điểm mạnh của công trình này không nằm ở kết quả, mà ở chỗ **kết quả có thể kiểm chứng độc lập**.

- **Năm tệp kết quả** có mã băm SHA-256 đăng ký. Bất kỳ ai cũng tạo lại được và đối chiếu mã băm.
- **1.145 bài kiểm thử tự động** (502 backend + 643 mô phỏng), cùng 9 bài kiểm thử giao diện đã chạy và đạt.
- **Bảy mệnh đề toán học** được chứng minh bằng suy luận, không phải bằng mô phỏng, và mỗi mệnh đề được kiểm tra lại bằng chương trình.
- **Nhật ký quyết định** ghi lại từng lần rút lại tuyên bố, kèm bằng chứng đã bác bỏ nó.

Điểm cuối là điều tôi muốn người đọc chú ý nhất. Ba tuyên bố do chính tôi viết ra đã bị rút lại: tỷ lệ chi phí 2,3 lần, một tuyên bố về tính tái lập dựa trên một phép kiểm tra **không thể nào thất bại**, và một kết quả "không khác biệt" hóa ra sai ở 6 trên 10 kịch bản.

---

## 7. Những gì nghiên cứu này **không** trả lời

Nêu rõ, vì đây là giới hạn thật chứ không phải khiêm tốn hình thức:

- **Người bán thật có trả nợ như mô phỏng không?** Không biết. Không có dữ liệu thực nào trong nghiên cứu.
- **Hợp đồng này có "vừa sức" với người bán không?** Không biết. Gánh nặng được đo trên **doanh thu**, không phải trên phần người bán còn lại sau chi phí. Biên lợi nhuận, chi phí vận hành, các khoản nợ khác đều nằm ngoài mô hình.
- **Các ngưỡng 10/15/20/25% có phản ánh khó khăn thật không?** Không. Đó là các mốc báo cáo do nghiên cứu tự chọn, không phải ngưỡng đã được kiểm chứng.
- **So sánh với khoản vay cố định có công bằng không?** Mô hình **giả định** khoản cố định luôn được trả đủ và đúng hạn. Vì vậy nó là một **chuẩn so sánh lạc quan** cho phía cho vay, không phải một dự báo.
- **Lãi suất 18%, kỳ hạn 12 tháng, hình dạng mùa vụ có phản ánh thị trường Việt Nam không?** Không. Tất cả đều là giả định. Không tham số nào được ước lượng từ dữ liệu Việt Nam. Nghiên cứu này **lấy cảm hứng từ bối cảnh Việt Nam, không hiệu chỉnh theo Việt Nam**.

---

## 8. Hiện trạng

| Hạng mục | Trạng thái |
|---|---|
| Bài nghiên cứu | Hoàn chỉnh — 19 trang, 15 mục, định dạng bài báo học thuật |
| Bản demo | Đang chạy |
| Tệp kết quả | 5 tệp, có mã băm, tái lập được |
| Kiểm thử | 1.145 bài, đạt toàn bộ |
| Dữ liệu thực | **Chưa có** — đây là giới hạn lớn nhất |

Bước tiếp theo, nếu có, là dữ liệu trả nợ thực tế. Đó là thứ duy nhất biến công trình này từ **nghiên cứu cơ chế hợp đồng** thành **bằng chứng về hành vi thị trường**. Chừng nào chưa có, mọi con số ở đây vẫn là mô phỏng — và tài liệu này gọi đúng tên nó ở mọi chỗ.

---

*Bài nghiên cứu đầy đủ bằng tiếng Anh: `MANUSCRIPT.pdf`. Mã nguồn, dữ liệu và toàn bộ nhật ký quyết định: github.com/hoangle0919/sellerflow*
