
from app.email_service import send_order_confirmation

send_order_confirmation(
    recipient="hamzahamza970453@gmail.com",
    order_id=101,
    items=[
        {
            "product_name_snapshot": "Smartphone",
            "quantity": 2,
            "subtotal": "20000.00"
        }
    ],
    total="20050.00",
    address={
        "address_line_1": "Test Address",
        "city": "Hyderabad",
        "state": "Telangana",
        "postal_code": "500001"
    }
)
