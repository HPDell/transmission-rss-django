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
from django.urls import include, path
from rest_framework.authtoken import views as authtoken_views
from transrss_manager import apis, views

urlpatterns = [
    path('', views.index, name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path('api/feed/', apis.api_feed_source_list),
    path('api/torrent/', apis.api_torrent_list),
    path('api/torrent/<str:id>/', apis.api_torrent_detail),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-auth-token/', authtoken_views.obtain_auth_token),
    path('control/match/', views.match_download),
    path('feed/', views.feed_list, name="feed_list"),
    path('feed/<int:id>/', views.feed_detail, name="feed_detail"),
    path('feed/<int:id>/delete/', views.feed_delete, name="feed_delete"),
    path('feed/<int:feed_id>/matcher/', views.matcher_list, name="matcher_list"),
    path('feed/<int:feed_id>/matcher/<int:matcher_id>/delete/', views.matcher_delete, name="matcher_delete"),
    path('torrent/refresh/', views.torrent_refresh, name="torrent_refresh"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
