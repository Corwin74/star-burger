from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

import numpy as np
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability
                for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id]
                                for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    restaurants = Restaurant.objects.raw(
        'SELECT * FROM foodcartapp_restaurant\
        LEFT JOIN geocode_geocache on geocode_geocache.address\
             = foodcartapp_restaurant.address'
    )
    restaurants_geo_cache = {}
    max_id_restaurant = 0
    for venue in restaurants:
        restaurants_geo_cache[venue.id] = venue.lat, venue.lon
        if max_id_restaurant < venue.id:
            max_id_restaurant = venue.id
    print(restaurants_geo_cache)
    max_id_product = Product.objects.all().order_by('id').last().id
    interaction_matrix = np.zeros((max_id_restaurant, max_id_product),
                                  dtype=int)
    products = RestaurantMenuItem.objects.select_related(
                                                         'product',
                                                         'restaurant',
                                                        ).all()
    for product in products:
        if product.availability:
            interaction_matrix[
                product.restaurant.id-1][product.product.id-1] = 1
    unclosed_orders = Order.objects.exclude(status_int=4). \
        order_by('status_int').prefetch_related('lines'). \
        select_related('cook_by').all()
    unclosed_orders_and_coordinates = Order.objects.raw('SELECT * FROM foodcartapp_order\
        LEFT JOIN geocode_geocache on\
        geocode_geocache.address=foodcartapp_order.address')
    orders_geo_cache = {}
    for order in unclosed_orders_and_coordinates:
        orders_geo_cache[order.id] = order.lat, order.lon
    orders_and_candidate_restaurants = []
    for order in unclosed_orders:
        lines = order.lines.all()
        products_number = lines.count()
        order_matrix = np.zeros((max_id_product, max_id_product), dtype=int)
        for line in lines:
            order_matrix[line.product_id-1][line.product_id-1] = 1
        restaurants_candidate_id = (np.where(np.sum(np.dot(interaction_matrix,
                                                    order_matrix),
                                    axis=1) == products_number)[0]+1).tolist()
        restaurants_candidate = []

        # Тупой перебор, но снижает количество SQL запросов, по сравнению с:
        # restaurants_candidate = restaurants.filter(
        #   id__in=restaurants_candidate_id)
        for venue in restaurants:
            if venue.id in restaurants_candidate_id:
                restaurants_candidate.append(venue)
        if restaurants_candidate:
            customer_coordinates = orders_geo_cache[order.id]
            restaurant_and_distance = []
            if customer_coordinates[0] and customer_coordinates[1]:
                for restaurant in restaurants_candidate:
                    restaurant_coordinates = restaurants_geo_cache[restaurant.id]
                    if restaurant_coordinates[0] and restaurant_coordinates[1]:
                        delivery_distance = round(
                            distance.distance(
                                restaurant_coordinates,
                                customer_coordinates
                                ).km,
                            3,
                        )
                        restaurant_and_distance.append(
                            (restaurant, delivery_distance)
                        )
                    else:
                        restaurant_and_distance.append(
                            (restaurant, 'Ошибка определения координат')
                        )
            else:
                for restaurant in restaurants_candidate:
                    restaurant_and_distance.append(
                        (restaurant, 'Ошибка определения координат')
                    )
            orders_and_candidate_restaurants.append(
                (
                    order,
                    sorted(restaurant_and_distance,
                           key=lambda x: x[1] if isinstance(x[1], float) else 100000)
                )
            )
    return render(request, template_name='order_items.html', context={
        'pairs': orders_and_candidate_restaurants,
    })
