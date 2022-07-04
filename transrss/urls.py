"""transrss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from transrss_manager import apis, views

urlpatterns = [
    path('', views.index, name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path('api/feed/', apis.api_feed_source_list),
    path('api/torrent/', apis.api_torrent_list),
    path('api/torrent/<str:id>/', apis.api_torrent_detail),
    path('control/match/', views.match_download),
    path('feed/<int:id>/', views.feed_detail, name="feed_detail"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout')
]
