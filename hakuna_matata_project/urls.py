# Web/hakuna_matata_project/urls.py

from django.contrib import admin
from django.urls import path, include

# استيراد الإعدادات اللازمة لعرض الصور
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # <-- استيراد هذا
from django.contrib.sitemaps.views import sitemap
from tours.sitemaps import (
    TourSitemap, 
    CategorySitemap, 
    BlogPostSitemap, 
    StaticViewSitemap
)

sitemaps = {
    'static': StaticViewSitemap,   # صفحات ثابتة
    'tours': TourSitemap,          # الرحلات
    'categories': CategorySitemap, # المدن
    'blog': BlogPostSitemap,       # المقالات
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # --- ### ده مكان السطر الصحيح (جوه القايمة) ### ---
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
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

# السطر ده مهم عشان ملفات الـ static في وضع الإنتاج (Production)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)