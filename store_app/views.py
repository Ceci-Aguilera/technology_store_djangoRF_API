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
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes

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
    # if True:
        order = Order.objects.get(id = order_id)
        if request.user.is_anonymous == True or request.user == order.user:
            item = CartItem.objects.get(id = item_id)
            item.delete()
            result = 'Success'
        else:
            result = 'Error'
    except:
    # else:
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




# Product Filtering By Category And Keyword
class ProductFilterByCK(ListAPIView):
    serializer_class = ProductVariationSerializer
    model = ProductVariation

    def get_queryset(self):
        search_params = self.request.query_params.get('search_keyword')
        products = ProductVariation.objects.filter(product__title__icontains=search_params)



# This filter functionality only works with multiple variations, but
# only one variation per category
class VariationsInCategoryListView(APIView):

    def get(self, request, id, format=None):
        product_category = Category.objects.get(id = id)
        variations_categories = product_category.variations_categories.all()
        result = dict()
        for category in variations_categories:
            variations = product_category.possible_variations.filter(variation_category=category)
            result[category.category_title] = VariationSerializer(variations, many=True).data

        return Response({"Result": result}, status=status.HTTP_200_OK)

    def post(self, request, id, format=None):
        data = request.data
        product_category = Category.objects.get(id = id)
        variations_categories = product_category.variations_categories.all()
        products = ProductVariation.objects.filter(product__category__id = id)

        for category in variations_categories:
            try:
                variation_id = data[category.category_title]
                products = products.filter(variations__id=variation_id)
            except:
                pass

        products_serializer = ProductVariationSerializer(products, many=True)
        return Response({"Result": products_serializer.data}, status=status.HTTP_200_OK)




class OrderDetailView(RetrieveAPIView):

    serializer_class = OrderSerializer

    def get_object(self, *args, **kwargs):
        id = self.kwargs.get('id')
        order = Order.objects.get(id = id)
        if order.user is None or order.user == self.request.user:
            return order
        return None




class UserOrdersListView(ListAPIView):

    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.fiter(user=self.request.user)




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

    def get(self, request, id, format=None):
        try:
            order = Order.objects.get(id = id)
            if request.user.is_anonymous == True or request.user == order.user:
                order_serializer = self.get_serializer(order)
                return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)


    # Delete CartItem from Cart
    def put(self, request, id, item_id, format=None):
        result = delete_item_from_cart(request, id, item_id)
        status_result = status.HTTP_200_OK if result == 'Success' else status.HTTP_400_BAD_REQUEST
        return Response({"Result":result}, status=status_result)


    def delete(self, request, id, format=None):
        if request.user.is_anonymous == True or request.user == order.user:
            order.delete()
            return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)





