# Lender outreach kit

Target list (Vietnam, in rough order of fit):

1. **Digital-first consumer/SME lenders** — Tima, F88, Validus Vietnam, Funding Societies (VN desk) — already lend to thin-file borrowers, feel bureau-gap pain daily.
2. **E-wallet / BNPL risk teams** — MoMo, ZaloPay, Kredivo Vietnam — have merchant relationships, need merchant credit models.
3. **Bank digital-SME units** — VPBank SME, TPBank, MB Bank digital — slower, but the largest checks.
4. **Platform lending programs** — Shopee (SEasy/SPayLater partners), Lazada seller financing partners — longest shot, deepest fit.

The ask is never "buy the product." It is: *"20 minutes to show you a scoring approach for merchants you currently decline."*

---

## Cold email (EN)

**Subject:** Scoring the Shopee sellers you currently decline

Hi {Name},

Most Vietnamese ecommerce sellers fail bank underwriting for one
reason: no CIC file. But a seller with 680 days of order history,
a 4.9 rating, and 2.8% returns is not thin-file — the data just
isn't in a bureau.

I've built SellerFlow, a decisioning layer that scores merchants
from operational data — revenue trajectory, returns, delivery
performance, ratings — and returns a full credit decision
(PD, limit, rate, reasoning) through one API call in under a second.

You keep the capital and the license; SellerFlow only scores.

Live product: https://sellerflow-production.up.railway.app
(API docs at /api/docs — you can score a test merchant right now.)

Would 20 minutes next week be worth it to see it run against a
profile you'd currently decline?

{Your name}
Founder, SellerFlow — Ho Chi Minh City

---

## Cold email (VI)

**Tiêu đề:** Chấm điểm tín dụng cho seller Shopee mà ngân hàng đang từ chối

Chào anh/chị {Tên},

Phần lớn seller TMĐT Việt Nam bị từ chối vay vì một lý do: không có
lịch sử CIC. Nhưng một seller với 680 ngày bán hàng, rating 4.9 và
tỷ lệ hoàn trả 2.8% không hề "thiếu dữ liệu" — dữ liệu chỉ không
nằm ở CIC.

Em xây dựng SellerFlow — một lớp chấm điểm tín dụng dựa trên dữ liệu
vận hành: doanh thu, tăng trưởng, hoàn trả, giao hàng, đánh giá.
Một API call trả về quyết định đầy đủ (PD, hạn mức, lãi suất,
lý do) trong dưới 1 giây.

Bên anh/chị giữ vốn và giấy phép — SellerFlow chỉ chấm điểm.

Sản phẩm đang chạy: https://sellerflow-production.up.railway.app

Anh/chị có 20 phút tuần sau để em demo trực tiếp với một hồ sơ
mà quy trình hiện tại của mình đang từ chối không ạ?

{Tên}
Founder, SellerFlow — TP.HCM

---

## The honest FAQ (they will ask; answer straight)

**"What is the model trained on?"**
A synthetic baseline calibrated to realistic seller distributions —
that's exactly why I'm talking to you. A pilot on your historical
declined/approved book is how it becomes real. Your data never
leaves your side of the pilot design.

**"Is the platform data verified?"**
Today it's self-reported; platform API integration (Shopee Open
Platform) is the next build. A pilot can also run on data you
already collect from applicants.

**"What do you want from a pilot?"**
Retro-score 200–500 of your past SME/merchant applications where you
know the outcome. Compare my ranking against yours. No integration,
no cost, two weeks. If the model ranks risk better than your current
process on merchants you declined, we talk terms.

That last answer is the whole pitch: a retro-scoring pilot costs the
lender nothing, requires no integration, and gives you real outcome
data — the one thing the model actually needs.
