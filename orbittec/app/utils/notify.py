"""Customer notifications across email, SMS, and WhatsApp. Every send is
logged to NotificationLog regardless of channel or whether it actually
went out over a real provider. Email works for real if MAIL_SERVER is
configured; otherwise it prints to console. SMS/WhatsApp are stubs that
print to console until real provider credentials are configured."""
from flask import current_app
from app.extensions import db
from app.models.notification import NotificationLog


def send_email(to_address, subject, body):
    server = current_app.config.get('MAIL_SERVER')
    if not server:
        print(f"[EMAIL — console fallback, MAIL_SERVER not configured]\nTo: {to_address}\nSubject: {subject}\n{body}\n")
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_address

        with smtplib.SMTP(server, current_app.config['MAIL_PORT']) as smtp:
            if current_app.config.get('MAIL_USE_TLS'):
                smtp.starttls()
            if current_app.config.get('MAIL_USERNAME'):
                smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"Email send failed (non-fatal): {exc}")
        return False


def send_sms(to_phone, message):
    api_key = current_app.config.get('SMS_PROVIDER_API_KEY')
    if not api_key:
        print(f"[SMS — console fallback, no SMS provider configured]\nTo: {to_phone}\n{message}\n")
        return False
    print(f"[SMS — provider configured but not implemented yet]\nTo: {to_phone}\n{message}\n")
    return False


def send_whatsapp(to_phone, message):
    token = current_app.config.get('WHATSAPP_API_TOKEN')
    if not token:
        print(f"[WHATSAPP — console fallback, no WhatsApp Business API token configured]\nTo: {to_phone}\n{message}\n")
        return False
    print(f"[WHATSAPP — token configured but not implemented yet]\nTo: {to_phone}\n{message}\n")
    return False


def notify_order(order, subject, message, channels=('email', 'sms')):
    customer = order.customer

    for channel in channels:
        delivered = False
        if channel == 'email' and customer.email:
            delivered = send_email(customer.email, subject, message)
        elif channel == 'sms' and customer.phone:
            delivered = send_sms(customer.phone, message)
        elif channel == 'whatsapp' and customer.phone:
            delivered = send_whatsapp(customer.phone, message)
        else:
            continue

        db.session.add(NotificationLog(order_id=order.id, channel=channel, message=message, delivered=delivered))

    db.session.commit()
