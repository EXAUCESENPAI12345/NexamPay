from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Currency


CURRENCIES = [
    {
        "code": "XAF",
        "name": "Franc CFA BEAC",
        "symbol": "FCFA",
        "decimals": 0,
    },
    {
        "code": "XOF",
        "name": "Franc CFA BCEAO",
        "symbol": "FCFA",
        "decimals": 0,
    },
    {
        "code": "AOA",
        "name": "Kwanza angolais",
        "symbol": "Kz",
        "decimals": 2,
    },
    {
        "code": "CDF",
        "name": "Franc congolais",
        "symbol": "FC",
        "decimals": 2,
    },
    {
        "code": "STN",
        "name": "Dobra",
        "symbol": "Db",
        "decimals": 2,
    },
    {
        "code": "GHS",
        "name": "Cedi ghanéen",
        "symbol": "GH₵",
        "decimals": 2,
    },
    {
        "code": "NGN",
        "name": "Naira nigérian",
        "symbol": "₦",
        "decimals": 2,
    },
    {
        "code": "GNF",
        "name": "Franc guinéen",
        "symbol": "FG",
        "decimals": 0,
    },
    {
        "code": "GMD",
        "name": "Dalasi gambien",
        "symbol": "D",
        "decimals": 2,
    },
    {
        "code": "LRD",
        "name": "Dollar libérien",
        "symbol": "$",
        "decimals": 2,
    },
    {
        "code": "SLE",
        "name": "Leone",
        "symbol": "Le",
        "decimals": 2,
    },
    {
        "code": "CVE",
        "name": "Escudo cap-verdien",
        "symbol": "$",
        "decimals": 2,
    },
    {
        "code": "MRU",
        "name": "Ouguiya mauritanien",
        "symbol": "UM",
        "decimals": 2,
    },

    # Afrique du Nord
    {
        "code": "DZD",
        "name": "Dinar algérien",
        "symbol": "دج",
        "decimals": 2,
    },
    {
        "code": "EGP",
        "name": "Livre égyptienne",
        "symbol": "E£",
        "decimals": 2,
    },
    {
        "code": "LYD",
        "name": "Dinar libyen",
        "symbol": "ل.د",
        "decimals": 3,
    },
    {
        "code": "MAD",
        "name": "Dirham marocain",
        "symbol": "DH",
        "decimals": 2,
    },
    {
        "code": "SDG",
        "name": "Livre soudanaise",
        "symbol": "ج.س",
        "decimals": 2,
    },
    {
        "code": "TND",
        "name": "Dinar tunisien",
        "symbol": "د.ت",
        "decimals": 3,
    },

    # Afrique australe
    {
        "code": "BWP",
        "name": "Pula botswanais",
        "symbol": "P",
        "decimals": 2,
    },
    {
        "code": "SZL",
        "name": "Lilangeni",
        "symbol": "E",
        "decimals": 2,
    },
    {
        "code": "LSL",
        "name": "Loti",
        "symbol": "L",
        "decimals": 2,
    },
    {
        "code": "MWK",
        "name": "Kwacha malawien",
        "symbol": "MK",
        "decimals": 2,
    },
    {
        "code": "MZN",
        "name": "Metical mozambicain",
        "symbol": "MT",
        "decimals": 2,
    },
    {
        "code": "NAD",
        "name": "Dollar namibien",
        "symbol": "$",
        "decimals": 2,
    },
    {
        "code": "ZAR",
        "name": "Rand sud-africain",
        "symbol": "R",
        "decimals": 2,
    },
    {
        "code": "ZMW",
        "name": "Kwacha zambien",
        "symbol": "ZK",
        "decimals": 2,
    },
    {
        "code": "ZWG",
        "name": "Zimbabwe Gold",
        "symbol": "ZiG",
        "decimals": 2,
    },

    # Afrique de l'Est
    {
        "code": "BIF",
        "name": "Franc burundais",
        "symbol": "FBu",
        "decimals": 0,
    },
    {
        "code": "DJF",
        "name": "Franc djiboutien",
        "symbol": "Fdj",
        "decimals": 0,
    },
    {
        "code": "ERN",
        "name": "Nakfa érythréen",
        "symbol": "Nfk",
        "decimals": 2,
    },
    {
        "code": "ETB",
        "name": "Birr éthiopien",
        "symbol": "Br",
        "decimals": 2,
    },
    {
        "code": "KES",
        "name": "Shilling kényan",
        "symbol": "KSh",
        "decimals": 2,
    },
    {
        "code": "MGA",
        "name": "Ariary malgache",
        "symbol": "Ar",
        "decimals": 2,
    },
    {
        "code": "MUR",
        "name": "Roupie mauricienne",
        "symbol": "₨",
        "decimals": 2,
    },
    {
        "code": "RWF",
        "name": "Franc rwandais",
        "symbol": "FRw",
        "decimals": 0,
    },
    {
        "code": "SCR",
        "name": "Roupie seychelloise",
        "symbol": "₨",
        "decimals": 2,
    },
    {
        "code": "SOS",
        "name": "Shilling somalien",
        "symbol": "Sh",
        "decimals": 2,
    },
    {
        "code": "SSP",
        "name": "Livre sud-soudanaise",
        "symbol": "£",
        "decimals": 2,
    },
    {
        "code": "TZS",
        "name": "Shilling tanzanien",
        "symbol": "TSh",
        "decimals": 2,
    },
    {
        "code": "UGX",
        "name": "Shilling ougandais",
        "symbol": "USh",
        "decimals": 0,
    },
]


async def seed_currencies(
    db: AsyncSession,
) -> None:

    for data in CURRENCIES:

        result = await db.execute(
            select(Currency)
            .where(
                Currency.code == data["code"]
            )
            .limit(1)
        )

        currency = (
            result.scalar_one_or_none()
        )

        if currency is None:
            db.add(
                Currency(**data)
            )
        else:
            currency.name = data["name"]
            currency.symbol = data["symbol"]
            currency.decimals = data["decimals"]
            currency.is_active = True

    await db.commit()