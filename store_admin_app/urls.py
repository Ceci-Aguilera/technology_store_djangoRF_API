from django.contrib import admin
from django.conf.urls import url,include
from .views import *

from knox import views as knox_views

app_name = 'store_admin_app'

urlpatterns = [
    # url(r'^check-admin-auth/$', CheckAdminAuthenticatedView.as_view(), name='check-admin-auth-api'),
]
