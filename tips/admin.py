from django.contrib import admin
from .models import Cafe, User, Customer, Waiter, CafeAdmin, Transaction
# Register your models here.

admin.site.register(Cafe)
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Waiter)
admin.site.register(CafeAdmin)
admin.site.register(Transaction)
