/* tabs.js — product detail tab switching */

(function () {
    'use strict';

    function showTab(productSlug, tabName) {
        const container = document.getElementById('product-' + productSlug) || document;

        container.querySelectorAll('.tab').forEach(function (t) {
            t.classList.remove('active');
        });

        container.querySelectorAll('.tab-content').forEach(function (c) {
            c.classList.remove('active');
        });

        const activeTab = container.querySelector(`.tab[data-tab="${tabName}"]`);
        if (activeTab) activeTab.classList.add('active');

        const activeContent = document.getElementById(productSlug + '-' + tabName);
        if (activeContent) activeContent.classList.add('active');
    }

    // Expose globally so onclick attributes in templates can call it
    window.showTab = showTab;
}());
