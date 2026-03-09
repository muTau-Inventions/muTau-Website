(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var hamburger = document.getElementById('navHamburger');
        var drawer    = document.getElementById('navDrawer');

        if (!hamburger || !drawer) return;

        hamburger.addEventListener('click', function () {
            var isOpen = drawer.classList.toggle('open');
            hamburger.classList.toggle('open', isOpen);
            hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        // Close drawer when a link inside it is clicked
        drawer.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                drawer.classList.remove('open');
                hamburger.classList.remove('open');
                hamburger.setAttribute('aria-expanded', 'false');
            });
        });

        // Close on outside click
        document.addEventListener('click', function (e) {
            if (!drawer.contains(e.target) && !hamburger.contains(e.target)) {
                drawer.classList.remove('open');
                hamburger.classList.remove('open');
                hamburger.setAttribute('aria-expanded', 'false');
            }
        });
    });
}());