from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    
    # --- الأسطر الجديدة التي تحل المشكلة ---
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('book-now/', views.general_booking_view, name='book_now'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('search/', views.search_results, name='search_results'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
]