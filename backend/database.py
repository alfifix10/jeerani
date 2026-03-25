"""
خدمة قاعدة البيانات - Supabase
تخزين الترندات والمقالات المولّدة
"""

from datetime import datetime, timezone
from supabase import create_client
from config import settings

supabase = None


def get_db():
    """الحصول على اتصال قاعدة البيانات"""
    global supabase
    if supabase is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase


# ============ الترندات ============

async def save_trends(trends: list[dict]) -> bool:
    """حفظ الترندات في قاعدة البيانات"""
    db = get_db()
    if not db:
        return False
    try:
        now = datetime.now(timezone.utc).isoformat()
        for trend in trends:
            trend["fetched_at"] = now

        db.table("trends").upsert(
            trends, on_conflict="hashtag"
        ).execute()
        return True
    except Exception as e:
        print(f"خطأ في حفظ الترندات: {e}")
        return False


async def get_saved_trends(limit: int = 20) -> list[dict]:
    """جلب الترندات المحفوظة"""
    db = get_db()
    if not db:
        return []
    try:
        result = db.table("trends") \
            .select("*") \
            .order("rank") \
            .limit(limit) \
            .execute()
        return result.data
    except Exception as e:
        print(f"خطأ في جلب الترندات: {e}")
        return []


# ============ المقالات ============

async def save_article(article: dict) -> bool:
    """حفظ مقال في قاعدة البيانات"""
    db = get_db()
    if not db:
        return False
    try:
        article["created_at"] = datetime.now(timezone.utc).isoformat()
        db.table("articles").insert(article).execute()
        return True
    except Exception as e:
        print(f"خطأ في حفظ المقال: {e}")
        return False


async def get_articles(limit: int = 20) -> list[dict]:
    """جلب المقالات"""
    db = get_db()
    if not db:
        return []
    try:
        result = db.table("articles") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data
    except Exception as e:
        print(f"خطأ في جلب المقالات: {e}")
        return []


async def get_article_by_id(article_id: str) -> dict | None:
    """جلب مقال بالـ ID"""
    db = get_db()
    if not db:
        return None
    try:
        result = db.table("articles") \
            .select("*") \
            .eq("id", article_id) \
            .single() \
            .execute()
        return result.data
    except Exception as e:
        print(f"خطأ في جلب المقال: {e}")
        return None


# ============ إنشاء الجداول ============

SETUP_SQL = """
-- جدول الترندات
CREATE TABLE IF NOT EXISTS trends (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    rank INTEGER,
    title TEXT,
    hashtag TEXT UNIQUE,
    description TEXT,
    category TEXT,
    category_label TEXT,
    views TEXT,
    likes TEXT,
    shares TEXT,
    comments TEXT DEFAULT '0',
    growth TEXT,
    growth_up BOOLEAN DEFAULT true,
    video_count INTEGER DEFAULT 0,
    region TEXT DEFAULT 'عالمي',
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- جدول المقالات
CREATE TABLE IF NOT EXISTS articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    excerpt TEXT,
    content TEXT,
    category TEXT,
    read_time TEXT,
    trend_hashtag TEXT,
    emoji TEXT DEFAULT '📝',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- فهرس للبحث السريع
CREATE INDEX IF NOT EXISTS idx_trends_hashtag ON trends(hashtag);
CREATE INDEX IF NOT EXISTS idx_articles_hashtag ON articles(trend_hashtag);
"""


def print_setup_instructions():
    """طباعة تعليمات إنشاء الجداول"""
    print("=" * 50)
    print("لإنشاء الجداول في Supabase:")
    print("1. افتح https://supabase.com/dashboard")
    print("2. اذهب إلى SQL Editor")
    print("3. انسخ والصق الكود التالي:")
    print("=" * 50)
    print(SETUP_SQL)
