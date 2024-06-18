"""
URL configuration for AsesorBot project.

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
from django.urls import path
from .views import home, policy, contact_form_view
from .views import signup, user_login, user_view, user_logout
from .views import user_profile, comofunciona
from .views import ayuda, editar, configuracion
from .views import user_login_editar, user_login_delete
from django.contrib.auth import views as auth_views
from webapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name="home"),
    path("policy/", policy, name="policy"),

    path('contact/', contact_form_view, name='contact_form'),

    path('signup/', signup, name='signup'),
    path("login/", user_login, name="login"),
    
    path('logout/', user_logout, name='logout'),

    path('ayuda/', ayuda, name='ayuda'),

    path('user_view/', user_view, name='user_view'),

    path('accounts/login/', user_login, name='login'),


    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

    path('verify-email-confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify-email-confirm'),

    path('user_view/profile/', user_profile, name='user_profile'),
    path('user_view/comofunciona/', comofunciona, name='comofunciona'),

    path('user_view/configuracion/', configuracion, name='configuracion'),

    path('user_view/configuracion/user_login_editar/', user_login_editar, name='user_login_editar'),
    path('user_view/configuracion/editar/', editar, name='editar'),
    
    path('user_view/configuracion/user_login_delete/<str:user_email>/', user_login_delete, name='user_login_delete'),
]
