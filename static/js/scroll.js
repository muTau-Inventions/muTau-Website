(function () {
    'use strict';

    function initScrollAnimations() {
        const selector = '.card, .paper, .product-card, .team-card, .feature-list li';
        const elements = document.querySelectorAll(selector);

        if (!elements.length) return;

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity   = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target); // only animate once
                }
            });
        }, { threshold: 0.08 });

        elements.forEach(function (el) {
            el.style.opacity    = '0';
            el.style.transform  = 'translateY(24px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(el);
        });
    }

    document.addEventListener('DOMContentLoaded', initScrollAnimations);
}());
