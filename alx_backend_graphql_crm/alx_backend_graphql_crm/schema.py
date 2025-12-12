import graphene
from .models import Customer,Order,Product
import re

class Query(graphene.ObjectType):
  hello = graphene.String(default_value="Hello, GraphQL!")




schema=graphene.Schema(query=Query,mutation=Mutation)
