"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home.views import *
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from home.views import get_csrf_token

urlpatterns = [
    path('', home, name="home"),
    path('freeOutput', freeOutput, name='freeOutput'),
    path('freeOutputJson', freeOutputJson, name='freeOutputJson'),
    path('freeOutputJson2', freeOutputJson2, name='freeOutputJson2'),
    path('freeTrial/', freeTrial, name='freeTrial'),
    path('join/', joinCreateOrganisation, name='joinCreateOrganisation'),  # Updated name for join/create organisation
    path('login/', login_view, name='login'),  # Use distinct view function for login
    path('loginJson', login_viewJson, name='loginJson'),  # Use distinct view function for login
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('manageUsers/', manageUsers, name='manageUsers'),
    path('additionalInformation/', additionalInformation, name='additionalInformation'),
    path('additionalInformationJson', additionalInformationJson, name='additionalInformationJson'),
    path('enquire/', enquire, name='enquire'),
    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
    # auth route========================================================================================================
    path('send_otp_to_email', send_otp_to_email, name='send_otp_to_email'),
    path('verify_otp', verify_otp, name='verify_otp'),
    path('verify_login', verify_login, name='verify_login'),
    path('check_email', check_email, name='check_email'),
    path('check_login', check_login, name='check_login'),
    # admin route ===================================================================================================
    path('add_permission', add_permission, name='add_permission'),
    path('get_permissions', get_permissions, name='get_permissions'),
    path('add_loadplan', add_loadplan, name='add_loadplan'),
    path('get_loadplan', get_loadplan, name='get_loadplan'),
    path('add_container', add_container, name='add_container'),
    path('get_container', get_container, name='get_container'),
    path('send_email', send_email, name='send_email'),
    path('get_allusers', get_allusers, name='get_allusers'),
    path('get_usertype', get_usertype, name='get_usertype'),
    path('update_usertype', update_usertype, name='update_usertype'),
    path('remove_user', remove_user, name='remove_user'),
    path('add_sku', add_sku, name='add_sku'),
    path('get_sku', get_sku, name='get_sku'),
    path('delete_sku', delete_sku, name='delete_sku'),
    # admin and planner route =============================================================================================
    path('add_or_edit_order', add_or_edit_order, name='add_or_edit_order'),
    path('get_skuByCode', get_skuByCode, name='get_skuByCode'),
    path('get_containerByName', get_containerByName, name='get_containerByName'),
    path('get_orderByNumber', get_orderByNumber, name='get_orderByNumber'),
    path('attach_skus_to_order', attach_skus_to_order, name='attach_skus_to_order'),
    path('get_skus_by_order_numbers', get_skus_by_order_numbers, name='get_skus_by_order_numbers'),

]

#for aws enable 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)