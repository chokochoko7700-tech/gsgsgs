# Username qidiruv — Telegram bot + Mini App

Username bo'yicha 400+ saytdagi ochiq profillarni qidiradi.
Asos: [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock).

## Imkoniyatlar
- **Mini app**: natijalar topilishi bilan jonli chiqadi, filtr, hammasini nusxalash, Telegram mavzusiga moslashadi.
- **Bot**: `/search username` yoki shunchaki username yuborish.
- Telegram `initData` tekshiruvi, foydalanuvchi boshiga 1 ta qidiruv, umumiy parallel limit.

## Tuzilma
```
main.py             bot + web serverni birga ishga tushiradi
bot.py              Telegram handlerlar (aiogram 3)
web.py              mini app va /api/search (SSE oqim)
sherlock_runner.py  sherlock'ni ishga tushirish va natijani o'qish
auth.py             Mini App initData tekshiruvi
webapp/             mini app (HTML/CSS/JS)
```

## Lokal ishga tushirish
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # BOT_TOKEN va WEBAPP_URL ni yozing
python main.py
```
Mini app uchun HTTPS kerak — lokal sinovda `ngrok http 8080` va chiqqan manzilni `WEBAPP_URL` ga yozing.

## Render'ga joylash
1. Render → New → Blueprint → shu repo (`render.yaml` avtomatik o'qiladi).
2. `BOT_TOKEN` va `WEBAPP_URL` (`https://<servis>.onrender.com`) ni kiriting.
3. Deploy. Bot polling bilan ishlaydi, shuning uchun servis doim yoniq bo'lishi kerak (bepul tarif uxlab qoladi).

## Eslatma
Faqat ochiq (public) ma'lumot qidiriladi. O'zingiz yoki ruxsat bergan odamlar haqida, qonuniy maqsadda foydalaning.
