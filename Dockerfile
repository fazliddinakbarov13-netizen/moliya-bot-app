# 1. Frontend: React loyihasini qurish
FROM node:20 AS frontend-builder
WORKDIR /app/webapp
# Faqat package fayllarini nusxalaymiz (keshlash uchun)
COPY webapp/package*.json ./
RUN npm install
# Qolgan barcha fayllarni olamiz
COPY webapp/ ./
RUN npm run build

# 2. Backend: Python Bot va Web API xizmati
FROM python:3.11-slim
WORKDIR /app

# Kutubxonalarni o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Asosiy Python kodlarni tashlaymiz
COPY . .

# Oldingi qadamdan tayyor dist fayllarni Python muhitiga olib o'tamiz
COPY --from=frontend-builder /app/webapp/dist ./webapp/dist

# Web App porti (Aiohttp 8000)
EXPOSE 8000

# Loyihani avtomatik ishga tushirish
CMD ["python", "main.py"]
