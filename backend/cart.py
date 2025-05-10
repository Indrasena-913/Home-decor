from fastapi import APIRouter, HTTPException, Path
from starlette import status

from backend.auth import db_dependency,user_dependency
from backend.models import Product, User,Cart,CartItem

router=APIRouter()



@router.post("/products/cartload/{product_id}",status_code=status.HTTP_201_CREATED)
async def add_to_cart(db:db_dependency,user:user_dependency,product_id:int=Path(gt=0)):
    userId=user["sub"]
    existing_user = db.query(User).filter(User.id == user["sub"]).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    cart=db.query(Cart).filter(Cart.user_id==userId).first()
    if not cart:
        cart=Cart(user_id=userId)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    cart_item=db.query(CartItem).filter(CartItem.cart_id==cart.id,CartItem.product_id==product_id).first()

    if cart_item:
        cart_item.quantity+=1
    else:
        cart_item=CartItem(cart_id=cart.id,product_id=product_id,quantity=1);
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)


    return {"message": "Product added to cart", "cart_item": {
        "id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }}


@router.delete("/products/unloadcart/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_from_the_cart(user:user_dependency,db:db_dependency,product_id:int=Path(gt=0)):
    userId=user["sub"]

    existing_user = db.query(User).filter(User.id == user["sub"]).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart=db.query(Cart).filter(Cart.user_id==userId).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item=db.query(CartItem).filter(CartItem.cart_id==cart.id,CartItem.product_id==product_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    if cart_item.quantity>1:
        cart_item.quantity-=1
        db.commit()
        db.refresh(cart_item)

    else:
        db.delete(cart_item)
        db.commit()

@router.delete("/products/clear-cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user: user_dependency, db: db_dependency):
    user_id = user["sub"]

    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is already empty")

    for item in cart_items:
        db.delete(item)

    db.commit()

    return {"message": "Cart cleared successfully"}


@router.get("/products/cart", status_code=status.HTTP_200_OK)
async def get_cart_items(user: user_dependency, db: db_dependency):
    user_id = user["sub"]


    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Not authenticated")


    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        return {"message": "Cart is empty", "items": []}


    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    items = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            items.append({
                "cart_item_id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_price": product.price,
                "quantity": item.quantity,
            })

    return {"message": "Cart fetched successfully", "items": items}
