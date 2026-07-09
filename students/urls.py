from django.urls import path
from . import views
from django.db.models import Q
urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_add, name='student_add'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('<int:pk>/confirm/', views.confirm_data, name='confirm_data'),
]
