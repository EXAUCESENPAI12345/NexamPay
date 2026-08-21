from pydantic import BaseModel, Field


class DepositWebhookRequest(BaseModel):
    provider_transaction_id: str = Field(min_length=1, max_length=255)
    status: str = Field(min_length=1, max_length=50)


class WithdrawalWebhookRequest(BaseModel):
    provider_transaction_id: str = Field(min_length=1, max_length=255)
    status: str = Field(min_length=1, max_length=50)
