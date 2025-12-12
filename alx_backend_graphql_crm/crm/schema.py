
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
import re
from datetime import datetime


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order



class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    error = graphene.String()

    def validate_phone(self,phone):
        if phone is None:
            return True
        return bool(re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone))
    return CreateCustomer(customer=input,message="customer created successfully)

  

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(BulkCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        created_customers = []
        errors = []

        for user in input:
            if Customer.objects.filter(email=user.email).exists():
                errors.append(f"Email {user.email} already exists.")
                continue

            customer = Customer(name=user.name, email=user.email, phone=user.phone)
            created_customers.append(customer)

        Customer.objects.bulk_create(created_customers)

        return BulkCreateCustomers(customers=created_customers, errors=errors)

  

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False, default_value=0)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, input):

        if input.price <= 0:
            return CreateProduct(error="Price must be positive.")

        if input.stock < 0:
            return CreateProduct(error="Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )

        return CreateProduct(product=product)


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, input):

        try:
            customer = Customer.objects.get(id=input.customer_id)
        except:
            return CreateOrder(error="Invalid customer ID.")

        if not input.product_ids:
            return CreateOrder(error="At least one product is required.")

        try:
            products = Product.objects.filter(id__in=input.product_ids)
        except:
            return CreateOrder(error="Invalid product ID(s).")

        total = sum([p.price for p in products])

        order = Order.objects.create(customer=customer, total_amount=total)
        order.products.set(products)

        return CreateOrder(order=order)



class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
