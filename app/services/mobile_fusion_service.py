from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class MobileFusionService(ABC):
    """
    Contrat obligatoire pour l'intégration Mobile Fusion.

    L'implémentation concrète sera branchée avec
    la documentation officielle et les identifiants
    du compte Mobile Fusion.
    """

    @abstractmethod
    async def create_deposit(
        self,
        *,
        amount: Decimal,
        currency: str,
        country_code: str,
        network_code: str,
        mobile_number: str,
        reference: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def verify_deposit(
        self,
        *,
        provider_reference: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_withdrawal(
        self,
        *,
        amount: Decimal,
        currency: str,
        country_code: str,
        network_code: str,
        mobile_number: str,
        reference: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def verify_withdrawal(
        self,
        *,
        provider_reference: str,
    ) -> dict[str, Any]:
        raise NotImplementedError