from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #homepage  urls
    path('home', home, name='home'),

    #store urls
    path('<str:slug>/<int:table_id>/', store, name='store'),
    path('generate_qr_code', generate_code, name="generate_code"),

    #cart urls
    path('<str:slug>/<int:table_id>/add-to-cart', add_to_cart, name='add-to-cart'),
    path('<str:slug>/<int:table_id>/cart', cart_list, name='cart'),
    path('<str:slug>/<int:table_id>/update-cart', update_cart_item, name='update-cart'),
    path('<str:slug>/<int:table_id>/delete-from-cart', delete_cart_item, name='delete-from-cart'),

    #checkout urls
    path('<str:slug>/<int:table_id>/orderAlP', checkout, name='orderit'),

    #order urls
    path('<str:slug>/<int:table_id>/orderstatus',order_status,name='order_status'),
    path('<str:slug>/order_update/<int:id>/',order_update,name='order_update'),
    path('<str:slug>/orders-display/',orders_display,name='orders_display')

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

