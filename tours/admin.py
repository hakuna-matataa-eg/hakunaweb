# tours/admin.py

from django.contrib import admin
from django.utils.html import format_html
# --- السطران الجديدان والمهمان ---
from modeltranslation.admin import TabbedTranslationAdmin

from .models import (
    Tour, Category, Activity, Boat, BoatImage, Amenity, FAQ,
    PackageCategory, TourPackage, HotelLocation, Hotel, HotelImage,
    Booking, BlogCategory, BlogPost, ItineraryDay, CategoryGalleryImage,
    HotelBooking # <-- لقد أضفت هذا الموديل هنا لأنه كان ناقصاً في ملفك
)

# --- Inlines تبقى كما هي ---
class BoatImageInline(admin.TabularInline):
    model = BoatImage
    extra = 0
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = 'Image Preview'

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 0
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = 'Image Preview'

class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1

class CategoryGalleryImageInline(admin.TabularInline):
    model = CategoryGalleryImage
    extra = 1

# --- تعديل الكلاسات الرئيسية لترث من TabbedTranslationAdmin ---

@admin.register(Boat)
class BoatAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('name',)
    inlines = [BoatImageInline]
    change_form_template = 'admin/multiupload.html'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for image in request.FILES.getlist('images_multiple'):
            BoatImage.objects.create(boat=obj, image=image)

@admin.register(Hotel)
class HotelAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('name', 'location', 'price_per_night', 'stars')
    list_filter = ('location', 'stars', 'amenities')
    filter_horizontal = ('amenities',)
    inlines = [HotelImageInline]
    change_form_template = 'admin/multiupload.html'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for image in request.FILES.getlist('images_multiple'):
            HotelImage.objects.create(hotel=obj, image=image)

@admin.register(Tour)
class TourAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('name', 'destination', 'category', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'destination')
    filter_horizontal = ('amenities',)
    inlines = [ItineraryDayInline, FAQInline]
    fields = ('name', 'destination', 'category', 'description', 'duration_days',
              'is_featured', 'amenities', 'card_image')

@admin.register(TourPackage)
class TourPackageAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('name', 'category')
    list_filter = ('category',)
    filter_horizontal = ('boats', 'hotels', 'amenities', 'tour')

@admin.register(BlogPost)
class BlogPostAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('author', 'category')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_tours',)

# ==================== التعديل المطلوب هنا ====================
@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin): # <-- التعديل هنا
    list_display = ('name', 'id', 'show_in_categories') # <-- أضفنا هذا
    list_editable = ('show_in_categories',) # <-- لجعلها قابلة للتعديل مباشرة
    list_filter = ('show_in_categories',) # <-- لفلترة الفئات
    inlines = [CategoryGalleryImageInline]
# ==================== نهاية التعديل ====================


# --- الموديلات غير المترجمة أو التي لا تحتاج واجهة خاصة ---
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tour', 'package', 'booking_date')
    list_filter = ('tour', 'booking_date')

# --- إضافة موديل الحجز الفندقي الذي كان ناقصاً ---
@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'hotel', 'category', 'start_date', 'created_at')
    list_filter = ('category', 'hotel', 'start_date')


# تسجيل باقي الموديلات
admin.site.register(Activity)
admin.site.register(Amenity)
admin.site.register(PackageCategory)
admin.site.register(HotelLocation)
admin.site.register(BlogCategory)