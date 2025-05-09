from fastapi import APIRouter, HTTPException, Path
from starlette import status

from backend.auth import db_dependency
from backend.models import Product

router=APIRouter()



@router.get("/products",status_code=status.HTTP_200_OK)
async def get_products(db:db_dependency):
    # existing_user=db.query(User).filter(User.id==user["sub"]).first()
    # if not existing_user:
    #     raise HTTPException(status_code=401,detail="Not authenticated")
    all_products=db.query(Product).all()
    if not all_products:
        raise HTTPException(status_code=404,detail="No products found")

    return all_products


@router.get("/products/{product_id}",status_code=status.HTTP_200_OK)
async def get_single_product(db:db_dependency,product_id:int=Path(gt=0)):
    # existing_user = db.query(User).filter(User.id == user["sub"]).first()
    # if not existing_user:
    #     raise HTTPException(status_code=401, detail="Not authenticated")

    product_to_return=db.query(Product).filter(Product.id==product_id).first()
    if not product_to_return:
        raise HTTPException(status_code=404,detail="No product found")
    return product_to_return



