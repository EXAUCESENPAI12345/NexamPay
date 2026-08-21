import secrets


def generate_transaction_id() -> str:
    return (
        f"TXN-"
        f"{secrets.token_hex(8).upper()}"
    )


def generate_idempotency_key() -> str:
    return (
        f"IDEMP-"
        f"{secrets.token_hex(16).upper()}"
    )