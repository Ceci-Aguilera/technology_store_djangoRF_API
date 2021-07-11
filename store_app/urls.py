from django.contrib import admin
from django.conf.urls import url,include
# from .views import PricesPageAPI,HowToAPIView, CreateOrderAPI, OrderSummaryAPIView, RetrieveAllProductColorsAPI
from .views import *

app_name = 'store_app'

urlpatterns = [
    url(r'^categories/$', CategoryListView.as_view(), name='categories-api'),
    url(r'^products/$', ProductVariationsListView.as_view(), name='products-variation-api'),
    url(r'^products-most-sell/$', ProductVariationMostSell.as_view(), name='products-variation--most-sell-api'),
    url(r'^products-category/(?P<id>[0-9]+)/$', ProductVariationFromCategoryListView.as_view(), name='products-category-api'),
    url(r'^product-filter/$', ProductFilterByCK.as_view(), name='product-filter-api'),
    url(r'^product-filter/(?P<id>[0-9]+)/$', ProductFilterByCK.as_view(), name='product-filter-api'),
    url(r'^variation-filter/(?P<id>[0-9]+)/$', VariationsInCategoryListView.as_view(), name='variation-filter-api'),
    url(r'^order-detail/(?P<id>[0-9]+)/$', OrderDetailView.as_view(), name='order-detail-api'),
    url(r'^user-orders/$', UserOrdersListView.as_view(), name='user-orders-api'),
    url(r'^product-detail/(?P<id>[0-9]+)/$', ProductVariationDetailView.as_view(), name='product-detail-api'),
    url(r'^cart/(?P<id>[0-9]+)/$', CartView.as_view(), name='product-detail-api'),
    url(r'^cart/delete/(?P<id>[0-9]+)/(?P<item_id>[0-9]+)/$', CartView.as_view(), name='product-detail-api'),
    url(r'^checkout/(?P<id>[0-9]+)/$', CheckoutView.as_view(), name='checkout-api'),
    url(r'^payment/(?P<id>[0-9]+)/$', PaymentView.as_view(), name='payment-api'),
    url(r'^create-refund/(?P<id>[0-9]+)/$', CreateRefund.as_view(), name='create-refund-api'),
]
