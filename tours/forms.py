# tours/forms.py

from django import forms
from .models import Booking, Tour, TourPackage, HotelBooking, Hotel
from captcha.fields import CaptchaField

# =================================================================
#  النموذج الخاص بصفحة تفاصيل الرحلة (لا تغيير)
# =================================================================
class BookingForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Booking
        fields = [
            'full_name', 'email', 'phone_number', 'country',
            'num_adults', 'num_children', 'special_requests', 'package'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Country'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
            'package': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        tour = kwargs.pop('tour', None)
        super().__init__(*args, **kwargs)
        if tour:
            self.fields['package'].queryset = tour.packages.all()
            self.fields['package'].empty_label = "Select a specific package (optional)"

# =================================================================
#  النموذج العام الخاص بالنافذة المنبثقة (Modal) (لا تغيير)
# =================================================================
class GeneralBookingForm(forms.ModelForm):
    captcha = CaptchaField()
    tour = forms.ModelChoiceField(
        queryset=Tour.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Please select a tour"
    )

    class Meta:
        model = Booking
        fields = [
            'tour', 'full_name', 'email', 'phone_number', 'country', 
            'num_adults', 'num_children', 'special_requests'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Country'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Adults'}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Children'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any questions or special requests?'}),
        }

# =================================================================
#  نموذج صفحة "اتصل بنا" (لا تغيير)
# =================================================================
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}))  
    captcha = CaptchaField()

# =================================================================
#  نموذج صفحة الفئة (Category) (هذا هو التعديل)
# =================================================================
class CategoryBookingForm(forms.ModelForm):
    captcha = CaptchaField() 

    class Meta:
        model = HotelBooking
        fields = [
            'full_name', 'email', 'phone_number', 'address',
            'start_date', 'number_of_days', 'adults', 'children',
            'hotel', 'comment'
        ]
        
        # ======== التعديل هنا ========
        # أضفنا الكلاسات والـ Placeholders المناسبة لكل حقل
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Address (Optional)'}),
            
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            'number_of_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'e.g., 3'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'e.g., 2'}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'e.g., 1'}),
            
            'hotel': forms.Select(attrs={'class': 'form-select'}), 
            
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
        }
        # ======== نهاية التعديل ========

    def __init__(self, *args, **kwargs):
        # نستخرج الفنادق الخاصة بالمدينة من الـ view ونمررها هنا
        hotels_queryset = kwargs.pop('hotels', None)
        super().__init__(*args, **kwargs)
        
        if hotels_queryset:
            self.fields['hotel'].queryset = hotels_queryset
        
        # (اختياري) إضافة عنوان افتراضي للقائمة المنسدلة
        self.fields['hotel'].empty_label = "Select a hotel (optional)"
        
        # (تم حذف اللوب الذي كان هنا لأنه غير دقيق)

# =================================================================
#  نموذج الكابتشا فقط (لا تغيير)
# =================================================================
class CaptchaOnlyForm(forms.Form):
    captcha = CaptchaField()