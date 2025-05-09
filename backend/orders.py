from fastapi import APIRouter, HTTPException, status
from backend.auth import db_dependency, user_dependency
from backend.models import Cart, CartItem, Order, OrderItem, Product, User, OrderStatus
from datetime import datetime, UTC

router = APIRouter()

@router.post("/create-order", status_code=status.HTTP_201_CREATED)
async def create_order(db: db_dependency, user: user_dependency):
    user_id = user["sub"]

    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = Order(user_id=user_id, created_at=datetime.now(UTC))
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            price=item.product.price,
            status=OrderStatus.PENDING
        )
        db.add(order_item)

    for item in cart_items:
        db.delete(item)

    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
    }


@router.get("/my-orders", status_code=status.HTTP_200_OK)
async def get_user_orders(db: db_dependency, user: user_dependency):
    user_id = user["sub"]

    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    orders = db.query(Order).filter(Order.user_id == user_id).all()
    if not orders:
        return {"message": "No orders found"}

    order_list = []

    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        items_detail = []

        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                items_detail.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "status": item.status.value,
                })

        order_list.append({
            "order_id": order.id,
            "created_at": order.created_at,
            "items": items_detail
        })

    return {
        "user_id": user_id,
        "orders": order_list
    }
