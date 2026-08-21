from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Country


COUNTRIES = [

    # ==========================================================
    # AFRIQUE CENTRALE
    # ==========================================================

    {
        "code": "CM",
        "name": "Cameroun",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "CM",
    },
    {
        "code": "CF",
        "name": "République centrafricaine",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "CF",
    },
    {
        "code": "TD",
        "name": "Tchad",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "TD",
    },
    {
        "code": "CG",
        "name": "Congo",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "CG",
    },
    {
        "code": "CD",
        "name": "République démocratique du Congo",
        "region": "CENTRAL",
        "currency_code": "CDF",
        "flag_code": "CD",
    },
    {
        "code": "GQ",
        "name": "Guinée équatoriale",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "GQ",
    },
    {
        "code": "GA",
        "name": "Gabon",
        "region": "CENTRAL",
        "currency_code": "XAF",
        "flag_code": "GA",
    },
    {
        "code": "ST",
        "name": "São Tomé-et-Príncipe",
        "region": "CENTRAL",
        "currency_code": "STN",
        "flag_code": "ST",
    },

    # ==========================================================
    # AFRIQUE DE L'OUEST
    # ==========================================================

    {
        "code": "BJ",
        "name": "Bénin",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "BJ",
    },
    {
        "code": "BF",
        "name": "Burkina Faso",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "BF",
    },
    {
        "code": "CV",
        "name": "Cap-Vert",
        "region": "WEST",
        "currency_code": "CVE",
        "flag_code": "CV",
    },
    {
        "code": "CI",
        "name": "Côte d'Ivoire",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "CI",
    },
    {
        "code": "GM",
        "name": "Gambie",
        "region": "WEST",
        "currency_code": "GMD",
        "flag_code": "GM",
    },
    {
        "code": "GH",
        "name": "Ghana",
        "region": "WEST",
        "currency_code": "GHS",
        "flag_code": "GH",
    },
    {
        "code": "GN",
        "name": "Guinée",
        "region": "WEST",
        "currency_code": "GNF",
        "flag_code": "GN",
    },
    {
        "code": "GW",
        "name": "Guinée-Bissau",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "GW",
    },
    {
        "code": "LR",
        "name": "Liberia",
        "region": "WEST",
        "currency_code": "LRD",
        "flag_code": "LR",
    },
    {
        "code": "ML",
        "name": "Mali",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "ML",
    },
    {
        "code": "MR",
        "name": "Mauritanie",
        "region": "WEST",
        "currency_code": "MRU",
        "flag_code": "MR",
    },
    {
        "code": "NE",
        "name": "Niger",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "NE",
    },
    {
        "code": "NG",
        "name": "Nigeria",
        "region": "WEST",
        "currency_code": "NGN",
        "flag_code": "NG",
    },
    {
        "code": "SN",
        "name": "Sénégal",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "SN",
    },
    {
        "code": "SL",
        "name": "Sierra Leone",
        "region": "WEST",
        "currency_code": "SLE",
        "flag_code": "SL",
    },
    {
        "code": "TG",
        "name": "Togo",
        "region": "WEST",
        "currency_code": "XOF",
        "flag_code": "TG",
    },

    # ==========================================================
    # AFRIQUE DU NORD
    # ==========================================================

    {
        "code": "DZ",
        "name": "Algérie",
        "region": "NORTH",
        "currency_code": "DZD",
        "flag_code": "DZ",
    },
    {
        "code": "EG",
        "name": "Égypte",
        "region": "NORTH",
        "currency_code": "EGP",
        "flag_code": "EG",
    },
    {
        "code": "LY",
        "name": "Libye",
        "region": "NORTH",
        "currency_code": "LYD",
        "flag_code": "LY",
    },
    {
        "code": "MA",
        "name": "Maroc",
        "region": "NORTH",
        "currency_code": "MAD",
        "flag_code": "MA",
    },
    {
        "code": "SD",
        "name": "Soudan",
        "region": "NORTH",
        "currency_code": "SDG",
        "flag_code": "SD",
    },
    {
        "code": "TN",
        "name": "Tunisie",
        "region": "NORTH",
        "currency_code": "TND",
        "flag_code": "TN",
    },

    # ==========================================================
    # AFRIQUE AUSTRALE
    # ==========================================================

    {
        "code": "BW",
        "name": "Botswana",
        "region": "SOUTH",
        "currency_code": "BWP",
        "flag_code": "BW",
    },
    {
        "code": "SZ",
        "name": "Eswatini",
        "region": "SOUTH",
        "currency_code": "SZL",
        "flag_code": "SZ",
    },
    {
        "code": "LS",
        "name": "Lesotho",
        "region": "SOUTH",
        "currency_code": "LSL",
        "flag_code": "LS",
    },
    {
        "code": "MW",
        "name": "Malawi",
        "region": "SOUTH",
        "currency_code": "MWK",
        "flag_code": "MW",
    },
    {
        "code": "MZ",
        "name": "Mozambique",
        "region": "SOUTH",
        "currency_code": "MZN",
        "flag_code": "MZ",
    },
    {
        "code": "NA",
        "name": "Namibie",
        "region": "SOUTH",
        "currency_code": "NAD",
        "flag_code": "NA",
    },
    {
        "code": "ZA",
        "name": "Afrique du Sud",
        "region": "SOUTH",
        "currency_code": "ZAR",
        "flag_code": "ZA",
    },
    {
        "code": "ZM",
        "name": "Zambie",
        "region": "SOUTH",
        "currency_code": "ZMW",
        "flag_code": "ZM",
    },
    {
        "code": "ZW",
        "name": "Zimbabwe",
        "region": "SOUTH",
        "currency_code": "ZWG",
        "flag_code": "ZW",
    },
    {
    "code": "AO",
    "name": "Angola",
    "region": "SOUTH",
    "currency_code": "AOA",
    "flag_code": "AO",
},
    


    # ==========================================================
    # AFRIQUE DE L'EST
    # ==========================================================

    {
        "code": "BI",
        "name": "Burundi",
        "region": "EAST",
        "currency_code": "BIF",
        "flag_code": "BI",
    },
    {
        "code": "DJ",
        "name": "Djibouti",
        "region": "EAST",
        "currency_code": "DJF",
        "flag_code": "DJ",
    },
    {
        "code": "ER",
        "name": "Érythrée",
        "region": "EAST",
        "currency_code": "ERN",
        "flag_code": "ER",
    },
    {
        "code": "ET",
        "name": "Éthiopie",
        "region": "EAST",
        "currency_code": "ETB",
        "flag_code": "ET",
    },
    {
        "code": "KE",
        "name": "Kenya",
        "region": "EAST",
        "currency_code": "KES",
        "flag_code": "KE",
    },
    {
        "code": "MG",
        "name": "Madagascar",
        "region": "EAST",
        "currency_code": "MGA",
        "flag_code": "MG",
    },
    {
        "code": "MU",
        "name": "Maurice",
        "region": "EAST",
        "currency_code": "MUR",
        "flag_code": "MU",
    },
    {
        "code": "RW",
        "name": "Rwanda",
        "region": "EAST",
        "currency_code": "RWF",
        "flag_code": "RW",
    },
    {
        "code": "SC",
        "name": "Seychelles",
        "region": "EAST",
        "currency_code": "SCR",
        "flag_code": "SC",
    },
    {
        "code": "SO",
        "name": "Somalie",
        "region": "EAST",
        "currency_code": "SOS",
        "flag_code": "SO",
    },
    {
        "code": "SS",
        "name": "Soudan du Sud",
        "region": "EAST",
        "currency_code": "SSP",
        "flag_code": "SS",
    },
    {
        "code": "TZ",
        "name": "Tanzanie",
        "region": "EAST",
        "currency_code": "TZS",
        "flag_code": "TZ",
    },
    {
        "code": "UG",
        "name": "Ouganda",
        "region": "EAST",
        "currency_code": "UGX",
        "flag_code": "UG",
    },
    
]
async def seed_countries(
    db: AsyncSession,
) -> None:

    for data in COUNTRIES:

        result = await db.execute(
            select(Country)
            .where(
                Country.code == data["code"]
            )
            .limit(1)
        )

        country = (
            result.scalar_one_or_none()
        )

        if country is None:
            db.add(
                Country(**data)
            )
        else:
            country.name = data["name"]
            country.region = data["region"]
            country.currency_code = (
                data["currency_code"]
            )
            country.flag_code = (
                data["flag_code"]
            )
            country.is_active = True

    await db.commit()