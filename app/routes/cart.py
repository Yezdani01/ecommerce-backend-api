
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.cart import Cart, CartItem
from app.models.product import Product
from decimal import Decimal


def get_or_create_cart(db: Session, user_id: int):

    statement = insert(Cart).values(user_id=user_id)

    statement = statement.on_conflict_do_nothing(
        index_elements=["user_id"]
    )

    db.execute(statement)

    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).with_for_update().one()

    return cart


def build_cart_response(db: Session, cart: Cart):

    cart_items = db.query(CartItem, Product).join(
        Product, CartItem.product_id == Product.id
    ).filter(
        CartItem.cart_id == cart.id
    ).all()

    items = []
    total = Decimal("0.00")

    for item, product in cart_items:

        subtotal = product.price * item.quantity
        total += subtotal

        items.append({
            "id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": product.price,
            "subtotal": subtotal,
            "is_active": product.is_active
        })

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total": total
    }
