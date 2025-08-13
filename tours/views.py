# tours/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.db.models import Q
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

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

            # ==== تجميع بيانات الحجز طبقاً للفورم اللي عندك ====
            data = form.cleaned_data
            name             = data.get('full_name', '')
            email            = data.get('email', '')
            phone            = data.get('phone_number', '')
            adults           = data.get('num_adults', 0)
            children         = data.get('num_children', 0)
            package_name     = data.get('package', '')            # غالباً ModelChoiceField -> هيتحول لنص تلقائي
            package_name = str(package_name or '').replace(' (None)', '')
            special_requests = data.get('special_requests', '')
            date             = '-'  # مفيش تاريخ في الفورم الحالي
            guests_str       = f"Adults: {adults or 0}, Children: {children or 0}"

            # ==== 1) إيميل الإدارة (نصي) ====
            admin_lines = [
                f"New Booking Request – {tour.name}",
                f"Name: {name or '-'}",
                f"Email: {email or '-'}",
                f"Phone: {phone or '-'}",
                f"Guests: {guests_str}",
                f"Package: {package_name or '-'}",
                f"Special Requests: {(special_requests or '-').strip()}",
                f"Date: {date}",
            ]
            admin_body = "\n".join(admin_lines)

            try:
                EmailMessage(
                    subject=f"New Booking Request – {tour.name}",
                    body=admin_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[email] if email else []
                ).send(fail_silently=False)
            except Exception as e:
                messages.warning(request, f'Booking saved, but admin email failed: {e}')

            # ==== 2) إيميل العميل (HTML + نص بديل) ====
            if email:
                ctx = {
                    'name': name or 'Traveler',
                    'tour_name': tour.name,
                    'phone': phone,
                    'guests': guests_str,
                    'date': date,
                    'package_name': package_name,
                    'special_requests': special_requests,
                    # اللوجو بالرابط المطلق اللي حددته
                    'logo_url': 'https://hakuna-matataa.com/static/images/Blue%20and%20Yellow%20Simple%20Travel%20Logo.png',
                    'brand_color': '#0ea5e9',
                    'site_url': 'https://hakuna-matataa.com',
                }

                try:
                    html_content = render_to_string('tours/booking_confirmation.html', ctx)
                except TemplateDoesNotExist:
                    html_content = None
                except Exception:
                    html_content = None

                # نص بديل بسيط لو HTML مش متاح لأي سبب
                text_body = "\n".join([
                    f"Hello {ctx['name']},",
                    "",
                    "We received your booking request. Our team will contact you shortly.",
                    f"Tour: {ctx['tour_name']}",
                    f"Phone: {ctx['phone'] or '-'}",
                    f"Guests: {ctx['guests']}",
                    f"Package: {ctx['package_name'] or '-'}",
                    f"Special Requests: {(ctx['special_requests'] or '-').strip()}",
                    f"Date: {ctx['date']}",
                    "",
                    "Hakuna Matata Tours",
                    ctx['site_url'],
                ])

                try:
                    if html_content:
                        email_msg = EmailMultiAlternatives(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        )
                        email_msg.attach_alternative(html_content, "text/html")
                        email_msg.send(fail_silently=False)
                    else:
                        EmailMessage(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        ).send(fail_silently=False)
                except Exception as e:
                    messages.warning(request, f'Confirmation email failed: {e}')

            messages.success(request, 'Your booking inquiry has been sent successfully!')
            return redirect('tour_detail', tour_id=tour.id)
    else:
        form = BookingForm(tour=tour)

    # ===== باقي تفاصيل الصفحة كما هي =====
    packages = tour.packages.all()
    all_trip_images = []

    for package in packages:
        package.all_package_images = []
        for boat in package.boats.all():
            package.all_package_images.extend(boat.images.all())
        for hotel in package.hotels.all():
            package.all_package_images.extend(hotel.images.all())
        all_trip_images.extend(package.all_package_images)
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
            # الحجز هيتسجل مباشرة بكل الحقول اللي في الفورم (بما فيها tour)
            booking = form.save()

            data = form.cleaned_data
            name             = data.get('full_name', '') or ''
            email            = data.get('email', '') or ''
            phone            = data.get('phone_number', '') or ''
            country          = data.get('country', '') or ''
            adults           = data.get('num_adults', 0) or 0
            children         = data.get('num_children', 0) or 0
            special_requests = (data.get('special_requests', '') or '').strip()
            tour_obj         = data.get('tour', None)

            tour_name   = str(tour_obj or 'General Inquiry')
            guests_str  = f"Adults: {int(adults) if str(adults).isdigit() else adults}, " \
                          f"Children: {int(children) if str(children).isdigit() else children}"
            package_name = '-'    # النموذج العام مفيهوش باكيدج
            date         = '-'    # مفيش تاريخ في النموذج العام

            # ===== 1) إيميل الإدارة (نصي) =====
            admin_lines = [
                f"New Booking Request – {tour_name}",
                f"Name: {name or '-'}",
                f"Email: {email or '-'}",
                f"Phone: {phone or '-'}",
                f"Country: {country or '-'}",
                f"Guests: {guests_str}",
                f"Package: {package_name}",
                f"Special Requests: {special_requests or '-'}",
                f"Date: {date}",
            ]
            admin_body = "\n".join(admin_lines)

            try:
                EmailMessage(
                    subject=f"New Booking Request – {tour_name}",
                    body=admin_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[email] if email else []
                ).send(fail_silently=False)
            except Exception as e:
                messages.warning(request, f'Inquiry saved, but admin email failed: {e}')

            # ===== 2) إيميل العميل (HTML + نص بديل) =====
            if email:
                ctx = {
                    'name': name or 'Traveler',
                    'tour_name': tour_name,
                    'phone': phone,
                    'guests': guests_str,
                    'date': date,
                    'package_name': package_name,
                    'special_requests': special_requests,
                    'logo_url': 'https://hakuna-matataa.com/static/images/Blue%20and%20Yellow%20Simple%20Travel%20Logo.png',
                    'brand_color': '#0ea5e9',
                    'site_url': 'https://hakuna-matataa.com',
                }

                try:
                    html_content = render_to_string('tours/booking_confirmation.html', ctx)
                except TemplateDoesNotExist:
                    html_content = None
                except Exception:
                    html_content = None

                text_body = "\n".join([
                    f"Hello {ctx['name']},",
                    "",
                    "We received your booking request. Our team will contact you shortly.",
                    f"Tour: {ctx['tour_name']}",
                    f"Phone: {ctx['phone'] or '-'}",
                    f"Guests: {ctx['guests']}",
                    f"Package: {ctx['package_name'] or '-'}",
                    f"Special Requests: {(ctx['special_requests'] or '-').strip()}",
                    f"Date: {ctx['date']}",
                    "",
                    "Hakuna Matata Tours",
                    ctx['site_url'],
                ])

                try:
                    if html_content:
                        email_msg = EmailMultiAlternatives(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        )
                        email_msg.attach_alternative(html_content, "text/html")
                        email_msg.send(fail_silently=False)
                    else:
                        EmailMessage(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        ).send(fail_silently=False)
                except Exception as e:
                    messages.warning(request, f'Confirmation email failed: {e}')

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

            # ===== Helper =====
            def pick(data, *keys, default=''):
                for k in keys:
                    if k in data:
                        v = data.get(k)
                        if v not in (None, '', [], {}):
                            return v
                return default

            data = form.cleaned_data

            # ===== Exact field names from your form (with safe fallbacks) =====
            name   = pick(data, 'full_name', 'name', 'customer_name', default='')
            email  = pick(data, 'email', 'customer_email', default='')
            phone  = pick(data, 'phone_number', 'phone', 'mobile', 'customer_phone', default='')

            start_date     = pick(data, 'start_date', 'date', 'travel_date', default='-')
            number_of_days = pick(data, 'number_of_days', 'nights', 'days', default='')
            adults         = pick(data, 'adults', 'num_adults', 'adults_count', default=0) or 0
            children       = pick(data, 'children', 'num_children', 'children_count', default=0) or 0

            hotel_obj   = pick(data, 'hotel', 'selected_hotel', 'hotel_name', default='')
            hotel_name  = str(hotel_obj or '').replace(' (None)', '')

            address = pick(data, 'address', 'location', default='')
            notes   = pick(data, 'comment', 'message', 'notes', 'special_requests', default='')

            # Guests string
            def to_int(x):
                try: return int(x)
                except Exception: return x if x not in (None, '') else 0
            guests_str = f"Adults: {to_int(adults)}, Children: {to_int(children)}"

            tour_name    = category.name
            package_name = hotel_name or '-'
            date         = start_date  # للتمبلت

            # ===== 1) Admin email (plain text) =====
            admin_lines = [
                f"New Booking Request – {tour_name}",
                f"Category: {category.name} [ID: {category.id}]",
                f"Hotel: {hotel_name or '-'}",
                f"Name: {name or '-'}",
                f"Email: {email or '-'}",
                f"Phone: {phone or '-'}",
                f"Guests: {guests_str}",
                f"Number of days: {number_of_days or '-'}",
                f"Address: {address or '-'}",
                f"Package: {package_name}",
                f"Special Requests: {(notes or '-').strip()}",
                f"Date: {date}",
            ]
            admin_body = "\n".join(admin_lines)

            try:
                EmailMessage(
                    subject=f"New Booking Request – {tour_name}",
                    body=admin_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[email] if email else []
                ).send(fail_silently=False)
            except Exception as e:
                messages.warning(request, f'Booking saved, but admin email failed: {e}')

            # ===== 2) Customer email (HTML + text alternative) =====
            if email:
                ctx = {
                    'name': name or 'Traveler',
                    'tour_name': tour_name,
                    'phone': phone,
                    'guests': guests_str,
                    'date': date,
                    'package_name': package_name,
                    'special_requests': notes,
                    'logo_url': 'https://hakuna-matataa.com/static/images/Blue%20and%20Yellow%20Simple%20Travel%20Logo.png',
                    'brand_color': '#0ea5e9',
                    'site_url': 'https://hakuna-matataa.com',
                }

                try:
                    html_content = render_to_string('tours/booking_confirmation.html', ctx)
                except TemplateDoesNotExist:
                    html_content = None
                except Exception:
                    html_content = None

                text_body = "\n".join([
                    f"Hello {ctx['name']},",
                    "",
                    "We received your booking request. Our team will contact you shortly.",
                    f"Tour: {ctx['tour_name']}",
                    f"Phone: {ctx['phone'] or '-'}",
                    f"Guests: {ctx['guests']}",
                    f"Package: {ctx['package_name'] or '-'}",
                    f"Special Requests: {(ctx['special_requests'] or '-').strip()}",
                    f"Date: {ctx['date']}",
                    "",
                    "Hakuna Matata Tours",
                    ctx['site_url'],
                ])

                try:
                    if html_content:
                        email_msg = EmailMultiAlternatives(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        )
                        email_msg.attach_alternative(html_content, "text/html")
                        email_msg.send(fail_silently=False)
                    else:
                        EmailMessage(
                            subject="We received your booking – Hakuna Matata Tours",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                            reply_to=[settings.DEFAULT_FROM_EMAIL],
                        ).send(fail_silently=False)
                except Exception as e:
                    messages.warning(request, f'Confirmation email failed: {e}')

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

