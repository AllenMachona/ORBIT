"""Populates the database with categories, an admin account, a demo
customer, and a handful of demo products so the shop isn't empty on first
run. Delete/replace the demo accounts and products before real use.

Run with: python seed.py
"""
from dotenv import load_dotenv
load_dotenv()

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.product import Category, Product  # noqa: E402

DEMO_PASSWORD = 'ChangeMe123!'

CATEGORIES = [
    ('phones', 'Phones'),
    ('laptops', 'Laptops'),
    ('accessories', 'Accessories'),
]

PRODUCTS = [
    dict(name='iPhone 12 128GB', brand='Apple', category='phones', condition='new',
         price=8500, specs='RAM: 4GB\nStorage: 128GB\nScreen: 6.1"', is_trending=True,
         description='Latest iPhone 12, brand new, sealed box.'),
    dict(name='iPhone 12 128GB', brand='Apple', category='phones', condition='refurbished',
         price=6200, specs='RAM: 4GB\nStorage: 128GB\nScreen: 6.1"', is_trending=True,
         description='Certified refurbished iPhone 12, fully tested, minor cosmetic wear possible.'),
    dict(name='Samsung Galaxy A54', brand='Samsung', category='phones', condition='new',
         price=4800, specs='RAM: 8GB\nStorage: 128GB\nScreen: 6.4"',
         description='Brand new Samsung Galaxy A54, great all-round mid-range phone.'),
    dict(name='HP Pavilion 15', brand='HP', category='laptops', condition='new',
         price=9200, specs='RAM: 8GB\nStorage: 512GB SSD\nCPU: Intel i5', is_trending=True,
         description='Reliable everyday laptop for coursework and browsing.'),
    dict(name='Dell Latitude 5490', brand='Dell', category='laptops', condition='refurbished',
         price=5400, specs='RAM: 8GB\nStorage: 256GB SSD\nCPU: Intel i5',
         description='Refurbished business laptop, tested and verified, great value.'),
    dict(name='Lenovo IdeaPad 3', brand='Lenovo', category='laptops', condition='new',
         price=6800, specs='RAM: 8GB\nStorage: 256GB SSD\nCPU: AMD Ryzen 5',
         description='Lightweight, fast, brand new laptop.'),
    dict(name='Wireless Earbuds Pro', brand='Generic', category='accessories', condition='new',
         price=650, specs='Bluetooth 5.0\nBattery: 20hrs with case', is_trending=True,
         description='Comfortable, reliable wireless earbuds with charging case.'),
    dict(name='65W USB-C Fast Charger', brand='Generic', category='accessories', condition='new',
         price=280, specs='Output: 65W\nUSB-C PD',
         description='Fast-charge your phone or laptop.'),
]


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        category_map = {}
        for slug, name in CATEGORIES:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                cat = Category(slug=slug, name=name)
                db.session.add(cat)
                db.session.flush()
            category_map[slug] = cat
        db.session.commit()

        if not User.query.filter_by(email='admin@orbittec.co.bw').first():
            admin = User(
                email='admin@orbittec.co.bw', first_name='OrbitTec', last_name='Admin',
                is_admin=True,
            )
            admin.set_password(DEMO_PASSWORD)
            db.session.add(admin)

        if not User.query.filter_by(email='student@example.com').first():
            customer = User(
                email='student@example.com', first_name='Thato', last_name='Kgosi',
                phone='71234567', campus='University of Botswana (UB)',
            )
            customer.set_password(DEMO_PASSWORD)
            db.session.add(customer)

        db.session.commit()

        for p in PRODUCTS:
            existing = Product.query.filter_by(name=p['name'], condition=p['condition']).first()
            if existing:
                continue
            db.session.add(Product(
                category_id=category_map[p['category']].id,
                name=p['name'], brand=p['brand'], condition=p['condition'],
                price=p['price'], specs=p['specs'], description=p['description'],
                is_trending=p.get('is_trending', False), is_preorder=True,
                stock_quantity=10, is_active=True,
            ))
        db.session.commit()

        print(f'Seed complete. Demo password for all accounts: {DEMO_PASSWORD}')
        print('Admin login: admin@orbittec.co.bw')
        print('Customer login: student@example.com')


if __name__ == '__main__':
    run()
