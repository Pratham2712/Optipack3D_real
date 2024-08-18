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

urlpatterns = [
    path('', home, name="home"),
    path('freeTrial/', freeTrial, name='freeTrial'),
    path('join/', joinCreateOrganisation, name='joinCreateOrganisation'),  # Updated name for join/create organisation
    path('login/', login_view, name='login'),  # Use distinct view function for login
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('manageUsers/', manageUsers, name='manageUsers'),
    path('additionalInformation/', additionalInformation, name='additionalInformation'),
    path('freeOutput/', freeOutput, name='freeOutput'),
    path('enquire/', enquire, name='enquire')

]

#for aws enable 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)