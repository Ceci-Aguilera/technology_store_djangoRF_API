from rest_framework import serializers
from .models import *
from customer_app.serializers import UserCRUDSerializer

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        exclude = ['user']

class CategorySerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url = True, required=False)

    class Meta:
        model = Category
        fields = '__all__'


class VariationCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = VariationCategory
        fields = '__all__'


class VariationSerializer(serializers.ModelSerializer):

    category = VariationCategorySerializer(read_only = True)

    class Meta:
        model = Variation
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only = True)
    description = serializers.CharField(required=False)
    available_variations = VariationCategorySerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductVariationSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only = True)
    image = serializers.ImageField(use_url=True, required=False)
    variations = VariationSerializer(read_only=True, many=True)
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
