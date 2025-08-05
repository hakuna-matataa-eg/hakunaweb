# tours/models.py

from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')
    description = RichTextUploadingField(blank=True, null=True, help_text="اكتب هنا النبذة التعريفية عن المدينة.")
    highlights_text = RichTextUploadingField(blank=True, null=True, help_text="اكتب هنا عن أبرز الأماكن والشواطئ.")
    featured_hotels = models.ManyToManyField(
        'Hotel', 
        blank=True, 
        related_name="featured_in_categories",
        help_text="اختر الفنادق المميزة التي تريد عرضها في صفحة هذه المدينة."
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name

class Activity(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    icon = models.CharField(max_length=50)
    categories = models.ManyToManyField(Category, related_name='activities')
    class Meta:
        verbose_name_plural = "Activities"
    def __str__(self):
        return self.title

class Boat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name

class BoatImage(models.Model):
    boat = models.ForeignKey(Boat, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='boats/gallery/')
    def __str__(self):
        return f"Image for {self.boat.name}"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="e.g., 'fas fa-wifi'")
    def __str__(self):
        return self.name

class HotelLocation(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Hotel(models.Model):
    location = models.ForeignKey(HotelLocation, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    stars = models.IntegerField(default=3, help_text="Star rating from 1 to 5")
    additional_details = RichTextUploadingField(blank=True, null=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    def __str__(self):
        return self.name

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotels/gallery/')
    def __str__(self):
        return f"Image for {self.hotel.name}"

class Tour(models.Model):
    name = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text="هذه هي النظرة العامة للرحلة")
    duration_days = models.IntegerField()
    is_featured = models.BooleanField(default=False, help_text="لعرضها في الصفحة الرئيسية")
    # --- هذا هو الحقل الذي تم إضافته ---
    amenities = models.ManyToManyField(Amenity, blank=True, help_text="الرفاهيات الأساسية للرحلة")
    def __str__(self):
        return self.name

class ItineraryDay(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='itinerary_days/')
    class Meta:
        ordering = ['day_number']
    def __str__(self):
        return f"Day {self.day_number}: {self.title} ({self.tour.name})"

class FAQ(models.Model):
    tour = models.ForeignKey(Tour, related_name='faqs', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    def __str__(self):
        return self.question

class PackageCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class TourPackage(models.Model):
    tour = models.ManyToManyField(Tour, related_name='packages')
    category = models.ForeignKey(PackageCategory, on_delete=models.SET_NULL, null=True, related_name='packages')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    benefits = models.TextField()
    sleeps = models.PositiveIntegerField(default=2)
    boats = models.ManyToManyField(Boat, blank=True, help_text="اختر مركبًا أو أكثر لهذه الباقة")
    hotels = models.ManyToManyField(Hotel, blank=True, help_text="اختر الفنادق إذا كانت هذه باقة إقامة ساحلية")
    amenities = models.ManyToManyField(Amenity, blank=True, help_text="الرفاهيات الخاصة بهذه الباقة")
    def __str__(self):
        return f"{self.name} ({self.tour.name})"

class Booking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Booking for {self.tour.name} by {self.full_name}"

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text="سيتم إنشاؤه تلقائيًا من العنوان")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True)
    content = RichTextUploadingField() 
    featured_image = models.ImageField(upload_to='blog_images/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    related_tours = models.ManyToManyField(Tour, blank=True, help_text="اختر الرحلات المتعلقة بهذا المقال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.title
class CategoryGalleryImage(models.Model):
    category = models.ForeignKey(Category, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='categories/gallery/')
    caption = models.CharField(max_length=100, blank=True) # وصف اختياري للصورة

    def __str__(self):
        return f"Image for {self.category.name}"

class HotelBooking(models.Model):
    # Booking Details
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    number_of_days = models.IntegerField()
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    
    # Customer Details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.full_name} for {self.hotel.name if self.hotel else self.category.name}"
