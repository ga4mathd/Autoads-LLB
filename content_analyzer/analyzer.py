import os
import anthropic
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

api_key = os.getenv('CLAUDE_OPUS_KEY')
client = anthropic.Anthropic(api_key=api_key)

THRESHOLDS = {
    'VN': {'ctr': 1.5, 'hook_3s': 40, 'retention_25': 30, 'retention_50': 15, 'retention_75': 8},
    'KH': {'ctr': 1.2, 'hook_3s': 35, 'retention_25': 25, 'retention_50': 12, 'retention_75': 6},
    'PH': {'ctr': 1.3, 'hook_3s': 38, 'retention_25': 28, 'retention_50': 13, 'retention_75': 7},
}

def classify_and_analyze(video, metrics):
    market = video.get('market', 'VN')
    market_code = market[:2].upper() if market else 'VN'
    thresholds = THRESHOLDS.get(market_code, THRESHOLDS['VN'])
    
    checks = {
        'CTR': (metrics['ctr'], thresholds['ctr']),
        'Hook 3s': (metrics['hook_rate_3s'], thresholds['hook_3s']),
        'Retention 25%': (metrics['retention_25'], thresholds['retention_25']),
        'Retention 50%': (metrics['retention_50'], thresholds['retention_50']),
        'Retention 75%': (metrics['retention_75'], thresholds['retention_75']),
    }
    
    passed = sum(1 for actual, threshold in checks.values() if actual >= threshold)
    classification = 'WIN' if passed >= 3 else 'FAIL'
    score = f"{passed}/5"
    
    details_table = ""
    for name, (actual, threshold) in checks.items():
        status = "✅ ĐẠT" if actual >= threshold else "❌ CHƯA"
        details_table += f"| {name} | {actual}% | ≥{threshold}% | {status} |\n"
        
    if classification == 'WIN':
        analysis, recommendations = analyze_win(video, metrics, details_table, score)
    else:
        analysis, recommendations = analyze_fail(video, metrics, details_table, score)
        
    return {
        'classification': classification,
        'score': score,
        'analysis': analysis,
        'recommendations': recommendations,
        'checks': checks,
        'details_table': details_table,
    }

def analyze_win(video, metrics, details_table, score):
    prompt = f"""Bạn là Senior Creative Strategist chuyên phân tích content viral cho Lollibooks — thương hiệu sách tương tác trẻ em tại Đông Nam Á.
Video dưới đây đã được phân loại 🟢 WIN ({score}) sau 3 ngày chạy ads.
=== THÔNG TIN VIDEO ===
- Mã kịch bản: {video['script_id']}
- Tên Campaign: {video['camp_name']}
- Thị trường: {video['market']}
- Loại Campaign: {video['camp_type']}
- Target: {video['age_min']}-{video['age_max']} tuổi
- Caption: {video['caption']}
- CTA: {video['cta']}
- Ngân sách/ngày: {video['budget']} VND
=== CHỈ SỐ HIỆU SUẤT (3 ngày) ===
- Impressions: {metrics['impressions']:,}
- Reach: {metrics['reach']:,}
- CTR: {metrics['ctr']}%
- CPM: {metrics['cpm']:,.0f}
- CPC: {metrics['cpc']:,.0f}
- CPA: {metrics['cpa']:,.0f}
- Chi phí: {metrics['spend']:,.0f} VND
=== CHỈ SỐ VIDEO ===
- Video Views: {metrics['video_views']:,}
- Hook Rate 3s: {metrics['hook_rate_3s']}%
- Retention 25%: {metrics['retention_25']}%
- Retention 50%: {metrics['retention_50']}%
- Retention 75%: {metrics['retention_75']}%
- Retention 100%: {metrics['retention_100']}%
=== BẢNG PHÂN LOẠI ===
| Chỉ số | Thực tế | Ngưỡng | Kết quả |
|--------|---------|--------|---------|
{details_table}
=== YÊU CẦU PHÂN TÍCH ===
Hãy phân tích theo đúng cấu trúc sau:
**1. MỔ XẺ KỊCH BẢN (Script Anatomy)**
**2. INSIGHT RÚT RA**
**3. ĐỀ XUẤT NHÂN BẢN (5 CÁCH)**
**4. BRIEF CHO TEAM (TÓM GỌN)**
Viết ngắn gọn, súc tích, dùng bullet points."""
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    full_text = response.content[0].text
    if "ĐỀ XUẤT NHÂN BẢN" in full_text:
        parts = full_text.split("ĐỀ XUẤT NHÂN BẢN", 1)
        return parts[0].strip(), "ĐỀ XUẤT NHÂN BẢN" + parts[1].strip()
    return full_text, ""

def analyze_fail(video, metrics, details_table, score):
    prompt = f"""Bạn là Video Performance Doctor — chuyên gia chẩn đoán video ads không hiệu quả cho Lollibooks — thương hiệu sách tương tác trẻ em tại Đông Nam Á.
Video dưới đây đã FAIL ({score}) sau 3 ngày chạy.
=== THÔNG TIN VIDEO ===
- Mã kịch bản: {video['script_id']}
- Tên Campaign: {video['camp_name']}
- Thị trường: {video['market']}
- Target: {video['age_min']}-{video['age_max']} tuổi
- Caption: {video['caption']}
- Ngân sách/ngày: {video['budget']} VND
=== CHỈ SỐ HIỆU SUẤT ===
- Impressions: {metrics['impressions']:,}
- Hook Rate 3s: {metrics['hook_rate_3s']}%
- Retention 25%: {metrics['retention_25']}%
- Retention 50%: {metrics['retention_50']}%
- Retention 75%: {metrics['retention_75']}%
=== BẢNG PHÂN LOẠI ===
| Chỉ số | Thực tế | Ngưỡng | Kết quả |
|--------|---------|--------|---------|
{details_table}
=== YÊU CẦU CHẨN ĐOÁN ===
**PHẦN 1: RETENTION CURVE — XÁC ĐỊNH ĐIỂM GÃY**
**PHẦN 2: CHẨN ĐOÁN 4 TẦNG**
**PHẦN 3: ĐỀ XUẤT SỬA (3 PHƯƠNG ÁN)**
**PHẦN 4: TÓM TẮT CHO TEAM**
Viết ngắn gọn, súc tích, dùng bullet points."""

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    full_text = response.content[0].text
    if "ĐỀ XUẤT SỬA" in full_text:
        parts = full_text.split("ĐỀ XUẤT SỬA", 1)
        return parts[0].strip(), "ĐỀ XUẤT SỬA" + parts[1].strip()
    return full_text, ""
