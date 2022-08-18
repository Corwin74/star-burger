from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Order, OrderLine, Product, Restaurant, RestaurantMenuItem
import numpy as np


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
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

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
    max_id_restaurant = Restaurant.objects.all().order_by('id').last().id
    max_id_product = Product.objects.all().order_by('id').last().id
    interaction_matrix = np.zeros((max_id_restaurant, max_id_product), dtype=int)
    products = RestaurantMenuItem.objects.select_related('product', 'restaurant').all()
    for product in products:
        if product.availability:
            interaction_matrix[product.restaurant.id-1][product.product.id-1] = 1
    current_orders = Order.objects.exclude(status='CT').prefetch_related('lines').all()
    for order in current_orders:
        lines = order.lines.all()
        products_number = len(lines)
        order_matrix = np.zeros((max_id_product, max_id_product), dtype=int)
        for line in lines:
            order_matrix[line.product.id-1][line.product.id-1] = 1
        print(f'{order.id = } {products_number = }')
        q = np.sum(np.dot(interaction_matrix, order_matrix), axis=1)
        print(np.where(q==products_number)[0]+1,'\n')
    print(interaction_matrix)
    return render(request, template_name='order_items.html', context={
        'order_items': Order.price.total('CT'),
    })
