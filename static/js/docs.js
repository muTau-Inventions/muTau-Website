(function () {
    'use strict';

    function showSection(sectionId, updateHash) {
        document.querySelectorAll('.docs-section').forEach(function (s) {
            s.style.display = 'none';
        });

        document.querySelectorAll('.docs-sidebar a').forEach(function (a) {
            a.classList.remove('active');
        });

        // Show target section
        const target = document.getElementById(sectionId + '-section');
        if (target) target.style.display = 'block';

        // Activate matching sidebar link
        const link = document.querySelector(`.docs-sidebar a[data-section="${sectionId}"]`);
        if (link) link.classList.add('active');

        if (updateHash !== false) {
            history.replaceState(null, '', '#' + sectionId);
        }
    }

    function init() {
        const sidebar = document.querySelector('.docs-sidebar');
        if (!sidebar) return;

        // Attach click handlers
        sidebar.querySelectorAll('a[data-section]').forEach(function (link) {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                showSection(link.dataset.section, true);
            });
        });

        const hash = window.location.hash.replace('#', '');
        if (hash) {
            showSection(hash, false);
        } else {
            // Activate first section by default
            const first = sidebar.querySelector('a[data-section]');
            if (first) showSection(first.dataset.section, false);
        }
    }

    document.addEventListener('DOMContentLoaded', init);
}());
