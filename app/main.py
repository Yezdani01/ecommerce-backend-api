from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine

#===========Imports for the user login and registration=======
from app.models.user import User
from app.schemas.user import UserCreate,Userlogin, UserResponse, UserUpdate, PasswordChange
from app.routes.auth import register_user, login_user
from app.dependencies import get_db,get_current_user
from app.security import verify_password, hash_password

#==================== imports for address ====================
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate

#============Imports for the category ====================
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

#===========Imports for the products=============

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, StockUpdate, ProductResponse

#=====Imports for the cart===============

from app.models.cart import Cart, CartItem
from app.schemas.cart import (
    CartItemCreate, CartItemUpdate,
    CartItemResponse, CartResponse
)
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert
from app.routes.cart import get_or_create_cart, build_cart_response

#=====Imports for the order and bill===============
from app.models.order import Order, OrderItem
from app.models.bill import Bill

from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.bill import BillResponse

from app.routes.order import build_order_response
from app.email_service import send_order_confirmation

from fastapi import BackgroundTasks
from decimal import Decimal
from uuid import uuid4
import os

# ==================== End of Imports ====================
DELIVERY_FEE = Decimal(os.getenv("DELIVERY_FEE", "40.00"))

Base.metadata.create_all(bind=engine)

app = FastAPI()


#----------------user register, login and profile -----------


