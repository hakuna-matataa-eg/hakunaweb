document.addEventListener('DOMContentLoaded', function() {
    
    // ===============================================
    // 1. Mobile Menu Toggle Logic (تم التصحيح)
    // ===============================================
    const menuToggle = document.querySelector('.menu-toggle');
    // استهداف القائمة بالكلاس الذي خصصناه لها في HTML
    const navigation = document.querySelector('.navigation'); 

    if (menuToggle && navigation) {
        menuToggle.addEventListener('click', function() {
            // تصحيح اسم الكلاس ليتطابق مع CSS
            navigation.classList.toggle('is-active'); 
        });
    }

    // ===============================================
    // 2. Reusable Auto-Scroller Function
    // ===============================================
    function setupAutoScroller(containerSelector) {
        const scroller = document.querySelector(containerSelector);
        if (scroller) {
            let scrollAmount = 0;
            const scrollStep = 300; // Scroll distance
            const scrollInterval = 3500; // Time delay

            setInterval(() => {
                // Check if we are at the end
                if (scrollAmount >= scroller.scrollWidth - scroller.clientWidth - 1) { // -1 for precision
                    scrollAmount = 0; // Reset to start
                } else {
                    scrollAmount += scrollStep;
                }
                scroller.scrollTo({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            }, scrollInterval);
        }
    }

    // ===============================================
    // 3. Activate Scrollers on All Required Containers
    // ===============================================
    setupAutoScroller('.hotel-grid');
    setupAutoScroller('.nile-cruise-grid');
    setupAutoScroller('.home-tours-scroller');
    setupAutoScroller('.related-tours-scroller');

});
// Accordion Logic for Activities Page
document.addEventListener('DOMContentLoaded', function () {
    const accordionItems = document.querySelectorAll('.accordion-item');

    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        header.addEventListener('click', () => {
            // This part closes other open items for a cleaner experience
            accordionItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
            // This toggles the currently clicked item
            item.classList.toggle('active');
        });
    });
});
// Hotel Detail Modal Logic (Final Correct Version)
document.addEventListener('DOMContentLoaded', function() {
    const hotelModalElement = document.getElementById('hotelDetailModal');
    if (!hotelModalElement) return;

    const hotelModal = new bootstrap.Modal(hotelModalElement);
    const hotelModalTitle = document.getElementById('hotelModalTitle');
    const hotelModalBody = document.getElementById('hotelModalBody');
    const pageBookingForm = document.getElementById('page-booking-form');

    document.querySelectorAll('.view-hotel-details').forEach(button => {
        button.addEventListener('click', function() {
            try {
                const card = this.closest('.hotel-card');

                const name = card.dataset.name;
                const stars = parseInt(card.dataset.stars);
                const images = JSON.parse(card.dataset.images);
                const amenities = JSON.parse(card.dataset.amenities);

                // This is the new, correct way to get the descriptions
                const description = JSON.parse(card.dataset.description);
                const details = JSON.parse(card.dataset.details);

                hotelModalTitle.textContent = name;

                let starsHTML = '<p class="hotel-stars">';
                for(let i = 0; i < 5; i++) { starsHTML += `<i class="fa-star ${i < stars ? 'fas' : 'far'}"></i>`; }
                starsHTML += '</p>';

                let amenitiesHTML = '<div class="hotel-amenities"><h5>Amenities</h5><ul>';
                amenities.forEach(amenity => { amenitiesHTML += `<li><i class="${amenity.icon}"></i> ${amenity.name}</li>`; });
                amenitiesHTML += '</ul></div>';

                let carouselHTML = '';
                if (images.length > 0) {
                    carouselHTML = `
                        <div id="hotelImageCarousel" class="carousel slide" data-bs-ride="carousel">
                            <div class="carousel-inner">${images.map((url, index) => `<div class="carousel-item ${index === 0 ? 'active' : ''}"><img src="${url}" class="d-block w-100" alt="Hotel image"></div>`).join('')}</div>
                            <button class="carousel-control-prev" type="button" data-bs-target="#hotelImageCarousel" data-bs-slide="prev"><span class="carousel-control-prev-icon"></span></button>
                            <button class="carousel-control-next" type="button" data-bs-target="#hotelImageCarousel" data-bs-slide="next"><span class="carousel-control-next-icon"></span></button>
                        </div>`;
                }

                hotelModalBody.innerHTML = `${carouselHTML}${starsHTML}<p>${description}</p><hr><div class="prose-content">${details}</div>${amenitiesHTML}`;

                hotelModal.show();
            } catch (e) {
                console.error("Error parsing hotel data:", e);
                // Optionally, show an alert to the user
                // alert("Could not load hotel details. Please try again later.");
            }
        });
    });

    const modalBookNowBtn = document.getElementById('modalBookNowBtn');
    if (modalBookNowBtn) {
        modalBookNowBtn.addEventListener('click', function() {
            hotelModal.hide();
            if (pageBookingForm) {
                pageBookingForm.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});
// Reusable Horizontal Slider Arrow Controls (تم التصحيح)
document.addEventListener('DOMContentLoaded', function () {
    // تم تعديل هذا السطر ليبحث عن كلا الحاويتين
    const sliderWrappers = document.querySelectorAll('.horizontal-slider-wrapper, .mobile-slider-wrapper');

    sliderWrappers.forEach(wrapper => {
        const slider = wrapper.querySelector('.horizontal-slider, .mobile-gallery-slider');
        const prevButton = wrapper.querySelector('.prev-arrow');
        const nextButton = wrapper.querySelector('.next-arrow');

        if (slider && prevButton && nextButton) {
            // +20 for gap
            const scrollAmount = slider.querySelector(':first-child').clientWidth + 20;

            nextButton.addEventListener('click', () => {
                slider.scrollLeft += scrollAmount;
            });

            prevButton.addEventListener('click', () => {
                slider.scrollLeft -= scrollAmount;101
            });
        }
    });
});