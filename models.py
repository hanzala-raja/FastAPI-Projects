from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


# Making Class For Supplier Model
class Supplier(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=25)
    company = fields.CharField(max_length=25)
    email = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=25)

# Making Class For Product Model
class Products(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=35, nullable=False)
    quantity_in_stock = fields.IntField(default=0)
    quantity_sold = fields.IntField(default=0)
    unit_price = fields.FloatField(max_digits=10, decimal_places=2, default=0.00)
    revenue = fields.FloatField(max_digits=10, decimal_places=2, default=0.00)

# Applying Foreign Key
    supplied_by = fields.ForeignKeyField('models.Supplier', related_name='goods_supplied')


supplier_pydantic = pydantic_model_creator(Supplier, name="Supplier")
supplier_pydanticIn = pydantic_model_creator(Supplier, name="SupplierIn", exclude_readonly=True)

product_pydantic = pydantic_model_creator(Products, name="Product")
product_pydanticIn = pydantic_model_creator(Products, name="ProductIn", exclude_readonly=True)