@app.post("/api/v1/auth/register", tags=["Register"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user, db)


@app.post("/api/v1/auth/login",tags=["Login"])
def login(user: Userlogin, db: Session = Depends(get_db)):
    return login_user(user, db)

@app.get("/api/v1/users/me",response_model=UserResponse,tags=["User"])
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.patch("/api/v1/users/me", response_model=UserResponse,tags=["User"])
def update_my_profile(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = user.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if "name" in update_data and update_data["name"] is None:
        raise HTTPException(
            status_code=400,
            detail="Name cannot be empty"
        )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


#----------------Change password ----------------------------

@app.patch("/api/v1/users/me/password",tags=["Password"])
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    current_user.password_hash = hash_password(data.new_password)

    db.commit()

    return {"message": "Password changed successfully"}


#----------------Address -----------------------------------


@app.post("/api/v1/addresses", response_model=AddressResponse, status_code=201,tags=["Addresses"])
def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_address = Address(
        **address.model_dump(),
        user_id=current_user.id
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return new_address


@app.get("/api/v1/addresses", response_model=list[AddressResponse],tags=["Addresses"])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).all()

    return addresses



@app.get("/api/v1/addresses/{id}", response_model=AddressResponse,tags=["Addresses"])
def get_address(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    return address


@app.patch("/api/v1/addresses/{id}", response_model=AddressResponse, tags=["Addresses"])
def update_address(
    id: int,
    address: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_address = db.query(Address).filter(
        Address.id == id,
        Address.user_id == current_user.id
    ).first()

    if not existing_address:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = address.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")

    for key, value in update_data.items():
        setattr(existing_address, key, value)

    db.commit()
    db.refresh(existing_address)

    return existing_address



@app.delete("/api/v1/addresses/{id}", tags=["Addresses"])
def delete_address(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()

    return {"message": "Address deleted successfully"}



#----------------Category -----------------------------------


# CREATE CATEGORY
@app.post("/api/v1/categories", response_model=CategoryResponse, status_code=201, tags=["Categories"])
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Category).filter(Category.name == category.name).first()

    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    new_category = Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# LIST CATEGORIES - PUBLIC
@app.get("/api/v1/categories", response_model=list[CategoryResponse], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# GET SINGLE CATEGORY - PUBLIC
@app.get("/api/v1/categories/{id}", response_model=CategoryResponse, tags=["Categories"])
def get_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


# UPDATE CATEGORY
@app.patch("/api/v1/categories/{id}", response_model=CategoryResponse, tags=["Categories"])
def update_category(
    id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Category).filter(Category.id == id).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")

    if "name" in update_data:
        duplicate = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != id
        ).first()

        if duplicate:
            raise HTTPException(status_code=409, detail="Category name already exists")

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing


# DELETE CATEGORY
@app.delete("/api/v1/categories/{id}", tags=["Categories"])
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    
    products = db.query(
        Product).filter(Product.category_id == id).first()

    if products:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category because products are associated with it"
        )
    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}


#=============Products========================

from sqlalchemy import asc, desc
from fastapi import Query



@app.post("/api/v1/products", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    existing = db.query(Product).filter(Product.sku == product.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")

    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product



@app.get("/api/v1/products", response_model=list[ProductResponse], tags=["Products"])
def get_products(
    search: str | None = None,
    category_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    price_sort: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active.is_(True))

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if price_sort:
        if price_sort not in ["asc", "desc"]:
            raise HTTPException(
                status_code=400,
                detail="price_sort must be asc or desc"
            )

        if price_sort == "asc":
            query = query.order_by(asc(Product.price))
        else:
            query = query.order_by(desc(Product.price))

    return query.offset(skip).limit(limit).all()




@app.get("/api/v1/products/{id}", response_model=ProductResponse, tags=["Products"])
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == id,
        Product.is_active.is_(True)
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product



#login req


@app.patch("/api/v1/products/{id}", response_model=ProductResponse, tags=["Products"])
def update_product(
    id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Product).filter(Product.id == id).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")

    for field in ["category_id", "sku", "name", "price"]:
        if field in update_data and update_data[field] is None:
            raise HTTPException(status_code=400, detail=f"{field} cannot be null")

    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"]
        ).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    if "sku" in update_data:
        duplicate = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != id
        ).first()

        if duplicate:
            raise HTTPException(status_code=409, detail="SKU already exists")

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing



@app.patch("/api/v1/products/{id}/stock", response_model=ProductResponse, tags=["Products"])
def update_product_stock(
    id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.stock = stock_data.stock

    db.commit()
    db.refresh(product)

    return product



@app.delete("/api/v1/products/{id}", tags=["Products"])
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False

    db.commit()

    return {"message": "Product deactivated successfully"}


@app.get("/api/v1/categories/{id}/products", response_model=list[ProductResponse], tags=["Products"])
def get_category_products(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return db.query(Product).filter(
        Product.category_id == id,
        Product.is_active.is_(True)
    ).all()

#========================Cart =======================

@app.get("/api/v1/cart", response_model=CartResponse, tags=["Cart"])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    response = build_cart_response(db, cart)

    db.commit()

    return response



@app.post("/api/v1/cart/items", response_model=CartResponse, tags=["Cart"])
def add_cart_item(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active.is_(True)
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()

    if existing_item:

        new_quantity = existing_item.quantity + item.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )

        existing_item.quantity = new_quantity

    else:

        if item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )

        new_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )

        db.add(new_item)

    db.flush()

    response = build_cart_response(db, cart)

    db.commit()

    return response



@app.patch("/api/v1/cart/items/{id}", response_model=CartResponse, tags=["Cart"])
def update_cart_item(
    id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    existing_item = db.query(CartItem).filter(
        CartItem.id == id,
        CartItem.cart_id == cart.id
    ).first()

    if not existing_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = db.query(Product).filter(
        Product.id == existing_item.product_id,
        Product.is_active.is_(True)
    ).first()

    if not product:
        raise HTTPException(
            status_code=400,
            detail="Product is unavailable"
        )

    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    existing_item.quantity = item.quantity

    db.flush()

    response = build_cart_response(db, cart)

    db.commit()

    return response



@app.delete("/api/v1/cart/items/{id}", tags=["Cart"])
def delete_cart_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    item = db.query(CartItem).filter(
        CartItem.id == id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    return {"message": "Item removed from cart"}



@app.delete("/api/v1/cart", tags=["Cart"])
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return {"message": "Cart cleared successfully"}


#================Orders==================

@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=201,
    tags=["Orders"]
)
def place_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Verify address ownership
        address = db.query(Address).filter(
            Address.id == order_data.address_id,
            Address.user_id == current_user.id
        ).first()

        if not address:
            raise HTTPException(
                status_code=404,
                detail="Address not found"
            )

        # 2. Get and lock user's cart
        cart = get_or_create_cart(db, current_user.id)

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        # 3. Lock products to prevent concurrent overselling
        product_ids = [item.product_id for item in cart_items]

        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(Product.id).with_for_update().all()

        product_map = {
            product.id: product for product in products
        }

        subtotal = Decimal("0.00")
        order_items_data = []

        # 4. Validate stock and calculate prices
        for item in cart_items:

            product = product_map.get(item.product_id)

            if not product or not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="A product is unavailable"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}"
                )

            item_subtotal = product.price * item.quantity
            subtotal += item_subtotal

            order_items_data.append({
                "product_id": product.id,
                "product_name_snapshot": product.name,
                "quantity": item.quantity,
                "unit_price": product.price,
                "subtotal": item_subtotal
            })

        final_total = subtotal + DELIVERY_FEE

        # 5. Preserve shipping address
        address_snapshot = {
            "address_line_1": address.address_line_1,
            "address_line_2": address.address_line_2,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code
        }

        # 6. Create order
        new_order = Order(
            user_id=current_user.id,
            shipping_address_snapshot=address_snapshot,
            status="pending",
            total=final_total
        )

        db.add(new_order)
        db.flush()

        # 7. Create order items and reduce stock
        for item_data in order_items_data:

            order_item = OrderItem(
                order_id=new_order.id,
                **item_data
            )

            db.add(order_item)

            product = product_map[item_data["product_id"]]
            product.stock -= item_data["quantity"]

        # 8. Create bill
        bill = Bill(
            user_id=new_order.user_id,
            order_id=new_order.id,
            bill_number=f"BILL-{uuid4().hex.upper()}",
            subtotal=subtotal,
            delivery_fee=DELIVERY_FEE,
            final_total=final_total
        )

        db.add(bill)

        # 9. Clear cart
        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete()

        # Prepare email data before committing
        recipient = current_user.email
        order_id = new_order.id

        # 10. Commit everything together
        db.commit()

    except Exception:
        db.rollback()
        raise

    # 11. Send email only after successful commit
    background_tasks.add_task(
        send_order_confirmation,
        (recipient),
        order_id,
        order_items_data,
        str(final_total),
        address_snapshot
    )

    db.refresh(new_order)

    return build_order_response(db, new_order)



@app.get(
    "/api/v1/orders",
    response_model=list[OrderResponse],
    tags=["Orders"]
)
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.id.desc()).all()

    return [
        build_order_response(db, order)
        for order in orders
    ]


