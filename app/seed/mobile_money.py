from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Country, MobileMoneyNetwork


# Initial catalog for the principal NexamPay markets. The catalog is deliberately
# small and uses only providers that have been verified for the listed markets.
NETWORKS = {
    "CM": [
        ("MTN", "MTN Mobile Money"),
        ("ORANGE", "Orange Money"),
    ],
    "CD": [
        ("AIRTEL", "Airtel Money"),
        ("AFRIMONEY", "Afrimoney"),
        ("ORANGE", "Orange Money"),
        ("MPESA", "Vodacom M-Pesa"),
    ],
    "GA": [
        ("AIRTEL", "Airtel Money"),
        ("MOOV", "Moov Money"),
    ],
    "TD": [
        ("AIRTEL", "Airtel Money"),
        ("MOOV", "Moov Money"),
    ],
    "BJ": [
        ("MTN", "MTN Mobile Money / MoMo"),
        ("MOOV", "Moov Money"),
        ("CELTIIS", "Celtiis Cash"),
    ],
    "BF": [
        ("ORANGE", "Orange Money Burkina Faso"),
    ],
    "CI": [
        ("MOOV", "Moov Money Côte d'Ivoire"),
        ("MTN", "MTN Mobile Money Côte d'Ivoire"),
        ("ORANGE", "Orange Money Côte d'Ivoire"),
    ],
    "ML": [
        ("ORANGE", "Orange Money Mali"),
        ("SAMA", "Sama Money"),
    ],
    "SN": [
        ("MOBILE_CASH", "Mobile Cash"),
        ("ORANGE", "Orange Money"),
        ("QUICKPAY", "QuickPay"),
        ("WAVE", "Wave"),
    ],
    "TG": [
        ("TMONEY", "TMoney"),
    ],
    "CG": [
        ("AIRTEL", "Airtel Money"),
    ],
}


async def seed_mobile_money_networks(db: AsyncSession) -> None:
    for country_code, networks in NETWORKS.items():
        country_result = await db.execute(
            select(Country).where(Country.code == country_code).limit(1)
        )
        country = country_result.scalar_one_or_none()
        if country is None:
            continue

        for code, name in networks:
            result = await db.execute(
                select(MobileMoneyNetwork)
                .where(
                    MobileMoneyNetwork.country_id == country.id,
                    MobileMoneyNetwork.code == code,
                )
                .limit(1)
            )
            network = result.scalar_one_or_none()
            if network is None:
                db.add(
                    MobileMoneyNetwork(
                        country_id=country.id,
                        code=code,
                        name=name,
                        currency_code=country.currency_code,
                        is_active=True,
                    )
                )
            else:
                network.name = name
                network.currency_code = country.currency_code
                network.is_active = True

    await db.commit()
