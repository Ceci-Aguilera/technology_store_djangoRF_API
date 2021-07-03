from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

import json

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.views import APIView

from .models import *
from .serializers import *

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

#===============================================================================
#   Helpers
#===============================================================================
def add_to_cart(request, product_variation):
    data = request.data
    try:
        user = request.user
        if user is not None:
            order, created = Order.objects.get_or_create(
                user = user,
                ordered = False
            )
            #Check if item was already added before
            final_color = ColorVariationSerializer(data=data['final_color'])
            final_color.is_valid(raise_exception=True)
            final_color = final_color.save()
            cart_item = CartItem(final_product = product_variation,
                final_color=final_color, quantity=data['quantity'],
                order=order)
            for eachProduct in order.get_all_cart_items():
                if eachProduct.final_product == cart_item.final_product:
                    quantity = eachProduct.quantity + cart_item.quantity
                    cart_item.quantity = max(0, quantity)
                    cart_item.save()
                    eachProduct.delete()
                    break

            cart_item.save()
            result = order.id

    # Anonymous User
    except:
        try:
            order_id = data['order_id']
            order = Order.objects.get(
                id = order_id,
                ordered = False,
                user = None
            )
        except:
            try:
                order = Order.objects.create()
                order_id = order.id
                final_color = ColorVariationSerializer(data=data['final_color'])
                final_color.is_valid(raise_exception=True)
                final_color = final_color.save()
                cart_item = CartItem(final_product = product_variation,
                    final_color=final_color, quantity=data['quantity'],
                    order=order)
            except:
                result='Error'
                return result
        for eachProduct in order.get_all_cart_items():
            if eachProduct.final_product == cart_item.final_product:
                quantity = eachProduct.quantity + cart_item.quantity
                cart_item.quantity = max(0, quantity)
                cart_item.save()
                eachProduct.delete()
                break

        cart_item.save()
        result = order_id

    return result;


def delete_item_from_cart(request, order_id, item_id):
    try:
        order = Order.objects.get(id = id)
        if request.user.is_anonymous == True or request.user == order.user:
            item = CartItem(id = item_id)
            item.delete()
            result = 'Success'
        else:
            result = 'Error'
    except:
        result = 'Error'

    return result

#===============================================================================
#   End of Helpers
#===============================================================================

class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    model = Category
    queryset = Category.objects.all()


class ProductVariationsListView(ListAPIView):
    serializer_class = ProductVariationSerializer
    model = ProductVariation
    queryset = ProductVariation.objects.all()

class ProductVariationFromCategoryListView(ListAPIView):
    serializer_class = ProductVariationSerializer
    model = ProductVariation
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_url_kwarg)
        return ProductVariation.objects.filter(product__category__id=id)



class ProductVariationDetailView(GenericAPIView):

    serializer_class = ProductVariationSerializer

    def get(self, request, id, format=None):

        final_product = ProductVariation.objects.get(id = id)
        final_product_serializer = self.get_serializer(final_product)

        variations_to_send = ProductVariation.objects.filter(product = final_product.product)
        variations_serializer = self.get_serializer(variations_to_send, many=True)

        return Response({"Product": final_product_serializer.data, "Variations": variations_serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, id, format=None):

        final_product = ProductVariation.objects.get(id = id)
        result = add_to_cart(request, final_product)
        status_result = status.HTTP_200_OK if result!="Error" else status.HTTP_400_BAD_REQUEST
        return Response({"Result":result}, status=status_result)


class CartView(RetrieveUpdateDestroyAPIView):

    serializer_class = CartSerializer
    lookup_url_kwarg = 'id'
    lookup_url_kwarg2 = 'item_id'

    def get(self, request, format=None):
        try:
            id = self.kwargs.get(self.lookup_url_kwarg)
            order = Order.objects.get(id = id)
            if request.user.is_anonymous == True or request.user == order.user:
                order_serializer = self.get_serializer(order)
                return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)


    # Delete CartItem from Cart
    def put(self, request, format=None):
        id = self.kwargs.get(self.lookup_url_kwarg)
        item_id = self.kwargs.get(self.lookup_url_kwarg_2)
        result = delete_item_from_cart(request, order_id, item_id)
        status_result = status.HTTP_200_OK if result == 'Success' else status.HTTP_400_BAD_REQUEST
        return Response({"Result":result}, status=status_result)


    def delete(self, request, format=None):
        id = self.kwargs.get(self.lookup_url_kwarg)
        order = Order.objects.get(id = id)
        if request.user.is_anonymous == True or request.user == order.user:
            order.delete()
            return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)
