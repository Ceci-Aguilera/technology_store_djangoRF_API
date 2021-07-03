from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *
from customer_app.models import User

# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'pk',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__email',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']

class PaymentAdmin(admin.ModelAdmin):

    readonly_fields = ['timestamp',]

    fieldsets = (
            (None, {'fields': ('user', 'stripe_charge_id', 'amount','timestamp')}),
        )

    list_display = [
        'user',
        'amount',
        'timestamp'
    ]

    list_filter = ['user', 'timestamp']
    search_fields = ['user', 'timestamp']

# Register Models Here
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(ProductVariation)
admin.site.register(Variation)
admin.site.register(VariationCategory)
admin.site.register(Category)

admin.site.site_header = 'Tech Store Admin'
