(function () {
    'use strict';

    var STORAGE_KEY = 'mt_theme';
    var DARK  = 'dark';
    var LIGHT = 'light';

    // Plain Unicode symbols — not emojis, no variation selectors needed
    var SYMBOL_DARK  = '\u2600';  // ☀  BLACK SUN WITH RAYS  (shown when currently dark → click for light)
    var SYMBOL_LIGHT = '\u263D';  // ☽  CRESCENT MOON        (shown when currently light → click for dark)

    function current() {
        return document.documentElement.getAttribute('data-theme') || DARK;
    }

    function apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
        updateButtons(theme);
    }

    function updateButtons(theme) {
        var symbol = theme === DARK ? SYMBOL_DARK : SYMBOL_LIGHT;
        var label  = theme === DARK ? 'Light Mode' : 'Dark Mode';
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.textContent = symbol;
            btn.title       = label + ' aktivieren';
            btn.setAttribute('aria-label', btn.title);
        });
    }

    function toggle() {
        apply(current() === DARK ? LIGHT : DARK);
    }

    // The inline script in base.html already applies the saved theme before
    // the CSS renders (anti-FOUC). This block only needs to sync the button labels.
    document.addEventListener('DOMContentLoaded', function () {
        updateButtons(current());
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.addEventListener('click', toggle);
        });
    });
}());