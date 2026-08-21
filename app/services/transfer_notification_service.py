from app.services.telegram_delivery_service import (
    telegram_delivery_service,
)


async def notify_transfer_sender(
    *,
    telegram_user_id: int,
    transfer_id: str,
    amount: str,
    currency: str,
    receiver_nexampay_id: str,
) -> None:

    message = (
        "<b>Transfert confirmé</b>\n\n"
        f"Montant : <b>{amount} {currency}</b>\n"
        f"Destinataire : "
        f"<b>{receiver_nexampay_id}</b>\n"
        f"Référence : <b>{transfer_id}</b>"
    )

    await telegram_delivery_service.send_text(
        telegram_user_id=telegram_user_id,
        text=message,
    )


async def notify_transfer_receiver(
    *,
    telegram_user_id: int,
    transfer_id: str,
    amount: str,
    currency: str,
    sender_nexampay_id: str,
) -> None:

    message = (
        "<b>Vous avez reçu un transfert</b>\n\n"
        f"Montant : <b>{amount} {currency}</b>\n"
        f"Expéditeur : "
        f"<b>{sender_nexampay_id}</b>\n"
        f"Référence : <b>{transfer_id}</b>"
    )

    await telegram_delivery_service.send_text(
        telegram_user_id=telegram_user_id,
        text=message,
    )