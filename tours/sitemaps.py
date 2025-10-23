# الملف: Web/tours/sitemaps.py

from django.contrib.sitemaps import Sitemap
# لاحظ إننا استدعينا كل الموديلز اللي ضفنالها الدالة
from .models import Tour, Category, BlogPost 
from django.urls import reverse

class TourSitemap(Sitemap):
    """
    خريطة خاصة بكل الرحلات
    """
    changefreq = "weekly" # معدل التغيير المتوقع للصفحات دي (اسبوعي)
    priority = 0.9        # أهمية الصفحات دي (من 0 لـ 1)

    def items(self):
        # هات كل الرحلات
        return Tour.objects.all()

    # (اختياري لكن مفضل)
    # لو عندك حقل لآخر تعديل، ممكن تفعل السطور دي
    # def lastmod(self, obj):
    #     return obj.updated_at 


class CategorySitemap(Sitemap):
    """
    خريطة خاصة بصفحات المدن (التصنيفات)
    """
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        # هات كل التصنيفات اللي معلم عليها "show_in_categories"
        return Category.objects.filter(show_in_categories=True)


class BlogPostSitemap(Sitemap):
    """
    خريطة خاصة بالمقالات
    """
    changefreq = "daily" # المقالات ممكن تتغير يومياً
    priority = 0.7

    def items(self):
        return BlogPost.objects.all()

    def lastmod(self, obj):
        # إنت عندك الحقل ده، وده ممتاز لجوجل
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    """
    خريطة للصفحات الثابتة (الرئيسية، عنا، اتصل بنا...الخ)
    """
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        # دي أسماء الـ paths من ملف tours/urls.py
        return ['home', 'about_us', 'contact_us', 'blog_list', 'transfers', 'privacy_policy', 'terms']

    def location(self, item):
        return reverse(item)