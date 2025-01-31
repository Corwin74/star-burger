from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework import generics


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from geocode.geo_cache_api import create_or_update_coordinates

from .models import Banner, Order, OrderLine, Product


class BannerDeserializer(ModelSerializer):
    class Meta:
        model = Banner
        fields = ['title', 'src', 'text']


class BannerList(generics.ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerDeserializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class ProductSerializer(ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['products', 'firstname',
                  'lastname', 'phonenumber', 'address']


class OrderDeserializer(ModelSerializer):
    products = ProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname',
                  'lastname', 'phonenumber', 'address']


@api_view(['POST'])
def register_order(request):
    with transaction.atomic():
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address']
        )
        order_lines = []
        for order_line in serializer.validated_data['products']:
            order_lines.append(OrderLine(
                                         order=new_order,
                                         product=order_line['product'],
                                         quantity=order_line['quantity'],
                                         price=order_line['product'].price,
                                        )
                               )
        OrderLine.objects.bulk_create(order_lines)
        deserializer = OrderDeserializer(new_order)
    create_or_update_coordinates(serializer.validated_data['address'])

    return Response(deserializer.data)
