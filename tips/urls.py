from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'tips'
urlpatterns = [
    path('cafes', views.IndexView.as_view(), name='index'),  # TODO: redirect '' to 'cafes'
    path('cafes/<str:slug>/', views.CafeView.as_view(), name='cafe'),
    path('cafes/<str:cafe_slug>/<str:waiter_username>', views.WaiterView.as_view(), name='waiter'),
    path('register', views.registration, name='register'),
    path('login', views.login_user, name='login'),
    path('logout', login_required(views.logout_user), name='logout'),
    path('<str:username>', views.iamview, name='user')
]