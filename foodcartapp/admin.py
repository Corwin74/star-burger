from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html

from .models import Banner, Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderLine

from geocode.geo_cache_api import create_or_update_coordinates


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'text']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def response_post_save_change(self, request, obj):
        create_or_update_coordinates(obj.address)
        return super().response_post_save_change(request, obj)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly,
        # so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
                            '<img src="{url}" style="max-height: 200px;"/>',
                            url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
                '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
                edit_url=edit_url, src=obj.image.url
                )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'status',
        'lastname',
        'firstname',
        'phonenumber',
    ]

    inlines = [
        OrderLineInline
    ]

    def response_post_save_change(self, request, obj):
        resp = super().response_post_save_change(request, obj)
        create_or_update_coordinates(obj.address)
        if "ids" in request.GET:
            return redirect('restaurateur:view_orders')
        else:
            return resp

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (db_field.name == 'cook_by') & ('ids' in request.GET):
            try:
                kwargs['queryset'] = Restaurant.objects.filter(
                    id__in=[int(x) for x in request.GET.getlist('ids')])
            except ValueError as _:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
