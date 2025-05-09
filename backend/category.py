from fastapi import APIRouter, HTTPException, Path
from starlette import status

from backend.auth import db_dependency
from backend.models import Product,Category

router=APIRouter()

@router.get("/categories",status_code=status.HTTP_200_OK)
async def get_categories(db:db_dependency):
    all_categories = db.query(Category).all()
    if not all_categories:
        raise HTTPException(status_code=404, detail="No products found")

    return all_categories



@router.get("/products/categories/{category_id}",status_code=status.HTTP_200_OK)
async def get_products_by_categories(db:db_dependency,category_id:int=Path(gt=0)):
    category=db.query(Category).filter(Category.id==category_id).first()
    if not category:
        raise HTTPException(status_code=404,detail="category not found")
    products=db.query(Product).filter(Product.category_id==category.id).all()
    if not products:
        raise HTTPException(status_code=404,detail="No products found under that category")
    return {
        "category_name":category.name,
        "product":[
            {
                "id":product.id,
                "name":product.name,
                "description":product.description,
                "price":product.price,
                "image":product.image

            } for product in products
        ]
    }


