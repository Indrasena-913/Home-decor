from unicodedata import category

from fastapi import FastAPI
import models
import auth
import products
import cart
import category
import orders
from database import engine

app=FastAPI()
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(category.router)
app.include_router(orders.router)

models.Base.metadata.create_all(bind=engine)





