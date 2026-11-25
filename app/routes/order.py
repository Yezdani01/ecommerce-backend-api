
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem


def build_order_response(db: Session, order: Order):

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    return {
        "id": order.id,
        "user_id": order.user_id,
        "shipping_address_snapshot": order.shipping_address_snapshot,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
        "items": items
    }
