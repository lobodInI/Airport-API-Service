from django.contrib import admin

from order.models import Order, Ticket

admin.site.register(Order)
admin.site.register(Ticket)
