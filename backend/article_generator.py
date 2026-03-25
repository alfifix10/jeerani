"""
توليد المقالات باستخدام Claude API
يحلل بيانات تيك توك ويكتب مقالات كاشفة للحقائق
"""

import anthropic
from config import settings

client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

SYSTEM_PROMPT = """أنت كاتب مقالات عربي محترف متخصص في تحليل ترندات تيك توك وكشف الحقائق المخفية.

أسلوبك:
- عناوين جذابة ومثيرة للفضول
- تكشف حقائق لا يعرفها أغلب الناس
- تستخدم أرقام وإحصائيات حقيقية
- تحلل الجانب النفسي والاجتماعي للترندات
- تحذر من المخاطر المخفية إن وجدت
- أسلوب سلس وممتع وليس أكاديمياً جافاً

التنسيق:
- استخدم HTML للتنسيق (h3, p, strong)
- أضف صناديق حقائق بهذا الشكل: <div class="fact-box">💡 حقيقة: ...</div>
- اجعل المقال 500-800 كلمة
- قسّم المقال لـ 4-5 أقسام واضحة"""


async def generate_trend_article(trend_data: dict) -> dict:
    """توليد مقال تحليلي عن ترند معين"""

    hashtag = trend_data.get("hashtag", "")
    views = trend_data.get("views_formatted", "N/A")
    video_count = trend_data.get("videos_formatted", "N/A")
    top_comments = trend_data.get("top_comments", [])

    comments_text = "\n".join(f"- {c}" for c in top_comments[:10]) if top_comments else "لا تتوفر تعليقات"

    prompt = f"""اكتب مقالاً تحليلياً عن ترند تيك توك التالي:

الهاشتاق: #{hashtag}
المشاهدات: {views}
عدد الفيديوهات: {video_count}

أهم التعليقات:
{comments_text}

المطلوب:
1. عنوان جذاب يثير الفضول
2. مقدمة تشد القارئ
3. 3-4 حقائق مخفية عن هذا الترند (تحليل نفسي، اجتماعي، تجاري)
4. تحذيرات أو نصائح
5. خاتمة قوية

أرجع النتيجة بهذا الشكل:
TITLE: [العنوان]
EXCERPT: [ملخص 1-2 سطر]
CONTENT: [المقال بتنسيق HTML]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    return _parse_article_response(response_text, hashtag)


async def generate_analysis_article(topic: str, hashtag_data: dict) -> str:
    """توليد مقال تحليلي سريع لأداة المحلل"""

    views = hashtag_data.get("views_formatted", "غير معروف")
    video_count = hashtag_data.get("videos_formatted", "غير معروف")
    comments = hashtag_data.get("top_comments", [])
    comments_text = "\n".join(f"- {c}" for c in comments[:10]) if comments else "لا تتوفر"

    prompt = f"""حلل هذا الترند من تيك توك واكتب تحليلاً موجزاً:

الموضوع: {topic}
المشاهدات: {views}
عدد الفيديوهات: {video_count}
أبرز التعليقات:
{comments_text}

اكتب تحليلاً بـ 300-400 كلمة يكشف:
1. لماذا انتشر هذا الترند (التحليل النفسي)
2. من يستفيد منه تجارياً
3. حقيقة صادمة عنه
4. نصيحة للمشاهد

استخدم تنسيق HTML (h3, p, strong). أضف صناديق حقائق."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


async def generate_insights(topic: str, hashtag_data: dict) -> list[dict]:
    """توليد رؤى تحليلية سريعة"""

    views = hashtag_data.get("view_count", 0)
    video_count = hashtag_data.get("video_count", 0)

    prompt = f"""حلل ترند "{topic}" على تيك توك وأعطني 5 رؤى تحليلية.
المشاهدات: {views}، الفيديوهات: {video_count}

لكل رؤية أعطني:
- أيقونة مناسبة (emoji واحد)
- عنوان قصير (3-5 كلمات)
- شرح موجز (سطر واحد)

أرجعها بالشكل:
ICON: [emoji]
TITLE: [عنوان]
TEXT: [شرح]
---"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_insights(message.content[0].text)


def _parse_article_response(text: str, hashtag: str) -> dict:
    """تحليل رد Claude واستخراج أجزاء المقال"""
    title = ""
    excerpt = ""
    content = ""

    lines = text.split("\n")
    mode = None

    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
            mode = None
        elif line.startswith("EXCERPT:"):
            excerpt = line.replace("EXCERPT:", "").strip()
            mode = None
        elif line.startswith("CONTENT:"):
            content = line.replace("CONTENT:", "").strip() + "\n"
            mode = "content"
        elif mode == "content":
            content += line + "\n"

    if not title:
        title = f"تحليل ترند #{hashtag} - حقائق لا يعرفها أغلب الناس"
    if not excerpt:
        excerpt = f"تحليل معمق لترند #{hashtag} يكشف الحقائق المخفية وراء انتشاره"
    if not content:
        content = text

    return {
        "title": title,
        "excerpt": excerpt,
        "content": content.strip(),
        "trend_hashtag": hashtag,
    }


def _parse_insights(text: str) -> list[dict]:
    """تحليل الرؤى من رد Claude"""
    insights = []
    current = {}

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("ICON:"):
            current["icon"] = line.replace("ICON:", "").strip()
        elif line.startswith("TITLE:"):
            current["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("TEXT:"):
            current["text"] = line.replace("TEXT:", "").strip()
        elif line == "---" and current:
            if all(k in current for k in ("icon", "title", "text")):
                insights.append(current)
            current = {}

    if current and all(k in current for k in ("icon", "title", "text")):
        insights.append(current)

    return insights[:5]
