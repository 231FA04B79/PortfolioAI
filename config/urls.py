from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('analyzer/', include('analyzer.urls')),
    path('recruiter/', include('recruiter.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

