"""
URL configuration for imsys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# from cake import views #直接将路由设置到根页面 不在需要include包括各个app中的url
from cyanine import views as cyanine

urlpatterns = [
    path("admin/", admin.site.urls),

    #展示主界面
    path('',cyanine.main,name='main'),

    #蛋糕店管理系系统demo
    path('cake/',include('cake.urls'))
]
