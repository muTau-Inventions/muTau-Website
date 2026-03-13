(function () {
    'use strict';

    function initScrollAnimations() {
        var selector = '.card, .paper, .product-card, .team-card, .feature-list li';
        var elements = document.querySelectorAll(selector);

        if (!elements.length) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    // Remove inline styles so CSS transitions (including hover) take over cleanly
                    el.style.opacity   = '';
                    el.style.transform = '';
                    el.style.transition = '';
                    el.classList.add('visible');
                    observer.unobserve(el);
                }
            });
        }, { threshold: 0.08 });

        elements.forEach(function (el) {
            el.classList.add('scroll-hidden');
            observer.observe(el);
        });
    }

    document.addEventListener('DOMContentLoaded', initScrollAnimations);
}());