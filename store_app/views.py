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
    Helpers
#===============================================================================

#===============================================================================
    End of Helpers
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
