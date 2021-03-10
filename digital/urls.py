"""digital URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from dsrs import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"dsrs", views.DSRViewSet)
router.register(r"dsps", views.DSPViewSet)

'''FROM CARLOS: 
Added the 'resources' path, which forwards the request to the module dsrs.urls'''

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("resources/", include("dsrs.urls")),
]
