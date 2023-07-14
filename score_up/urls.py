"""
URL configuration for score_up project.

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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from .views import LoginView, SignupView, CreditCheckItemView, DisputeReasonItemView, EmailTemplateItemView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.frontpage, name='frontpage'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', views.MeView.as_view(), name='me'),
    path('api/content/credit-check-item/', CreditCheckItemView.as_view(), name='credit-check-item'),
    path('api/content/dispute-reason-item/', DisputeReasonItemView.as_view(), name='dispute-reason-item'),
    path('api/content/email-template-item/', EmailTemplateItemView.as_view(), name='email-template-item'),
    path('api/user-images/upload/', views.upload_user_images, name='upload_user_images'),
    path('api/user-images/get/', views.get_user_images, name='get_user_images'),
    path('api/content/save-letter/', views.save_letter, name='save_letter'),
    path('api/content/get-letters/', views.get_letters, name='get_letters'),
    path('api/content/delete-letter/', views.delete_letter, name='delete_letter'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
