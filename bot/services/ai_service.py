"""AI service for expense categorization and financial advice using OpenAI."""

import json
import logging
from typing import Optional
from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def categorize_expense(
    text: str,
    categories: list[dict],
    lang: str = "uz",
) -> list[dict]:
    """Parse user's natural language expense text and categorize it.

    Args:
        text: User's message like "ovqatga 45000, transportga 12000 ketdi"
        categories: List of available categories [{"id": 1, "name": "Oziq-ovqat", "icon": "🍞"}, ...]
        lang: User's language

    Returns:
        List of parsed expenses: [{"category_id": 1, "category_name": "Oziq-ovqat", "icon": "🍞", "amount": 45000, "description": "ovqat"}]
    """
    # Build category list for the prompt
    cat_list = "\n".join(
        [f"- ID:{c['id']}, Nomi: {c['name']}, Icon: {c['icon']}" for c in categories]
    )

    system_prompt = f"""Sen O'zbek moliya yordamchisisisan. Foydalanuvchi xarajatlarini yozadi, sen ularni tahlil qilib, har bir xarajatni tegishli kategoriyaga ajratishing kerak.

Mavjud kategoriyalar:
{cat_list}

MUHIM QOIDALAR:
1. Foydalanuvchi matnidan barcha xarajatlarni ajrat
2. Har bir xarajatni tegishli kategoriyaga biriktir
3. Summani faqat raqam sifatida qaytar (vergul, probel, "so'm" so'zlarini olib tashla)
4. "kecha", "bugun", "ertaga" kabi so'zlarga e'tibor ber
5. Agar kategoriyani aniqlay olmasang, "Kutilmagan xarajatlar" ga qo'y
6. Javobni FAQAT JSON formatida qaytar

JAVOB FORMATI — har doim JSON object bo'lishi kerak:
{{"expenses": [
  {{"category_id": 1, "category_name": "Oziq-ovqat", "icon": "🍞", "amount": 45000, "description": "ovqat", "date_offset": 0}},
  {{"category_id": 8, "category_name": "Transport", "icon": "🚕", "amount": 12000, "description": "transport", "date_offset": 0}}
]}}

date_offset: 0 = bugun, -1 = kecha, 1 = ertaga
Agar summani aniqlay olmasang, amount: 0 qo'y.
Agar hech qanday xarajat topilmasa: {{"expenses": []}}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        logger.info(f"AI categorization response: {content}")

        # Parse JSON response
        parsed = json.loads(content)

        # Extract expenses from object
        if isinstance(parsed, dict):
            # Try common keys
            for key in ["expenses", "items", "result", "data"]:
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]
            # If it's a single expense item wrapped in object
            if "category_id" in parsed and "amount" in parsed:
                return [parsed]
        elif isinstance(parsed, list):
            return parsed

        logger.warning(f"Unexpected AI response format: {parsed}")
        return []

    except Exception as e:
        logger.error(f"AI categorization error: {e}")
        return []


async def get_financial_advice(
    expenses_by_category: list[dict],
    total_income: float,
    total_expenses: float,
    budget: float,
    currency: str = "UZS",
    lang: str = "uz",
) -> str:
    """Generate AI financial advice based on monthly data.

    Returns: Formatted advice text in user's language.
    """
    # Build expense summary
    expense_lines = []
    for cat in expenses_by_category:
        percent = (cat["total"] / total_income * 100) if total_income > 0 else 0
        expense_lines.append(
            f"- {cat['name']}: {cat['total']:,.0f} ({percent:.1f}%)"
        )

    expense_summary = "\n".join(expense_lines)
    balance = total_income - total_expenses
    savings_rate = ((balance / total_income) * 100) if total_income > 0 else 0

    system_prompt = """Sen O'zbek moliyaviy maslahatchi AI sisan. Foydalanuvchining oylik moliyaviy ma'lumotlarini tahlil qilib, KONKRET va FOYDALI maslahat ber.

Qoidalar:
1. O'zbek tilida yoz
2. Har bir kategoriya bo'yicha tahlil ber
3. Optimal ko'rsatkichlarni taqqosla (ovqat: 20-30%, transport: 5-10%, va h.k.)
4. Tejash bo'yicha 3-5 ta KONKRET tavsiya ber
5. Ijobiy va motivatsion ohangda yoz
6. Javob 500 so'zdan oshmasin
7. Emoji ishlat"""

    user_prompt = f"""Foydalanuvchining oylik ma'lumotlari:

Daromad: {total_income:,.0f} {currency}
Xarajat: {total_expenses:,.0f} {currency}
Qoldiq: {balance:,.0f} {currency}
Tejamkorlik: {savings_rate:.1f}%
Byudjet: {budget:,.0f} {currency}

Xarajatlar tafsiloti:
{expense_summary}

Iltimos, tahlil va maslahat ber."""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"AI advice error: {e}")
        if lang == "ru":
            return "❌ Не удалось получить совет от AI. Попробуйте позже."
        return "❌ AI maslahatini olishda xatolik. Keyinroq urinib ko'ring."
