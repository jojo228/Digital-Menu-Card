from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', home, name='home'),

    #store
    path('store/<int:pk>/', store, name='store'),

    #cart urls
    path('add-to-cart', add_to_cart, name='add-to-cart'),
    path('cart', cart_list, name='cart'),
    path('update-cart', update_cart_item, name='update-cart'),
    path('delete-from-cart', delete_cart_item, name='delete-from-cart'),

    # path('cart/cart_clear/',cart_clear, name='cart_clear'),
    # path('cart/cart-detail/',cart_detail,name='cart_detail'),
    path('orderAlP/', checkout, name='orderit'),
    path('orderstatus/<int:pk>',order_status,name='order_status'),
    path('order_update/<int:id>/',order_update,name='order_update'),
    path('ordersdisplay/',orders_display,name='orders_display')

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

