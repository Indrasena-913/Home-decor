from unicodedata import category

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import auth
import products
import cart
import category
import orders
from database import engine

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(category.router)
app.include_router(orders.router)

models.Base.metadata.create_all(bind=engine)





