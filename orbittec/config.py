import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-before-deployment'

    INSTANCE_FOLDER = os.path.join(basedir, 'instance')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(basedir, 'instance', 'orbittec.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB per upload — product photos, kept data-light per brief

    DEPOSIT_PERCENTAGE = float(os.environ.get('DEPOSIT_PERCENTAGE') or 0.50)
    PREORDER_LEAD_DAYS = int(os.environ.get('PREORDER_LEAD_DAYS') or 10)

    # Payment provider: 'mock' works out of the box for local testing — the
    # full checkout flow runs end to end without real credentials. Switch to
    # 'orange_money' / 'mascom_myzaka' / 'card' once you have merchant
    # credentials from those providers (see app/utils/payments.py).
    PAYMENT_PROVIDER = os.environ.get('PAYMENT_PROVIDER') or 'mock'

    ORANGE_MONEY_API_KEY = os.environ.get('ORANGE_MONEY_API_KEY', '')
    ORANGE_MONEY_MERCHANT_ID = os.environ.get('ORANGE_MONEY_MERCHANT_ID', '')
    MASCOM_MYZAKA_API_KEY = os.environ.get('MASCOM_MYZAKA_API_KEY', '')
    CARD_GATEWAY_PUBLIC_KEY = os.environ.get('CARD_GATEWAY_PUBLIC_KEY', '')
    CARD_GATEWAY_SECRET_KEY = os.environ.get('CARD_GATEWAY_SECRET_KEY', '')

    # Email — leave MAIL_SERVER blank to print emails to the console instead
    # of sending them, so order-confirmation/arrival emails work in dev
    # without real SMTP credentials.
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'orders@orbittec.co.bw'

    # SMS / WhatsApp — blank credentials mean messages print to the console
    # instead of sending, same pattern as email. Plug in Africa's Talking,
    # Twilio, or the WhatsApp Business API later without changing call sites.
    SMS_PROVIDER_API_KEY = os.environ.get('SMS_PROVIDER_API_KEY', '')
    WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')

    COMPANY_NAME = 'OrbitTec'
    COMPANY_TAGLINE = 'Where Innovation Meets Value'
