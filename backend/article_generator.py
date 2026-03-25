"""
توليد مقالات ساخنة وكاشفة باستخدام Claude API
"""

import anthropic
from config import settings

SYSTEM_PROMPT = """أنت صحفي تحقيقات متخصص في كشف الحقائق المخفية وراء الأحداث الساخنة والترندات.

أسلوبك:
- عناوين صادمة ومثيرة تجعل القارئ لا يستطيع التوقف عن القراءة
- تكشف ما لا يعرفه 99% من الناس
- تذكر أسماء وتفاصيل حقيقية
- تستخدم أسلوب "ما لا يريدونك أن تعرفه"
- تربط الأحداث ببعضها بطريقة ذكية
- تحلل الدوافع المالية والنفسية الخفية
- تحذر الناس من المخاطر الحقيقية

التنسيق:
- استخدم HTML: h3, p, strong
- أضف صناديق حقائق صادمة: <div class="fact-box">🔥 حقيقة صادمة: ...</div>
- اجعل المقال 600-900 كلمة
- 5-6 أقسام، كل قسم يكشف حقيقة جديدة
- ابدأ بجملة صادمة تشد القارئ فوراً"""


def _get_client():
    return anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)


async def generate_trend_article(trend_data: dict) -> dict:
    """توليد مقال ساخن عن ترند"""
    client = _get_client()
    hashtag = trend_data.get("hashtag", "")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"""اكتب مقالاً ساخناً وكاشفاً عن هذا الموضوع: #{hashtag}

المطلوب:
1. عنوان صادم يجذب النقر (clickbait ذكي لكن صادق)
2. مقدمة تبدأ بحقيقة صادمة
3. اكشف 4-5 حقائق مخفية عن هذا الموضوع:
   - من يستفيد مادياً؟
   - ما القصة الحقيقية التي لا يعرفها أحد؟
   - ما المخاطر المخفية؟
   - ما علاقة هذا بأحداث أكبر؟
4. خاتمة تحذيرية أو كاشفة

اجعل المقال يشعر القارئ أنه اكتشف شيئاً لا يعرفه أحد.

أرجع بالشكل:
TITLE: [عنوان صادم]
EXCERPT: [سطرين يثيران الفضول]
CONTENT: [المقال بـ HTML]"""}],
    )

    return _parse_response(message.content[0].text, hashtag)


async def generate_analysis_article(topic: str, hashtag_data: dict) -> str:
    """مقال تحليلي سريع لأداة المحلل"""
    client = _get_client()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"""حلل هذا الموضوع الساخن: {topic}

اكتب تحليلاً بـ 400-500 كلمة يكشف:
1. القصة الحقيقية وراء هذا الموضوع
2. من يستفيد ومن يتضرر
3. حقائق صادمة لا يعرفها أغلب الناس
4. لماذا انتشر بهذه السرعة (التحليل النفسي)
5. تحذير أو نصيحة للقارئ

استخدم HTML (h3, p, strong). أضف صناديق حقائق صادمة."""}],
    )

    return message.content[0].text


async def generate_insights(topic: str, hashtag_data: dict) -> list[dict]:
    """رؤى تحليلية سريعة"""
    client = _get_client()

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": f"""حلل "{topic}" وأعطني 5 رؤى صادمة.

لكل رؤية:
ICON: [emoji]
TITLE: [عنوان قصير صادم]
TEXT: [حقيقة مخفية بسطر واحد]
---"""}],
    )

    return _parse_insights(message.content[0].text)


def _parse_response(text: str, hashtag: str) -> dict:
    title = ""
    excerpt = ""
    content = ""
    mode = None

    for line in text.split("\n"):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("EXCERPT:"):
            excerpt = line.replace("EXCERPT:", "").strip()
        elif line.startswith("CONTENT:"):
            content = line.replace("CONTENT:", "").strip() + "\n"
            mode = "content"
        elif mode == "content":
            content += line + "\n"

    return {
        "title": title or f"الحقيقة الصادمة وراء #{hashtag}",
        "excerpt": excerpt or f"ما لا يعرفه أحد عن #{hashtag} - تحقيق كاشف",
        "content": content.strip() or text,
        "trend_hashtag": hashtag,
    }


def _parse_insights(text: str) -> list[dict]:
    insights = []
    current = {}
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("ICON:"): current["icon"] = line.replace("ICON:", "").strip()
        elif line.startswith("TITLE:"): current["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("TEXT:"): current["text"] = line.replace("TEXT:", "").strip()
        elif line == "---" and current.get("title"):
            insights.append(current)
            current = {}
    if current.get("title"):
        insights.append(current)
    return insights[:5]
