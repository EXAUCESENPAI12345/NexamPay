from decimal import Decimal, ROUND_HALF_UP

from app.config import settings


CENT = Decimal("0.01")


def calculate_fee(amount: Decimal) -> Decimal:
    amount = Decimal(amount)

    if amount <= Decimal(settings.fee_free_limit):
        return Decimal("0.00")

    fee = (
        amount
        * Decimal(settings.fee_percent)
        / Decimal("100")
    )

    return fee.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def calculate_total(
    amount: Decimal,
) -> tuple[Decimal, Decimal]:
    amount = Decimal(amount)

    fee = calculate_fee(amount)
    total = (amount + fee).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )

    return fee, total