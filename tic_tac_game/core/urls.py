"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from home.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("play/<room_code>", play, name="play"),
    path('accounts/register/',register, name="register"),
    path('accounts/login/',login_page, name="login"),
    path('accounts/logout/', call_logout, name="logout"),
    path("api/generate-room-code/", create_room_id,name="create_room_id" ),
    path("profile-image-upload/", upload_image, name="upload_image"),
    path("user/<id>", profile_page, name="profile_page")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)