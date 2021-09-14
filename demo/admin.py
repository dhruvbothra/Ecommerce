from django.contrib import admin
from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered']


admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)