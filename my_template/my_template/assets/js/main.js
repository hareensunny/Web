!function(e){"use strict";e(window).on("load",function(){e(".loader-page").delay("300").fadeOut(1e3)}),e(".slider-1").owlCarousel({loop:!0,autoplay:!0,autoplayTimeout:5e3,animateOut:"fadeOut",animateIn:"fadeIn",smartSpeed:450,margin:0,nav:!0,navText:["<i class='fas fa-angle-double-left'></i>","<i class='fas fa-angle-double-right'></i>"],dots:!0,responsive:{0:{items:1},600:{items:1},1000:{items:1}}});var a=e(".slider-2");a.owlCarousel({loop:!0,autoplay:!0,autoplayTimeout:5e3,animateOut:"fadeOut",animateIn:"fadeIn",smartSpeed:450,dotsContainer:".dots-slider",margin:0,nav:!1,navText:["<i class='fas fa-angle-double-left'></i>","<i class='fas fa-angle-double-right'></i>"],dots:!0,touchDrag:!1,mouseDrag:!1,responsive:{0:{items:1,dots:!1},600:{items:1,dots:!1},991:{items:1,nav:!1,dots:!1},993:{items:1,nav:!1,dots:!0}}}),e(".slides-left").on("click",function(){event.preventDefault(),a.trigger("prev.owl.carousel")}),e(".slides-right").on("click",function(){event.preventDefault(),a.trigger("next.owl.carousel")});var t=e(".team-slider");t.owlCarousel({loop:!0,margin:30,autoplay:!0,autoplayTimeout:5e3,nav:!1,dots:!1,responsive:{0:{items:1,nav:!1},600:{items:1,nav:!1},992:{items:3,nav:!1,loop:!0},1200:{items:4,nav:!1,loop:!0}}}),e(".slide-left").on("click",function(){event.preventDefault(),t.trigger("prev.owl.carousel")}),e(".slide-right").on("click",function(){event.preventDefault(),t.trigger("next.owl.carousel")});var o=e(".team-3-slider");o.owlCarousel({loop:!0,margin:0,autoplay:!1,nav:!1,dots:!1,responsive:{0:{items:1,nav:!1},576:{items:1,nav:!1},992:{items:3,nav:!1,loop:!0},1200:{items:4,nav:!1,loop:!0}}}),e(".slide-left.team-3").on("click",function(){event.preventDefault(),o.trigger("prev.owl.carousel")}),e(".slide-right.team-3").on("click",function(){event.preventDefault(),o.trigger("next.owl.carousel")}),e(".testimonial-slider").owlCarousel({loop:!0,margin:10,nav:!0,autoplay:!1,dots:!1,navText:["<a class='arrow-btn flex-center'><i class='fas fa-arrow-left'></i></a>","<a class='arrow-btn flex-center'><i class='fas fa-arrow-right'></i></a>"],responsive:{0:{items:1},600:{items:1},1000:{items:1}}});var i=e(".testimonial-2-slide");i.owlCarousel({loop:!0,margin:30,autoplay:!0,autoplayTimeout:5e3,nav:!1,dots:!1,responsive:{0:{items:1,nav:!1},768:{items:2,nav:!1},992:{items:3,nav:!1,loop:!0},1200:{items:3,nav:!1,loop:!0}}}),e("#testimonial-slider").owlCarousel({loop:!0,margin:0,autoplay:!0,autoplayTimeout:5e3,nav:!1,dots:!0,responsive:{0:{items:1},768:{items:1},992:{items:1,loop:!0},1200:{items:2,loop:!0}}}),e(".slide-left.testi-2").on("click",function(){event.preventDefault(),i.trigger("prev.owl.carousel")}),e(".slide-right.testi-2").on("click",function(){event.preventDefault(),i.trigger("next.owl.carousel")}),e(".testimonial-3-slide").owlCarousel({loop:!0,margin:0,autoplay:!0,autoplayTimeout:5e3,nav:!1,dots:!0,responsive:{0:{items:1,nav:!1}}}),e(".client-logo-slide").owlCarousel({loop:!0,margin:140,autoplay:!0,nav:!1,dots:!1,slideTransition:"linear",autoplayTimeout:5e3,autoplaySpeed:5e3,autoplayHoverPause:!0,responsive:{0:{items:2,margin:50},600:{items:2},991:{items:3},1200:{items:4}}}),e(".logos-slide").owlCarousel({loop:!0,margin:20,autoplay:!0,nav:!1,dots:!1,slideTransition:"linear",autoplayTimeout:5e3,autoplaySpeed:5e3,autoplayHoverPause:!0,responsive:{0:{items:2,margin:50},600:{items:2},991:{items:2},1200:{items:3}}}),e(".slider-type-blog").owlCarousel({loop:!0,margin:0,autoplay:!0,nav:!0,dots:!1,autoplayTimeout:5e3,autoplayHoverPause:!0,navText:["<i class='fas fa-arrow-left transform-v-'></i>","<i class='fas fa-arrow-right'></i>"],responsive:{0:{items:1,margin:0},1200:{items:1}}}),e(".work-gallaty").owlCarousel({loop:!0,margin:30,autoplay:!0,autoplayTimeout:4e3,autoplayHoverPause:!0,nav:!1,responsive:{0:{items:2},600:{items:4},1000:{items:6}}}),e(".btn-filter").on("click",function(a){e(this).siblings(".active").removeClass("active"),e(this).addClass("active"),event.preventDefault()}),e(window).on("scroll",function(){e(window).scrollTop()<100?e(".transperant-head,.bottom-head").removeClass("fixed-nav"):e(".transperant-head,.bottom-head").addClass("fixed-nav"),e(this).scrollTop()>800?e(".scroll-btn").addClass("opacity-10"):e(".scroll-btn").removeClass("opacity-10")}),e(".scroll-btn").on("click",function(a){a.preventDefault(),e("html, body").animate({scrollTop:0},800)}),e(".main-menu").meanmenu({meanMenuContainer:".mobile-menu",meanScreenWidth:"991"}),e(".main-menu-2").meanmenu({meanMenuContainer:".mobile-menu-2",meanScreenWidth:"991"}),e(".main-menu-3").meanmenu({meanMenuContainer:".mobile-menu-3",meanScreenWidth:"991"}),e("#searchModal").on("shown.bs.modal",function(){e(".input-search").trigger("focus")})}(jQuery);


$('.banner_slider').owlCarousel({
    loop:true,
    margin:0,
    nav:false,
    dots:true,
    autoplay:true,
    autoplayTimeout:4000,
    slideSpeed: 600,
    autoplayHoverPause:false,
    mouseDrag:false,
    animateOut: 'fadeOut',
    responsive:{
        0:{
            items:1
        },
        600:{
            items:1
        },
        1000:{
            items:1
        }
    }
})
