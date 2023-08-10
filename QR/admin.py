from django.contrib import admin
from .models import *


# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}



admin.site.register(Store, StoreAdmin)
admin.site.register(Table)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(OrderItem)
admin.site.register(Subscription)
