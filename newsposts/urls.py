"""news URL Configuration

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

from newsposts import views
from django.urls import path, include
from django.contrib import admin

app_name = 'newsposts'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_news, name='login'),
    path('logout/', views.logout_news, name='logout'),
    path('register/', views.register_news, name="register"),
    path('about/', views.about, name='about'),
    path('news/', views.posts, name='posts'),
    path('news/<int:newspost_id>/', views.post_specific, name='posts_individual'),
    path('news/<int:newspost_id>/comment/', views.post_comment, name='post_comment')

]
