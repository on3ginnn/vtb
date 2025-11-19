from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from game.views import index, register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('game/', include('game.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
]