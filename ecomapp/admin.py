from django.contrib import admin

from ecomapp.models import Category, Message, Customer, Item,MessageHistory

# Register your models here.
# admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Item)

admin.site.register(Message)
admin.site.register(MessageHistory)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'phone', 'is_staff', 'is_superuser')  # Add 'created_at' to fields to display

admin.site.register(Customer, CustomerAdmin)