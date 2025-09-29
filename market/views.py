from django.http import JsonResponse
from .models import Product

def product_list(request):
    products = Product.objects.all().values("id", "name", "price")
    return JsonResponse(list(products), safe=False)
