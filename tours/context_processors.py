# tours/context_processors.py
from .forms import GeneralBookingForm

def booking_form_context(request):
    return {
        'general_booking_form': GeneralBookingForm()
    }