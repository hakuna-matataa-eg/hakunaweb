# tours/translation.py

from modeltranslation.translator import register, TranslationOptions
from .models import (
    Category,
    Activity,
    Boat,
    Amenity,
    HotelLocation,
    Hotel,
    Tour,
    ItineraryDay,
    FAQ,
    PackageCategory,
    TourPackage,
    BlogCategory,
    BlogPost,
    CategoryGalleryImage
)

# ترجمة موديل الفئات (المدن)
@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'highlights_text')

# ترجمة موديل الأنشطة
@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

# ترجمة موديل المراكب
@register(Boat)
class BoatTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

# ترجمة موديل الرفاهيات
@register(Amenity)
class AmenityTranslationOptions(TranslationOptions):
    fields = ('name',)

# ترجمة موديل مواقع الفنادق
@register(HotelLocation)
class HotelLocationTranslationOptions(TranslationOptions):
    fields = ('name',)

# ترجمة موديل الفنادق
@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'additional_details')

# ترجمة موديل الرحلات
@register(Tour)
class TourTranslationOptions(TranslationOptions):
    fields = ('name', 'destination', 'description')

# ترجمة موديل خط سير الرحلة اليومي
@register(ItineraryDay)
class ItineraryDayTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

# ترجمة موديل الأسئلة الشائعة
@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

# ترجمة موديل فئات الباقات
@register(PackageCategory)
class PackageCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

# ترجمة موديل باقات الرحلات
@register(TourPackage)
class TourPackageTranslationOptions(TranslationOptions):
    fields = ('name', 'benefits')

# ترجمة موديل فئات المدونة
@register(BlogCategory)
class BlogCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

# ترجمة موديل مقالات المدونة
@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

# ترجمة موديل صور معرض الفئات (المدن)
@register(CategoryGalleryImage)
class CategoryGalleryImageTranslationOptions(TranslationOptions):
    fields = ('caption',)