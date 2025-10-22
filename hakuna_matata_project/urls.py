from django.contrib import admin
from django.urls import path, include

# استيراد الإعدادات اللازمة لعرض الصور
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # <-- استيراد هذا
urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    # هذا السطر يربط المشروع بالتطبيق
    path('ckeditor/', include('ckeditor_uploader.urls')),

]
urlpatterns += i18n_patterns(
    path('', include('tours.urls')),
    
    # إذا كنت لا تريد ظهور /en/ في الرابط للغة الإنجليزية (الافتراضية)، أزل علامة التعليق من السطر التالي
    # prefix_default_language=False 
)

# ==================== التعديل الثالث ====================
# هذا السطر ضروري لعرض الصور في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================