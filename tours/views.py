# tours/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q 

# تم تجميع وتنظيم كل الاستيرادات هنا
from .models import (
    Tour, Category, Activity, BlogPost, BlogCategory,
    Hotel, HotelLocation, HotelImage, CategoryGalleryImage,
    TourPackage, Amenity, FAQ, Boat, BoatImage
)
from .forms import BookingForm, ContactForm, GeneralBookingForm, CategoryBookingForm 

# ==========================================================

# tours/views.py

def home(request):
    """
    View for the home page with separated tour types.
    """
    # جلب الرحلات المميزة الخاصة بالنايل كروز فقط
    nile_cruise_tours = Tour.objects.filter(
        category__name__icontains="Nile Cruise", 
        is_featured=True
    )
    
    # جلب كل الرحلات الساحلية المميزة (أي رحلة ليست نايل كروز)
    coastal_tours = Tour.objects.exclude(
        category__name__icontains="Nile Cruise"
    ).filter(is_featured=True)
    
    # جلب كل الفئات لعرضها في قسم الكاتيجوري
    categories = Category.objects.all()

    # --- هذا هو الجزء الجديد الذي يصلح المشكلة ---
    # تجهيز الصور الرئيسية لكل رحلة في القائمتين
    for tour in nile_cruise_tours:
        package = tour.packages.first()
        if package:
            # First, prepare the list of all images for this package
            package.all_package_images = list(package.boats.all().first().images.all()) if package.boats.exists() and package.boats.first() else []
            package.all_package_images.extend(list(package.hotels.all().first().images.all()) if package.hotels.exists() and package.hotels.first() else [])
            
            # Then, set the main tour image from that list
            tour.main_tour_image = package.all_package_images[0].image if package.all_package_images else None
        else:
            tour.main_tour_image = None
            
    for tour in coastal_tours:
        package = tour.packages.first()
        if package:
            # First, prepare the list of all images for this package
            package.all_package_images = list(package.boats.all().first().images.all()) if package.boats.exists() and package.boats.first() else []
            package.all_package_images.extend(list(package.hotels.all().first().images.all()) if package.hotels.exists() and package.hotels.first() else [])

            # Then, set the main tour image from that list
            tour.main_tour_image = package.all_package_images[0].image if package.all_package_images else None
        else:
            tour.main_tour_image = None
    # --- نهاية الجزء الجديد ---

    context = {
        'nile_cruise_tours': nile_cruise_tours,
        'coastal_tours': coastal_tours,
        'categories': categories,
    }
    return render(request, 'tours/index.html', context)

def tour_detail(request, tour_id):
    """
    View for the tour detail page, handles GET and POST for booking.
    """
    tour = get_object_or_404(Tour, id=tour_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tour = tour
            booking.save()
            messages.success(request, 'Your booking inquiry has been sent successfully!')
            return redirect('tour_detail', tour_id=tour.id)
    else:
        form = BookingForm(tour=tour)

    packages = tour.packages.all()
    all_trip_images = []

    # --- الحلقة الجديدة والمحسنة ---
    for package in packages:
        # 1. نجهز قائمة الصور الكاملة الخاصة بهذه الباقة للـ Modal
        package.all_package_images = []
        for boat in package.boats.all():
            package.all_package_images.extend(boat.images.all())
        for hotel in package.hotels.all():
            package.all_package_images.extend(hotel.images.all())
        
        # 2. نجمع كل الصور في قائمة واحدة للمعرض الرئيسي في أعلى الصفحة
        all_trip_images.extend(package.all_package_images)

        # 3. نحدد الصورة الرئيسية للكارت الخارجي
        package.main_package_image = None
        if package.all_package_images:
            package.main_package_image = package.all_package_images[0].image
    
    faqs = tour.faqs.all()
    similar_tours = Tour.objects.filter(category=tour.category).exclude(id=tour.id)[:3] if tour.category else []
    all_categories = Category.objects.all()
    tour_amenities = tour.amenities.all()

    context = {
        'tour': tour,
        'form': form,
        'packages': packages,
        'all_trip_images': all_trip_images,
        'faqs': faqs,
        'similar_tours': similar_tours,
        'categories': all_categories,
        'amenities': tour_amenities,
    }
    return render(request, 'tours/tour_detail.html', context)

def about_us(request):
    """
    View for the About Us page.
    """
    return render(request, 'tours/about.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact_us')
    else:
        form = ContactForm()
        
    return render(request, 'tours/contact.html', {'form': form})

def general_booking_view(request):
    if request.method == 'POST':
        form = GeneralBookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your inquiry has been sent! We will contact you shortly.')
            return redirect(request.META.get('HTTP_REFERER', '/')) 
    return redirect('/')

def blog_list(request):
    posts = BlogPost.objects.all()
    categories = BlogCategory.objects.all()
    context = {'posts': posts, 'categories': categories}
    return render(request, 'tours/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    similar_posts = BlogPost.objects.filter(category=post.category).exclude(slug=slug)[:3]
    categories = Category.objects.all() 
    main_tour_category = post.related_tours.first().category if post.related_tours.exists() else None
    similar_tours = Tour.objects.filter(category=main_tour_category).exclude(id__in=post.related_tours.all().values_list('id', flat=True))[:3] if main_tour_category else []

    context = {
        'post': post,
        'similar_posts': similar_posts,
        'similar_tours': similar_tours,
        'categories': categories,
    }
    return render(request, 'tours/blog_detail.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    hotels_in_category = category.featured_hotels.all()
    gallery_images = category.gallery_images.all()
    activities_in_category = category.activities.all()
    featured_tours = Tour.objects.filter(category=category, is_featured=True)[:3]

    if request.method == 'POST':
        form = CategoryBookingForm(request.POST, hotels=hotels_in_category)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.category = category
            booking.save()
            messages.success(request, 'Your booking inquiry has been sent successfully!')
            return redirect('category_detail', category_id=category.id)
    else:
        form = CategoryBookingForm(hotels=hotels_in_category)

    context = {
        'category': category,
        'hotels': hotels_in_category,
        'gallery_images': gallery_images,
        'activities': activities_in_category,
        'featured_tours': featured_tours,
        'form': form,
    }
    
    return render(request, 'tours/category_detail.html', context)


def all_tours(request):
    tours_list = Tour.objects.all().order_by('id')
    categories = Category.objects.all()

    category_filter = request.GET.get('category')
    if category_filter:
        tours_list = tours_list.filter(category__id=category_filter)

    paginator = Paginator(tours_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'tours/tour_card_snippet.html',
            {'tours': page_obj}
        )
        return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

    context = {
        'tours': page_obj,
        'categories': categories,
    }
    return render(request, 'tours/all_tours.html', context)

def search_results(request):
    query = request.GET.get('q')
    results = []

    if query:
        # نبحث في اسم الرحلة، الوصف، والوجهة
        results = Tour.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(destination__icontains=query)
        )

    # نقوم بتجهيز الصور الرئيسية للرحلات التي تم العثور عليها
    for tour in results:
        package = tour.packages.first()
        if package and hasattr(package, 'main_package_image'):
            tour.main_tour_image = package.main_package_image
        else:
            tour.main_tour_image = None
            
    context = {
        'query': query,
        'tours': results,
    }
    return render(request, 'tours/search_results.html', context)

# الكود الصحيح
def privacy_policy_view(request):
    return render(request, 'tours/privacy_policy.html')


def terms_view(request):
    return render(request, 'tours/terms.html')

