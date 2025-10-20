from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

def service_worker(request):
    """Serve the service worker with proper headers"""
    import os
    from django.conf import settings
    
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/javascript')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except FileNotFoundError:
        return HttpResponse('// Service worker not found', content_type='application/javascript', status=404)

def manifest(request):
    """Serve the PWA manifest with proper headers"""
    import os
    from django.conf import settings
    
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/json')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except FileNotFoundError:
        return HttpResponse('{}', content_type='application/json', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('students/', include('students.urls')),
    path('batches/', include('batches.urls')),
    path('fees/', include('fees.urls')),
    path('contacts/', include('contacts.urls')),
    path('accounts/', include('accounts.urls')),
    
    # PWA URLs
    path('sw.js', service_worker, name='service_worker'),
    path('manifest.json', manifest, name='manifest'),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)