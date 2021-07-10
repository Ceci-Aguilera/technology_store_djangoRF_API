from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import auth
from customer_app.models import User

from django.core.validators import RegexValidator

COLOR_VALIDATOR = RegexValidator(r'^#(?:[0-9a-fA-F]{3}){1,2}$', 'only valid hex color code is accepted')

# Create your models here.



ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)



# ==============================================================================
#   Variation CATEGORY
# ==============================================================================
class VariationCategory(models.Model):
    category_title= models.CharField(max_length=256)

    class Meta:
        verbose_name_plural='variation categories'

    def __str__(self):
        return self.category_title




# ==============================================================================
#   Variation
# ==============================================================================
class Variation(models.Model):
    variation_category= models.ForeignKey(VariationCategory, on_delete=models.CASCADE)
    variation = models.CharField(max_length=256)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return self.variation_category.category_title + " - " + self.variation





# ==============================================================================
#   CATEGORY : Category of a Product
# ==============================================================================
class Category(models.Model):
    category_title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='uploads/products/', blank=True)
    variations_categories = models.ManyToManyField(VariationCategory)
    possible_variations = models.ManyToManyField(Variation)

    class Meta:
        verbose_name_plural='categories'

    def __str__(self):
        return self.category_title




# ==============================================================================
#   PRODUCT
# ==============================================================================
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    base_price = models.FloatField(default=0.0)
    discount_price = models.FloatField(default=0.0)
    description = models.TextField()
    amount_sold = models.IntegerField(default=0)
    extra_available_variations = models.ManyToManyField(VariationCategory)

    def __str__(self):
        return self.title + " - " + self.category.category_title




class ColorVariation(models.Model):
    nickname = models.CharField(max_length=256)
    color_in_hex = models.CharField(max_length=256, validators=[COLOR_VALIDATOR], default='#000000')

    def __str__(self):
        return self.nickname + " - " + self.color_in_hex

# ==============================================================================
#   Product Variation
# In this case the user must choose an existing product variation
# ==============================================================================
class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/products/')
    variations = models.ManyToManyField(Variation)
    color_variations = models.ManyToManyField(ColorVariation)
    custom_base_price = models.FloatField(default=0.0)
    custom_price_with_all_variations = models.FloatField(default=0.0)
    amount_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.product.title  + " - v"

    def get_total_price(self):
        if self.custom_price_with_all_variations != 0 and self.custom_price_with_all_variations != 0.0:
            return self.custom_price_with_all_variations

        price = self.product.base_price if (self.custom_base_price == 0.0 or self.custom_base_price == 0) else self.custom_base_price
        variation_set = self.variations.all()
        for variation in variation_set:
            price += variation.price
        return price





# ==============================================================================
#   ORDER
# ==============================================================================
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    # items = models.ManyToManyField(CartItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        if self.user is not None:
            return self.user.email + '-' + str(self.start_date)
        return 'Anonymous' + '-' + str(self.start_date)

    def get_all_cart_items(self):
        return self.cart_items_set.all()

    def get_total_cost(self):
        total_cost = 0.0
        items = get_all_cart_items()
        for order_item in items:
            total_cost += order_item.get_final_price()
        if self.coupon:
            total_cost -= max(0, (self.coupon.amount))
        return total_cost






# ==============================================================================
#   CART ITEM : Item added to cart
# ==============================================================================
class CartItem(models.Model):
    final_product = models.ForeignKey(ProductVariation, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name="cart_items_set")
    final_color = models.ForeignKey(ColorVariation, on_delete=models.CASCADE)

    def __str__(self):
        helper = 'Deleted object'
        if self.final_product is not None:
            helper = self.final_product.product.title
        return f"{self.quantity} of {helper}"

    def get_total_product_price(self):
        if self.final_product is not None:
            return self.quantity * self.final_product.get_total_price()
        return 0

    def get_amount_saved(self):
        return self.quantity * self.final_product.product.discount_price


    def get_total_discount_product_price(self):
        if self.final_product is not None:
            return self.get_total_product_price() - self.get_amount_saved()
        return 0

    def get_final_price(self):
        if self.final_product is not None:
            if self.final_product.product.discount_price:
                return self.get_total_discount_product_price()
            return self.get_total_product_price()
        return 0





# ==============================================================================
#   Payment :
# ==============================================================================
class Payment(models.Model):
    user= models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user is not None:
            return self.user.email

        return 'Anonymous' + '-' + str(self.timestamp)



# ==============================================================================
#   COUPON
# ==============================================================================
class Coupon(models.Model):
    code = models.CharField(max_length=256)
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.code




# ==============================================================================
#   ADDRESS : Can be billing or shipping and user can set it as its default one
# ==============================================================================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    state_or_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email + "-" + self.address_type

    class Meta:
        verbose_name_plural = 'Addresses'





# ==============================================================================
#   REAFUND
# ==============================================================================
class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk} - {self.email}"
