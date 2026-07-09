from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('semesters.urls')),
    path('students/', include('students.urls')),
    path('complaints/', include('complaints.urls')),
    path('reports/', include('reports.urls')),
    path('chat/', include('chat.urls')),
    path('analytics/', include('analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
