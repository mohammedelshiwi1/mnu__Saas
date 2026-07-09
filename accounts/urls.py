from django.urls import path
from . import views
urlpatterns = [
    path('login/',  views.login_view,   name='login'),
    path('logout/', views.logout_view,  name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('users/',  views.manage_users, name='manage_users'),
]
