from django.contrib import admin
from django.conf.urls import url,include
# from .views import PricesPageAPI,HowToAPIView, CreateOrderAPI, OrderSummaryAPIView, RetrieveAllProductColorsAPI
from .views import *

app_name = 'store_app'

urlpatterns = [
    url(r'^categories/$', CategoryListView.as_view(), name='categories-api'),
    url(r'^products/$', ProductVariationsListView.as_view(), name='products-variation-api'),
    url(r'^products-category/(?P<id>[0-9]+)/$', ProductVariationFromCategoryListView.as_view(), name='products-category-api'),
    url(r'^product-detail/(?P<id>[0-9]+)/$', ProductVariationDetailView.as_view(), name='product-detail-api'),
]
