from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #homepage  urls
    path('', home, name='home'),

    #store urls
    path('store/<int:pk>/', store, name='store'),
    path('generate_qr_code', generate_code, name="generate_code"),

    #cart urls
    path('add-to-cart', add_to_cart, name='add-to-cart'),
    path('cart', cart_list, name='cart'),
    path('update-cart', update_cart_item, name='update-cart'),
    path('delete-from-cart', delete_cart_item, name='delete-from-cart'),

    #checkout urls
    path('orderAlP/', checkout, name='orderit'),

    #order urls
    path('orderstatus/<int:pk>',order_status,name='order_status'),
    path('order_update/<int:id>/',order_update,name='order_update'),
    path('ordersdisplay/',orders_display,name='orders_display')

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

