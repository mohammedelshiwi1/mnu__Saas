from django.urls import path
from . import views
urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('student/<int:pk>/word/', views.student_report_word, name='student_word'),
    path('semester/excel/', views.semester_excel, name='semester_excel'),
]
