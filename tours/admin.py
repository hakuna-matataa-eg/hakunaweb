# tours/admin.py

from django.contrib import admin
from .models import (
    Tour, Category, Activity, Boat, BoatImage, Amenity, FAQ, 
    PackageCategory, TourPackage, HotelLocation, Hotel, HotelImage,
    Booking, BlogCategory, BlogPost, ItineraryDay, CategoryGalleryImage
)

# --- Inlines: لإدارة موديلات داخل موديلات أخرى ---

class BoatImageInline(admin.TabularInline):
    model = BoatImage
    extra = 1

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1
    
class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1

class CategoryGalleryImageInline(admin.TabularInline):
    model = CategoryGalleryImage
    extra = 10 # لعرض حقل فارغ واحد لبدء إضافة الصور


# --- Main Admin Classes: لتخصيص لوحة التحكم ---

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'category', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'destination')
    filter_horizontal = ('amenities',)
    inlines = [ItineraryDayInline, FAQInline]

@admin.register(Boat)
class BoatAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [BoatImageInline]

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per_night', 'stars')
    list_filter = ('location', 'stars', 'amenities')
    filter_horizontal = ('amenities',)
    inlines = [HotelImageInline]

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    # هذا هو الجزء الأهم: يسمح بالاختيار المتعدد للمراكب والفنادق والرفاهيات
    filter_horizontal = ('boats', 'hotels', 'amenities', 'tour')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('author', 'category')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_tours',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tour', 'package', 'booking_date')
    list_filter = ('tour', 'booking_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

    # هذا السطر هو المسؤول عن إظهار قسم الصور المتعددة في الأسفل
    inlines = [CategoryGalleryImageInline]

# --- تسجيل الموديلات البسيطة الأخرى ---
admin.site.register(Activity)
admin.site.register(Amenity)
admin.site.register(PackageCategory)
admin.site.register(HotelLocation)
admin.site.register(BlogCategory)
admin.site.register(CategoryGalleryImage)
