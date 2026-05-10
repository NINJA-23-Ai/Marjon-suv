# Marjon Suv Telegram Bot MVP

Marjon Suv — suv yetkazib berish xizmati uchun Telegram bot, Backend API va PostgreSQL asosidagi MVP loyiha.

## Imkoniyatlar

- Mijoz registratsiyasi: ism, telefon raqam va Telegram ID saqlanadi.
- Buyurtma berish jarayoni to'liq o'zbek tilida:
  1. mahsulot tanlash;
  2. miqdor tanlash;
  3. manzil yuborish;
  4. to'lov turini tanlash;
  5. buyurtmani tasdiqlash.
- Mahsulotlar:
  - 19L suv;
  - bo'sh idish almashtirish.
- Buyurtma statuslari: `NEW`, `ACCEPTED`, `DELIVERING`, `DELIVERED`, `CANCELED`.
- Yangi buyurtma haqida admin chatga Telegram xabarnoma yuboriladi.
- Admin statistikasi:
  - bugungi buyurtmalar soni;
  - bugungi tushum;
  - haftalik tushum;
  - oylik tushum.
- Backend API orqali health check, statistika va status yangilash endpointlari mavjud.

## Texnologiyalar

- Python 3.11+
- Aiogram 3
- FastAPI
- SQLAlchemy Async
- PostgreSQL
- Docker / Docker Compose

## Arxitektura

Loyiha clean architecture tamoyillariga yaqin tuzilgan:

```text
app/
  api/              # Backend API routerlari va dependency'lar
  bot/              # Telegram bot factory, handlerlar, keyboardlar, FSM state'lar
  config/           # Environment, logging, database sozlamalari
  middlewares/      # Bot middleware'lari
  models/           # SQLAlchemy ORM modellari
  repositories/     # Database query qatlamlari
  schemas/          # Pydantic validation schema'lari
  services/         # Business logic va integratsiya xizmatlari
```

Business logic `services` qatlamida, database query'lari `repositories` qatlamida, Telegram va HTTP kirish nuqtalari esa alohida saqlangan. Bu keyinchalik kuryer tizimi, CRM, to'lov modullari va dashboard qo'shishni osonlashtiradi.

## Environment variables

`.env.example` faylidan `.env` yarating:

```bash
cp .env.example .env
```

Asosiy sozlamalar:

| Variable | Tavsif |
| --- | --- |
| `BOT_TOKEN` | Telegram BotFather tokeni |
| `ADMIN_CHAT_ID` | Yangi buyurtmalar yuboriladigan admin chat ID |
| `ADMIN_IDS` | Admin Telegram ID ro'yxati, vergul bilan ajratiladi |
| `DATABASE_URL` | SQLAlchemy async PostgreSQL URL |
| `WATER_19L_PRICE` | 19L suv narxi |
| `EMPTY_BOTTLE_EXCHANGE_PRICE` | Bo'sh idish almashtirish narxi |


## Railway / Railpack orqali deploy qilish

Railpack build aniqlashi uchun root katalogda `railpack.json`, `runtime.txt`, `main.py` va executable `start.sh` mavjud. Railway/Railpack deployment uchun environment variable'larni sozlang va kerakli runtime rejimini tanlang:

- `APP_MODE=bot` — Telegram bot polling rejimida ishga tushadi. Bu default qiymat.
- `APP_MODE=api` — FastAPI server ishga tushadi va Railway beradigan `PORT` qiymatini ishlatadi.

Start command sifatida `./start.sh` ishlatiladi. Agar platformada start command qo'lda kiritilsa, aynan `./start.sh` qiymatini yozing.

## Docker orqali ishga tushirish

```bash
docker compose up --build
```

Bot `bot` service sifatida polling rejimida ishlaydi. API `http://localhost:8000` manzilida ochiladi.

## Lokal ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

API'ni alohida ishga tushirish:

```bash
uvicorn app.api.app:app --host 0.0.0.0 --port 8000
```

## API endpointlari

- `GET /api/health` — servis holati.
- `GET /api/admin/stats` — admin statistikasi.
- `PATCH /api/admin/orders/{order_id}/status?status=ACCEPTED` — buyurtma statusini yangilash.

## Eslatma

MVP tez ishga tushishi uchun jadval yaratish `Base.metadata.create_all` orqali bajariladi. Production bosqichida Alembic migratsiyalarini qo'shish tavsiya etiladi.
