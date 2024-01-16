from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [path('admin/', admin.site.urls),
               path('api/', include('api.urls'))]

admin.site.site_header = 'Кабинет шеф-повара'
admin.site.index_title = 'Рецепты поварят'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
