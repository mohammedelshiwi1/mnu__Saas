from django.urls import path
from . import views
urlpatterns = [
    path('', views.analytics_dashboard, name='analytics'),
    path('search/', views.search_view, name='analytics_search'),
    path('api/heatmap/', views.api_heatmap, name='api_heatmap'),
]
