  // Function to copy link to clipboard and alert the user
    function copyToClipboard(link) {
        navigator.clipboard.writeText(link).then(() => {
            alert('Link copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    }

// Initialize the carousel using Slick
$(document).ready(function(){
    $('.trending-slider').slick({
        autoplay: true,
        autoplaySpeed: 6000,
        dots: false,
        arrows: true,
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
    });
});

// Close the navbar dropdown when clicking outside of it
document.addEventListener('click', function (event) {
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const isNavbarOpen = navbarCollapse.classList.contains('show');
    const isClickInsideNavbar = navbarCollapse.contains(event.target);

    if (isNavbarOpen && !isClickInsideNavbar) {
        $('.navbar-collapse').collapse('hide');
    }
});