@app.get(
    "/api/v1/orders/{id}",
    response_model=OrderResponse,
    tags=["Orders"]
)
def get_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return build_order_response(db, order)



@app.post(
    "/api/v1/orders/{id}/cancel",
    response_model=OrderResponse,
    tags=["Orders"]
)
def cancel_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Lock the order
        order = db.query(Order).filter(
            Order.id == id,
            Order.user_id == current_user.id
        ).with_for_update().first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Only pending orders can be cancelled"
            )

        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        product_ids = [
            item.product_id for item in order_items
        ]

        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(Product.id).with_for_update().all()

        product_map = {
            product.id: product for product in products
        }

        # Restore stock
        for item in order_items:
            product = product_map[item.product_id]
            product.stock += item.quantity

        order.status = "cancelled"

        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(order)

    return build_order_response(db, order)


#===============Bill=============================

@app.get(
    "/api/v1/orders/{id}/bill",
    response_model=BillResponse,
    tags=["Bills"]
)
def get_order_bill(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bill = db.query(Bill).join(
        Order, Bill.order_id == Order.id
    ).filter(
        Bill.order_id == id,
        Bill.user_id == current_user.id,
        Order.user_id == current_user.id
    ).first()

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    return bill



@app.get(
    "/api/v1/bills",
    response_model=list[BillResponse],
    tags=["Bills"]
)
def get_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(Bill.id.desc()).all()



