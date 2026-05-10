# Marjon Suv Telegram Bot MVP

Marjon Suv — suv yetkazib berish xizmati uchun Telegram bot, Backend API va PostgreSQL asosidagi MVP loyiha.

## Imkoniyatlar

- Mijoz registratsiyasi: ism, telefon raqam va Telegram ID saqlanadi.
- Buyurtma berish jarayoni to'liq o'zbek tilida:
  1. mahsulot tanlash;
  2. miqdor tanlash;
  3. manzil yuborish;
  4. joylashuv yuborish yoki o'tkazib yuborish;
  5. qo'shimcha izoh yozish;
  6. to'lov turini tanlash;
  7. buyurtmani tasdiqlash.
- Mahsulotlar:
  - 19L suv;
  - bo'sh idish almashtirish.
- Buyurtma statuslari: `NEW`, `ACCEPTED`, `DELIVERING`, `DELIVERED`, `CANCELED`.
- Yangi buyurtma haqida admin chatga Telegram xabarnoma yuboriladi.
- Admin panel:
  - barcha buyurtmalarni ko'rish;
  - buyurtmani qabul qilish yoki rad etish;
  - buyurtmachi ma'lumotlarini ko'rish;
  - kuryer tayinlash;
  - bugungi buyurtmalar soni, bugungi/haftalik/oylik tushum.
- Kuryer paneli:
  - o'ziga biriktirilgan buyurtmalarni ko'rish;
  - mijoz ma'lumotlarini olish;
  - buyurtmani `DELIVERING` va `DELIVERED` statuslariga o'tkazish.
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
| `COURIER_IDS` | Default kuryer Telegram ID ro'yxati, vergul bilan ajratiladi |
| `DATABASE_URL` | PostgreSQL connection string. `postgres://`, `postgresql://` yoki `postgresql+asyncpg://` qabul qilinadi; app async driverga avtomatik moslaydi. |
| `WATER_19L_PRICE` | 19L suv narxi |
| `EMPTY_BOTTLE_EXCHANGE_PRICE` | Bo'sh idish almashtirish narxi |



> Agar `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL` xatosi chiqsa, `DATABASE_URL` qiymati to'liq PostgreSQL connection string emas yoki noto'g'ri ko'chirilgan bo'ladi. Railway'da odatda PostgreSQL plugin yaratib, uning `DATABASE_URL` qiymatini aynan shu nom bilan service variable sifatida ulang.

## Railway / Railpack orqali deploy qilish

Railpack build aniqlashi uchun root katalogda `railpack.json`, `runtime.txt`, `main.py` va executable `start.sh` mavjud. Railway/Railpack deployment uchun environment variable'larni sozlang va kerakli runtime rejimini tanlang:

- `APP_MODE=bot` — Telegram bot polling rejimida ishga tushadi. Bu default qiymat.
- `APP_MODE=api` — FastAPI server ishga tushadi va Railway beradigan `PORT` qiymatini ishlatadi.

Bot startup vaqtida `delete_webhook(drop_pending_updates=True)` chaqiriladi va polling faqat yangi instance orqali boshlanadi. Start command sifatida `./start.sh` ishlatiladi. Agar platformada start command qo'lda kiritilsa, aynan `./start.sh` qiymatini yozing.

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
