from rest_framework import serializers
from .models import *
from customer_app.serializers import UserCRUDSerializer

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        exclude = ['user']




class VariationCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = VariationCategory
        fields = '__all__'


class VariationSerializer(serializers.ModelSerializer):

    variation_category = VariationCategorySerializer(read_only = True)

    class Meta:
        model = Variation
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url = True, required=False)
    variations_categories = VariationCategorySerializer(read_only=True, many=True)
    possible_variations = VariationSerializer(read_only=True, many=True)

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only = True)
    description = serializers.CharField(required=False)
    extra_available_variations = VariationCategorySerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = '__all__'

class ColorVariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ColorVariation
        fields = '__all__'

class ProductVariationSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only = True)
    image = serializers.ImageField(use_url=True, required=False)
    variations = VariationSerializer(read_only=True, many=True)
    color_variations = ColorVariationSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField('get_total_price')


    def get_total_price(self, obj):

        if obj.custom_price_with_all_variations != 0 and obj.custom_price_with_all_variations != 0.0:
            return obj.custom_price_with_all_variations

        price = obj.product.base_price if (obj.custom_base_price == 0.0 or obj.custom_base_price == 0) else obj.custom_base_price
        variation_set = obj.variations.all()
        for variation in variation_set:
            price += variation.price
        return price

    class Meta:
        model = ProductVariation
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):

    final_product = ProductVariationSerializer(read_only=True)
    user = UserCRUDSerializer(read_only=True)
    final_color = ColorVariationSerializer(read_only=True)
    total_product_price = serializers.SerializerMethodField('get_total_product_price')
    amount_saved = serializers.SerializerMethodField('get_amount_saved')
    total_discount_product_price = serializers.SerializerMethodField('get_total_discount_product_price')
    final_price = serializers.SerializerMethodField('get_final_price')

    def get_total_product_price(self, obj):
        if obj.final_product is not None:
            return obj.quantity * obj.final_product.get_total_price()
        return 0

    def get_amount_saved(self, obj):
        return obj.quantity * obj.final_product.product.discount_price


    def get_total_discount_product_price(self, obj):
        if obj.final_product is not None:
            return obj.get_total_product_price() - obj.get_amount_saved()
        return 0

    def get_final_price(self, obj):
        if obj.final_product is not None:
            if obj.final_product.product.discount_price:
                return obj.get_total_discount_product_price()
            return obj.get_total_product_price()
        return 0

    class Meta:
        model = CartItem
        fields = '__all__'




class CartSerializer(serializers.ModelSerializer):

    user = UserCRUDSerializer(read_only=True)
    items = CartItemSerializer(source='cart_items_set', many=True)
    total_cost = serializers.SerializerMethodField('get_total_cost')

    def get_total_cost(self, obj):
        total_cost = 0.0
        items = obj.get_all_cart_items()
        for order_item in items:
            total_cost += order_item.get_final_price()
        if obj.coupon:
            total_cost -= max(0, (obj.coupon.amount))
        return total_cost

    class Meta:
        model = Order
        fields = ('id', 'user', 'items','total_cost')


class PaymentSerializer(serializers.ModelSerializer):

    user  = UserCRUDSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):

    user = UserCRUDSerializer(read_only=True)
    items = CartItemSerializer(source='cart_items_set', many=True)
    billing_address = AddressSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)
    all_cart_items = serializers.SerializerMethodField('get_all_cart_items')
    total_cost = serializers.SerializerMethodField('get_total_cost')

    def get_all_cart_items(self,obj):
        return obj.cart_items_set.all()

    def get_total_cost(self, obj):
        total_cost = 0.0
        items = get_all_cart_items()
        for order_item in items:
            total_cost += order_item.get_final_price()
        if obj.coupon:
            total_cost -= max(0, (obj.coupon.amount))
        return total_cost

    class Meta:
        model = Order
        fields = '__all__'



class RefundSerializer(serializers.ModelSerializer):

    order = OrderSerializer(read_only=True)
    reason = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)

    class Meta:
        model = Refund
        fields = '__all__'
