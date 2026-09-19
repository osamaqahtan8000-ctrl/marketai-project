import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

app = FastAPI(title="MarketAI API", version="2.0.0")

# إعداد CORS للسماح للواجهة بالاتصال بالباك إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# مفتاح API
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# نماذج البيانات (Pydantic Models)
class ProductInput(BaseModel):
    product_name: str
    category: str
    target_audience: Optional[str] = "عام"
    price: Optional[float] = 0.0

class MarketingOutput(BaseModel):
    marketing_description: str
    seo_tags: List[str]
    social_media_post: str

class PricingRequest(BaseModel):
    product_name: str
    category: str
    target_audience: Optional[str] = "الجمهور العام"

@app.get("/")
def home():
    return {"message": "MarketAI Backend is running smoothly!"}

# مسار توليد المحتوى التسويقي
@app.post("/generate-marketing", response_model=MarketingOutput)
async def generate_marketing(data: ProductInput):
    if not client:
        return MarketingOutput(
            marketing_description=f"منتج {data.product_name} المتميز في قسم {data.category}. جودة عالية وتصميم مبتكر.",
            seo_tags=[data.category, "تسوق_أونلاين", "منتجات_مميزة"],
            social_media_post=f"اكتشف الآن {data.product_name}! متوفر بسعر مميز. #تسوق"
        )
    
    prompt = f"""
    أنت خبير تسويق رقمي ومتخصص في التجارة الإلكترونية.
    المطلوب: توليد محتوى ترويجي جذاب للمنتج التالي:
    - الاسم: {data.product_name}
    - التصنيف: {data.category}
    - الجمهور المستهدف: {data.target_audience}
    - السعر: {data.price}$

    أجب بصيغة JSON فقط:
    {{
        "marketing_description": "وصف تسويقي مقنع في سطرين أو ثلاثة",
        "seo_tags": ["كلمة1", "كلمة2", "كلمة3"],
        "social_media_post": "منشور ترويجي جذاب للسوشيال ميديا مع هاشتاقات"
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        return json.loads(clean_text.strip())
    except Exception as e:
        return MarketingOutput(
            marketing_description=f"منتج {data.product_name} المتميز. جودة فائقة وتصميم عصري يواكب احتياجاتك اليومية.",
            seo_tags=[data.category, "عروض", "تخفيضات"],
            social_media_post=f"لا تفوّت فرصة اقتناء {data.product_name} الآن بسعر {data.price}$ فقط!"
        )

# مسار التسعير التنافسي الذكي وكود الخصم
@app.post("/suggest-pricing")
async def suggest_pricing(data: PricingRequest):
    fallback_response = {
        "suggested_price": 75,
        "price_min": 60,
        "price_max": 90,
        "reasoning": "سعر تنافسي متوازن يلائم معايير السوق ويحقق هامش ربح ممتاز للمتجر.",
        "promo_code": "PROMO20",
        "promo_discount": "20%",
        "promo_message": "خصم خاص ومحدود 20% بمناسبة إطلاق المنتج!"
    }
    
    if not client:
        return fallback_response

    prompt = f"""
    أنت خبير تسعير تجاري.
    حلل المنتج واقترح سعراً تنافسياً بالدولار وكود خصم:
    - اسم المنتج: {data.product_name}
    - التصنيف: {data.category}
    - الجمهور المستهدف: {data.target_audience}

    أرجع بصيغة JSON فقط:
    {{
        "suggested_price": 75,
        "price_min": 60,
        "price_max": 90,
        "reasoning": "تبرير اقتصادي موجز ومقنع في سطرين",
        "promo_code": "DEAL20",
        "promo_discount": "20%",
        "promo_message": "عرض ترويجي حصري"
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        return json.loads(clean_text.strip())
    except Exception:
        return fallback_response
    # نموذج طلب تحليل المراجعة
class ReviewAnalysisRequest(BaseModel):
    product_name: str
    review_text: str

@app.post("/analyze-review")
async def analyze_review(data: ReviewAnalysisRequest):
    """تحليل مشاعر المراجعة واستخراج الإيجابيات والسلبيات عبر الذكاء الاصطناعي"""
    fallback_response = {
        "sentiment": "إيجابي",
        "score": 85,
        "pros": ["جودة جيدة", "تجربة استخدام ممتازة"],
        "cons": ["لا توجد ملاحظات سلبية بارزة"],
        "summary": "مراجعة مشجعة تدل على رضا العميل عن المنتج."
    }
    
    if not client:
        return fallback_response

    prompt = f"""
    أنت خبير في تحليل مشاعر العملاء (Sentiment Analysis) ومعالجة اللغات الطبيعية NLP.
    حلل تقييم العميل التالي للمنتج:
    - المنتج: {data.product_name}
    - نص التقييم: "{data.review_text}"

    المطلوب استخراج:
    1. المشاعر: (إيجابي أو سلبي أو محايد)
    2. النسبة المئوية للرضا (score من 0 إلى 100)
    3. النقاط الإيجابية (pros: مصفوفة نصوص قصيرة)
    4. النقاط السلبية أو التحسينات (cons: مصفوفة نصوص قصيرة)
    5. ملخص تنفيذي للبائع في سطر واحد (summary)

    أجب بصيغة JSON فقط:
    {{
        "sentiment": "إيجابي",
        "score": 90,
        "pros": ["ميزة 1", "ميزة 2"],
        "cons": ["ملاحظة 1"],
        "summary": "ملخص سريع"
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        return json.loads(clean_text.strip())
    except Exception:
        return fallback_response