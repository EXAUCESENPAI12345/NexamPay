from decimal import Decimal

from app.providers.base import DepositProvider


class MobileFusionProvider(
    DepositProvider
):

    async def create_deposit(
        self,
        *,
        transaction_id: str,
        phone_number: str,
        amount: Decimal,
        currency_code: str,
        network_code: str,
    ) -> dict:

        raise NotImplementedError(
            "Mobile Fusion API integration "
            "must be configured from the "
            "official provider documentation."
        )

    async def get_status(
        self,
        provider_transaction_id: str,
    ) -> dict:

        raise NotImplementedError(
            "Mobile Fusion status API "
            "must be configured."
        )