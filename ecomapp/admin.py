from django.contrib import admin

from ecomapp.models import Category, Customer, Item

# Register your models here.
# admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Item)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'phone', 'is_staff', 'is_superuser')  # Add 'created_at' to fields to display

admin.site.register(Customer, CustomerAdmin)