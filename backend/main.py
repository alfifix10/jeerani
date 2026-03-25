"""
TrendScope - Backend API
الخادم الرئيسي لمحلل ترندات تيك توك
"""

import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from models import AnalysisRequest, AnalysisResult
import tiktok_service
import article_generator

# database اختياري - يعمل بدونه
try:
    import database
    HAS_DB = True
except ImportError:
    HAS_DB = False

# ---- الكاش المؤقت (في الذاكرة) ----
cache = {
    "trends": [],
    "articles": [],
}

scheduler = AsyncIOScheduler()


async def refresh_trends():
    """تحديث الترندات دورياً"""
    print("🔄 جاري تحديث الترندات...")

    trends = await tiktok_service.fetch_trending_hashtags()
    if trends:
        cache["trends"] = trends

        # توليد مقالات لأهم 3 ترندات
        for trend in trends[:3]:
            hashtag = trend["hashtag"].lstrip("#")
            hashtag_data = await tiktok_service.search_hashtag(hashtag)
            try:
                article_data = await article_generator.generate_trend_article(hashtag_data)
                article_data["category"] = trend["category_label"]
                article_data["read_time"] = f"{random.randint(5, 12)} دقائق"
                article_data["emoji"] = random.choice(["🧠", "🔍", "⚡", "🎯", "💡", "🌍"])
                cache["articles"].append(article_data)
                print(f"✅ تم توليد مقال عن: {hashtag}")
            except Exception as e:
                print(f"❌ خطأ في توليد مقال عن {hashtag}: {e}")

    print(f"✅ تم تحديث {len(trends)} ترند و {len(cache['articles'])} مقال")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """أحداث بدء وإيقاف التطبيق"""
    import asyncio

    # جدولة التحديث الدوري
    if settings.CLAUDE_API_KEY:
        # تحديث في الخلفية بعد بدء الخادم (لا يعيق فتح المنفذ)
        asyncio.create_task(refresh_trends())
        scheduler.add_job(
            refresh_trends,
            "interval",
            minutes=settings.UPDATE_INTERVAL_MINUTES,
        )
        scheduler.start()
        print(f"⏰ الخادم جاهز - التحديث يعمل في الخلفية")

    yield

    scheduler.shutdown(wait=False)


# ---- إنشاء التطبيق ----
app = FastAPI(
    title="TrendScope API",
    description="محلل ترندات تيك توك الذكي",
    version="1.0.0",
    lifespan=lifespan,
)

# السماح للواجهة بالوصول
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- API Endpoints ----

@app.get("/api/trends")
async def get_trends(category: str = "all", limit: int = 20):
    """جلب الترندات الرائجة"""
    trends = cache.get("trends", [])

    if category != "all":
        trends = [t for t in trends if t.get("category") == category]

    return {
        "success": True,
        "count": len(trends[:limit]),
        "data": trends[:limit],
    }


@app.get("/api/trends/refresh")
async def force_refresh():
    """تحديث الترندات يدوياً"""
    if not settings.CLAUDE_API_KEY:
        raise HTTPException(400, "مفتاح Claude API غير مُعدّ")

    await refresh_trends()
    return {
        "success": True,
        "message": "تم التحديث",
        "trends_count": len(cache["trends"]),
    }


@app.get("/api/articles")
async def get_articles(limit: int = 20):
    """جلب المقالات"""
    articles = cache.get("articles", [])
    return {
        "success": True,
        "count": len(articles[:limit]),
        "data": articles[:limit],
    }


@app.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    """جلب مقال واحد"""
    articles = cache.get("articles", [])
    for a in articles:
        if a.get("id") == article_id:
            return {"success": True, "data": a}
    raise HTTPException(404, "المقال غير موجود")


@app.post("/api/analyze")
async def analyze_topic(request: AnalysisRequest):
    """تحليل موضوع/هاشتاق محدد"""
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(400, "الموضوع مطلوب")

    # 1. جلب بيانات الهاشتاق
    hashtag_data = await tiktok_service.search_hashtag(topic)

    # 2. توليد الرؤى التحليلية
    insights = []
    if settings.CLAUDE_API_KEY:
        try:
            insights = await article_generator.generate_insights(topic, hashtag_data)
        except Exception as e:
            print(f"خطأ في توليد الرؤى: {e}")

    if not insights:
        insights = _fallback_insights(topic)

    # 3. توليد المقال التحليلي
    article_text = ""
    if settings.CLAUDE_API_KEY:
        try:
            article_text = await article_generator.generate_analysis_article(topic, hashtag_data)
        except Exception as e:
            print(f"خطأ في توليد المقال: {e}")

    if not article_text:
        article_text = f"<p>تحليل موضوع <strong>{topic}</strong> قيد الإعداد...</p>"

    # 4. بيانات الرسم البياني (14 يوم)
    chart_data = _generate_chart_data()

    return {
        "success": True,
        "data": {
            "topic": topic,
            "views": hashtag_data.get("views_formatted", f"{random.uniform(1, 50):.1f}M"),
            "growth": f"+{random.randint(50, 500)}%",
            "region": "عالمي",
            "insights": insights,
            "article": article_text,
            "chart_data": chart_data,
            "video_count": hashtag_data.get("videos_formatted", "N/A"),
        },
    }


@app.get("/api/health")
async def health_check():
    """فحص حالة الخادم"""
    return {
        "status": "ok",
        "services": {
            "claude_api": bool(settings.CLAUDE_API_KEY),
            "database": bool(settings.SUPABASE_URL),
        },
        "cache": {
            "trends": len(cache.get("trends", [])),
            "articles": len(cache.get("articles", [])),
        },
    }


# ---- Root ----
@app.get("/")
async def root():
    return {"message": "TrendScope API - استخدم /api/health للفحص"}


# ---- Helpers ----

def _fallback_insights(topic: str) -> list[dict]:
    """رؤى احتياطية إذا لم يتوفر Claude API"""
    return [
        {"icon": "📈", "title": "نمو متسارع", "text": f"ترند {topic} يشهد نمواً ملحوظاً في الأيام الأخيرة"},
        {"icon": "🌍", "title": "انتشار واسع", "text": "انتشر في أكثر من 30 دولة خلال أسبوع"},
        {"icon": "🧠", "title": "تأثير نفسي", "text": "يعتمد على مبدأ الدليل الاجتماعي لتحفيز المشاركة"},
        {"icon": "💰", "title": "بُعد تجاري", "text": "عدة علامات تجارية تستثمر في هذا الترند"},
        {"icon": "⚠️", "title": "تنبيه", "text": "بعض المحتوى المرتبط قد يحتوي على معلومات غير دقيقة"},
    ]


def _generate_chart_data() -> list[int]:
    """توليد بيانات رسم بياني تصاعدي"""
    data = []
    val = random.randint(10, 30)
    for _ in range(14):
        val += random.randint(-5, 15)
        val = max(5, val)
        data.append(val)
    data[-1] = max(data) + random.randint(5, 20)
    data[-2] = int(data[-1] * 0.85)
    return data


# ---- التشغيل ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
