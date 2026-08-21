from abc import ABC, abstractmethod
from decimal import Decimal


class DepositProvider(ABC):

    @abstractmethod
    async def create_deposit(
        self,
        *,
        transaction_id: str,
        phone_number: str,
        amount: Decimal,
        currency_code: str,
        network_code: str,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_status(
        self,
        provider_transaction_id: str,
    ) -> dict:
        raise NotImplementedError