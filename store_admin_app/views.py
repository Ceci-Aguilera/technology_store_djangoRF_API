from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
)
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

import json
from knox.models import AuthToken
from datetime import date, timedelta

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

from customer_app.models import User
from customer_app.serializers import *

from store_app.models import *
from store_app.serializers import *

from .serializers import *

# Create your views here.

# ==============================================================================
# Authentication
# ==============================================================================
class CheckAdminAuthenticatedView(RetrieveAPIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = UserCRUDSerializer

    def get_object(self):
        return self.request.user


# ==============================================================================
# User
# ==============================================================================
class UserListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    serializer_class = UserCRUDSerializer
    model = User
    queryset = User.objects.all()


class UserUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = UserCRUDSerializer
    lookup_field='id'


# ==============================================================================
# Order
# ==============================================================================
class OrderListView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderUpdateView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = OrderSerializer
    lookup_field = 'id'

# ==============================================================================
# Products
# ==============================================================================
# class ProductListView(ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
# class ProuductManageView(RetrieveUpdateDestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
#     serializer_class = ProductSerializer
#     lookup_field = 'id'
#
# class ProductMostSell(ListAPIView):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
#     queryset = Product.objects.all().order_by('amount_sold')[:10]
#     serializer_class = ProductMostSellSerializer

# ==============================================================================
# Refund
# ==============================================================================
class RefundListView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer

class RefundtManageView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = RefundSerializer
    lookup_field = 'id'

# ==============================================================================
# Payment
# ==============================================================================
class PaymentListViewCurrentYear(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Payment.objects.all().filter(timestamp__year = date.today().year)
    serializer_class = PaymentSerializer


class PaymentListViewCurrentMonth(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Payment.objects.all().filter(timestamp__month = date.today().month)
    serializer_class = PaymentSerializer

class PaymentListViewCurrentWeek(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        current_day = date.today()
        start_week = current_day - timedelta(current_day.weekday())
        end_week = start_week + timedelta(7)
        return Payment.objects.all().filter(timestamp__range = [start_week, end_week])

    serializer_class = PaymentSerializer

class PaymentProportionToUser(GenericAPIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    def get(self, request, format=None):

        logged_payments = Payment.objects.filter(user__isnull=False).count()
        anonymous_payments = Payment.objects.filter(user__isnull=True).count()

        return Response({"Logged payments": logged_payments, "Anonymous payments": anonymous_payments},
            status=status.HTTP_200_OK,
            )
