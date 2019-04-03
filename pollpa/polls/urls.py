from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('poll/<int:poll_id>/', views.poll, name='poll'),
    path('login/', views._login, name='login'),
    path('register/', views.register, name='register'),
    path('reset/', views.reset, name='reset'),
    path('logout/', views._logout, name="logout"),
    path('superlogout/', views._logout, name="superlogout"),
    path('account/', views.account, name="account"),
    path('suggest/', views.suggest, name="suggest"),
    path('latest/', views.latest, name="latest"),
]
