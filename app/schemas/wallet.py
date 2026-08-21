from decimal import Decimal

from pydantic import BaseModel


class WalletResponse(BaseModel):
    balance: Decimal
    currency_code: str
    status: str