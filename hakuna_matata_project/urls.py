from django.contrib import admin
from django.urls import path, include

# استيراد الإعدادات اللازمة لعرض الصور
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    # هذا السطر يربط المشروع بالتطبيق
    path('', include('tours.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# ==================== التعديل الثالث ====================
# هذا السطر ضروري لعرض الصور في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================