# OrbitTec — Pre-Order Electronics Storefront

Flask + SQLAlchemy e-commerce platform for pre-ordering phones, laptops,
and accessories, with a 50% deposit checkout model, order status tracking,
and an admin dashboard.

## What's built and genuinely working

- **Accounts** — signup/login with hashed passwords, campus selection.
- **Catalog** — phones/laptops/accessories, filterable by category and
  condition (New vs. Refurbished), search. New and Refurbished units of
  the "same model" are separate listings with independent prices, exactly
  as the brief asked for.
- **Cart & checkout** — automatic 50% deposit calculation, delivery method
  (campus collection or delivery) with address capture, order confirmation.
- **Order tracking** — Pending → Deposit Paid → Arrived → Delivered, with
  a visual progress tracker on the customer's order page.
- **Admin dashboard** — order list with status filters, revenue-collected
  total, and the core requested action: **"Mark as Arrived"**, which
  automatically fires a customer notification (email + SMS) telling them
  to pay the balance and arrange collection.
- **Balance payment** — once an order is marked arrived, the customer gets
  a "Pay Balance" button on their order page, using the same payment
  abstraction as the deposit.
- **Product management** — add/edit/hide products, image upload, mark
  items as trending for the homepage.
- Mobile-first, lightweight Bootstrap 5 layout — no heavy JS frameworks,
  lazy-loaded images.

## Honest limitations — read before going live

**Payments**: `PAYMENT_PROVIDER=mock` is the default, and it's what makes
the entire checkout flow (including balance payment) work end-to-end
today. It always succeeds and does not move real money. Real Orange
Money, Mascom MyZaka, and card gateway integrations require merchant
credentials from those providers that no one can generate for you — see
`app/utils/payments.py` for exactly what each one needs. The abstraction
is built so plugging in real credentials later is a contained change in
that one file, not a rewrite.

**SMS / WhatsApp**: same pattern. Without real provider credentials
(`SMS_PROVIDER_API_KEY` / `WHATSAPP_API_TOKEN`), messages print to the
console instead of sending — you'll see every notification in your
terminal while testing. Email works for real if you configure SMTP.

**Not built**: CSRF protection, rate limiting, and other production
security hardening weren't in scope for this pass — see the EBMS
project's `SECURITY-CHECKLIST.md` pattern if you want the same kind of
explicit pre-go-live list built for this project too, just ask.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Generate a real `SECRET_KEY` (any long random string) and put it in `.env`.
Everything else in `.env.example` has safe defaults — SQLite database,
mock payments, console-fallback notifications — so you can run it exactly
as-is for local testing.

```bash
python seed.py     # creates categories, admin + demo customer, demo products
python run.py       # starts on http://localhost:5000
```

### Demo accounts (password for both: `ChangeMe123!`)

| Email | Role |
|---|---|
| `admin@orbittec.co.bw` | Admin (dashboard + product management) |
| `student@example.com` | Customer |

### Suggested walkthrough

1. Log in as `student@example.com`, browse the shop, add an item to cart,
   check out (deposit auto-calculated at 50%, "Test Payment" method
   completes instantly).
2. Log in as `admin@orbittec.co.bw` in another browser/incognito window,
   go to the Admin Dashboard, open the order, click **"Mark as Arrived"**
   — watch your terminal for the email/SMS notification that fires.
3. Back as the customer, open the order — a "Pay Balance" button now
   appears. Pay it (again via Test Payment).
4. Back as admin, **"Mark as Delivered"** becomes available once the
   balance is paid.

## Project structure

```
orbittec/
  app/
    __init__.py          app factory
    extensions.py         db, login_manager, migrate
    models/                User, Category/Product, CartItem, Order/OrderItem, Payment, NotificationLog
    routes/                 auth, shop, cart, checkout, account, admin, pages
    templates/                base.html + one template per page
    static/css/styles.css      OrbitTec branding
    utils/
      payments.py             pluggable payment provider abstraction
      notify.py                 email/SMS/WhatsApp with console fallback
  config.py
  run.py
  seed.py
  requirements.txt
  .env.example
```
