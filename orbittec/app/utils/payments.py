"""Pluggable payment provider abstraction. Every provider implements the
same interface: charge(amount, payer_identifier, order_reference) ->
PaymentResult. Checkout code never talks to a specific gateway directly —
switching from mock to real is a one-line config change, not a rewrite.

MockPaymentProvider always succeeds instantly (default: PAYMENT_PROVIDER=
mock) — this is what lets the full checkout flow work today without real
merchant credentials. NEVER use it in production.

OrangeMoneyProvider / MascomMyZakaProvider / CardProvider are stubs that
raise NotImplementedError explaining exactly what real credentials are
needed — implementing them requires signing up with that provider.
"""
from dataclasses import dataclass
from flask import current_app


@dataclass
class PaymentResult:
    success: bool
    provider_reference: str = ''
    failure_reason: str = ''


class PaymentProvider:
    def charge(self, amount, payer_identifier, order_reference):
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    def charge(self, amount, payer_identifier, order_reference):
        import secrets
        return PaymentResult(success=True, provider_reference=f'MOCK-{secrets.token_hex(6).upper()}')


class OrangeMoneyProvider(PaymentProvider):
    def charge(self, amount, payer_identifier, order_reference):
        raise NotImplementedError(
            'Orange Money integration requires real merchant credentials from Orange Botswana. '
            'Set PAYMENT_PROVIDER=mock for testing until those are available.'
        )


class MascomMyZakaProvider(PaymentProvider):
    def charge(self, amount, payer_identifier, order_reference):
        raise NotImplementedError(
            'Mascom MyZaka integration requires real merchant credentials from Mascom. '
            'Set PAYMENT_PROVIDER=mock for testing until those are available.'
        )


class CardProvider(PaymentProvider):
    def charge(self, amount, payer_identifier, order_reference):
        raise NotImplementedError(
            'Card gateway integration requires real API keys from a payment processor '
            '(e.g. DPO Group). Set PAYMENT_PROVIDER=mock for testing until those are available.'
        )


PROVIDERS = {
    'mock': MockPaymentProvider,
    'orange_money': OrangeMoneyProvider,
    'mascom_myzaka': MascomMyZakaProvider,
    'card': CardProvider,
}


def get_provider(method=None):
    key = method or current_app.config.get('PAYMENT_PROVIDER', 'mock')
    provider_class = PROVIDERS.get(key, MockPaymentProvider)
    return provider_class()
