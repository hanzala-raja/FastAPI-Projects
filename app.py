from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic, supplier_pydanticIn, Supplier ,product_pydanticIn , product_pydantic, Products)

from typing import List
from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType, NameEmail
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

from dotenv import dotenv_values
from dotenv import load_dotenv
credentials = dotenv_values(".env")

load_dotenv()

app = FastAPI()

@app.get('/')
def index():
  return{"message": "Hello"}


# Adding Supplier
@app.post('/supplier')
async def add_supplier(supplier_info: supplier_pydanticIn):
  supplier_obj = await Supplier.create(**supplier_info.dict(exclude_unset=True))
  response = await supplier_pydantic.from_tortoise_orm(supplier_obj)
  return {"status": "ok", "data": response}

# See All the Supplier
@app.get('/supplier')
async def get_all_supplier():
  response = await supplier_pydantic.from_queryset(Supplier.all())
  return {"status": "ok", "data": response}

# To Find Specific Supplier
@app.get('/supplier/{supplier_id}')
async def get_specific_supplier(supplier_id: int):
    response = await supplier_pydantic.from_queryset_single(Supplier.get(id=supplier_id))
    return {"status": "ok", "data": response}

# Update Supplier
@app.put('/supplier/{supplier_id}')
async def update_supplier(supplier_id: int, update_info: supplier_pydanticIn):
    supplier = await Supplier.get(id=supplier_id)
    data = update_info.dict(exclude_unset=True) 
    await supplier.update_from_dict(data)
    await supplier.save()
    response = await supplier_pydantic.from_tortoise_orm(supplier)  
    return {"status": "ok", "data": response}

# Delete Supplier
@app.delete('/supplier/{supplier_id}')
async def delete_supplier(supplier_id: int):
  await Supplier.get(id = supplier_id).delete() 
  return {"status": "ok"}

# Adding Products
@app.post('/product/{supplier_id}')
async def add_product(supplier_id: int, products_details: product_pydanticIn): 
    supplier = await Supplier.get(id=supplier_id)
    products = products_details.model_dump(exclude_unset=True)
    products['revenue'] = products.get('quantity_sold', 0) * products.get('unit_price', 0)
    product_obj = await Products.create(**products, supplied_by=supplier)
    response = await product_pydantic.from_tortoise_orm(product_obj)
    return {"status": "ok", "data": response}

# To Show All Products
@app.get('/product')
async def all_products():
   response = await product_pydantic.from_queryset(Products.all())
   return {"status": "ok", "data": response}

# Finding specific Product
@app.get('/product/{product_id}')
async def specific_product(id: int):
   response = await product_pydantic.from_queryset_single(Products.get(id = id))
   return {"status": "ok", "data": response}

# Update Product
@app.put('/product/{product_id}')
async def update_product(id: int, update_info: product_pydanticIn):
   product = await Products.get(id = id)
   update_info = update_info.dict(exclude_unset =True)
   product.name = update_info['name']
   product.quantity_in_stock = update_info['quantity_in_stock']
   product.revenue += update_info['quantity_sold'] * update_info['unit_price']
   product.quantity_sold += update_info['quantity_sold']
   product.unit_price += update_info['unit_price']
   await product.save()
   response = await product_pydantic.from_tortoise_orm(product)
   return {"status": "ok", "data": response}

# Delete Product
@app.delete('/product/{id}')
async def delete_product(id: int):
   await Products.filter(id = id).delete()
   return {"status": "ok"}


class EmailSchema(BaseModel):
    email: List[NameEmail]  


class EmailContent(BaseModel):
   message:str
   subject:str

conf = ConnectionConfig(
    MAIL_USERNAME = credentials['EMAIL'],
    MAIL_PASSWORD = credentials['PASSWORD'],
    MAIL_FROM = credentials['EMAIL'],
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

@app.post('/email/{product_id}')
async def send_email(product_id:int, content: EmailContent):
  product = await Products.get(id=product_id)
  supplier = await product.supplied_by
  recipients_list = [supplier.email]
   
  html = f"""
    <h5>Hanzala Business LTD</h5>
    <br>
    <p>Hi, This is a testing mail</p> 
    <p><b>Subject:</b> {content.subject}</p> 
    <p><b>Message:</b> {content.message}</p> 
    <br>  
    <h6>Regards,</h6>
    <h6>Hanzala Business LTD</h6> 
    """

  message = MessageSchema(
        subject=content.subject,
        recipients=recipients_list, # Yahan corrected list pass ki hai
        body=html,
        subtype=MessageType.html
    )
  fm = FastMail(conf)
  await fm.send_message(message)
  return {"status": "ok"}   


#DB Connection 
register_tortoise(
  app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)