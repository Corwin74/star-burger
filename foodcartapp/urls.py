from django.urls import path

from .views import BannerList, product_list_api, banners_list_api, register_order


app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    path('v1/banners/', BannerList.as_view())
]
