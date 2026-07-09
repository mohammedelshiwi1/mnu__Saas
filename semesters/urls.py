from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('semesters/', views.semester_list, name='semester_list'),
    path('semesters/add/', views.semester_add, name='semester_add'),
    path('semesters/<int:pk>/toggle/', views.semester_toggle, name='semester_toggle'),
]