class CheckoutView(GenericAPIView):

    def get(self, request, id, format=None):
        order = Order.objects.get(id = id)
        if request.user.is_anonymous == True or request.user == order.user:
            if order.billing_address == None:
                try:
                    billing_address = Address.objects.get(user=request.user, address_type="B", default=True)
                    order.billing_address = billing_address
                except:
                    pass
            if order.shipping_address == None:
                try:
                    shipping_address = Address.objects.get(user=request.user, address_type="S", default=True)
                    order.shipping_address = shipping_address
                except:
                    pass

            order.save()
            order_serializer = self.get_serializer(order)
            return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response ({"Result":"Error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        try:
            order = Order.objects.get(id=id)
            if order.user is not None:
                if order.user != request.user:
                    return Response({"Order Summary": "Error while updating"}, status=status.HTTP_400_BAD_REQUEST)
            # BILLING AND SHIPPING ADDRESSES
            try:
                billing_address_id = request.data['billing_address_id']
                order.billing_address = Address.objects.get(id = billing_address_id)
                order.save()
            except:
                pass

            try:
                shipping_address_id = request.data['shipping_address_id']
                order.shipping_address = Address.objects.get(id = shipping_address_id)
                order.save()
            except:
                pass

            order_serializer = self.get_serializer(order)
            return Response({"Order Summary": order_serializer.data}, status=status.HTTP_200_OK)


        except:
            return Response({"Order Summary": "Error while updating"}, status=status.HTTP_400_BAD_REQUEST)






class PaymentView(GenericAPIView):
    serializer_class = PaymentSerializer

    def get(self, request, id, format=None):

        try:
            order = Order.objects.get(id=id)
            if order.user != None and order.user != request.user:
                return Response({"Result":"Error authenticating user"}, status=status.HTTP_400_BAD_REQUEST)

            order_serializer = OrderSerializer(order)
            return Response({"Result":order_serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"Result":"Error during payment"}, status=status.HTTP_400_BAD_REQUEST)



    def post(self, request, id, format=None):
        try:
            order = Order.objects.get(id=id, ordered=False)

            amount = int(order.get_total_cost() * 100)

            if order.user==None or order.user.one_click_purchasing == False:
                card_num = request.data['card_num']
                exp_month = request.data['exp_month']
                exp_year = request.data['exp_year']
                cvc = request.data['cvc']

                token = stripe.Token.create(
                  card={
                    "number": card_num,
                    "exp_month": int(exp_month),
                    "exp_year": int(exp_year),
                    "cvc": cvc
                  },
                )

            if order.user is not None and order.user != request.user:
                if order.user != request.user:
                    return Response({"Result":"Error authenticating user"}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    user = request.user

                    if user.one_click_purchasing:
                        customer = stripe.Customer.retrieve(
                            user.stripe_customer_id,
                        )

                        charge = stripe.Charge.create(
                            amount=amount,
                            currency="usd",
                            customer=user.stripe_customer_id
                        )

                        return Response({"Result":"Success"}, status=status.HTTP_200_OK)

                    #If user is not anonymous and wants to save the payment credentials for shopping faster
                    if request.data['save_payment_info']:

                        #Check if user already exists
                        user.one_click_purchasing = True
                        customer = None
                        if user.stripe_customer_id != '' and user.stripe_customer_id != None:

                            # Old Customer
                            stripe.Customer.modify(
                                user.stripe_customer_id,
                                source=token
                            )
                            customer = stripe.Customer.retrieve(
                                user.stripe_customer_id,
                            )
                        else:
                            # New Customer
                            customer = stripe.Customer.create(
                                email=user.email,
                                source=token
                            )
                        user.stripe_customer_id = customer['id']
                        user.save()

                        charge = stripe.Charge.create(
                            amount=amount,
                            currency="usd",
                            customer=user.stripe_customer_id
                        )

            if request.data['save_payment_info'] == False:

                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=token
                )


            # After payment with stripe
            user = order.user
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = user
            payment.amount = order.get_total_cost()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()
            for item in order.items.all():
                item.product.amount_sold += item.quantity
                item.product.save()

            return Response({"Result":"Success"}, status=status.HTTP_200_OK)

        except stripe.error.CardError as e:
            return Response({"Result":"Error with card during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            return Response({"Result":"Rate Limit error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            return Response({"Result":"Invalid request error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            return Response({"Result":"Authentication error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            return Response({"Result":"API connection error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({"Result":"Something went wrong during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"Result":"Error during payment"}, status=status.HTTP_400_BAD_REQUEST)







class CreateRefund(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = RefundSerializer

    def post(self, request, id, format=None):
        try:
            order = Order.objects.get(id=id)
            if order.refund_requested:
                return Response({"Result":"Order has already been asked for refund"}, status=status.HTTP_400_BAD_REQUEST)
            refund_serializer = self.get_serializer(data=request.data)
            refund_serializer.is_valid(raise_exception=True)
            refund_serializer.save(order=order)
            order.refund_requested=True
            order.save()
            return Response({"Result":"Success"}, status=status.HTTP_200_OK)
        except:
            return Response({"Result":"Error asking for refund"}, status=status.HTTP_400_BAD_REQUEST)
