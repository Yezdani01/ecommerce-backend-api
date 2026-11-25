
import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_order_confirmation(
    recipient: str,
    order_id: int,
    items: list,
    total: str,
    address: dict
):
    try:
        message = EmailMessage()

        message["Subject"] = f"Order #{order_id} confirmed"
        message["From"] = os.getenv("SMTP_FROM", "orders@example.com")
        message["To"] = recipient

        item_details = "\n".join(
            f"{item['product_name_snapshot']} x {item['quantity']}"
            f" - {item['subtotal']}"
            for item in items
        )

        address_details = ", ".join(
            str(value) for value in address.values() if value
        )

        message.set_content(
            f"Your order #{order_id} has been confirmed!\n\n"
            f"Items:\n{item_details}\n\n"
            f"Total: {total}\n"
            f"Payment: Cash on Delivery\n"
            f"Shipping Address: {address_details}\n\n"
            f"Thank you for shopping with us!"
        )

        host = os.getenv("SMTP_HOST", "localhost")
        port = int(os.getenv("SMTP_PORT", "1025"))

        with smtplib.SMTP(host, port, timeout=10) as server:

            if os.getenv("SMTP_USE_TLS", "false").lower() == "true":
                server.starttls()

            username = os.getenv("SMTP_USERNAME")
            password = os.getenv("SMTP_PASSWORD")

            if username:
                server.login(username, password)

            server.send_message(message)
            logger.info("Order confirmation email sent successfully")

    except Exception:
        logger.exception(
            "Failed to send confirmation for order %s",
            order_id
        )
