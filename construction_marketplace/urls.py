from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Must include marketplace URLs BEFORE admin
    path('', include('marketplace.urls')),
    
    # Django admin - this should come AFTER marketplace URLs
    path('/admin/', admin.site.urls),
]

if settings.DEBUG:
   
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
