(function () {
    'use strict';

    var STORAGE_KEY = 'mt_theme';
    var DARK  = 'dark';
    var LIGHT = 'light';

    function current() {
        return document.documentElement.getAttribute('data-theme') || DARK;
    }

    function apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
        updateIcons(theme);
    }

    function updateIcons(theme) {
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.textContent = theme === DARK ? '🌙' : '☀️';
            btn.title = theme === DARK ? 'Light Mode aktivieren' : 'Dark Mode aktivieren';
        });
    }

    function toggle() {
        apply(current() === DARK ? LIGHT : DARK);
    }

    // Restore saved preference (must happen before render — also set in <head> ideally)
    (function init() {
        var saved;
        try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
        if (saved === LIGHT || saved === DARK) {
            document.documentElement.setAttribute('data-theme', saved);
        }
    }());

    document.addEventListener('DOMContentLoaded', function () {
        updateIcons(current());
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.addEventListener('click', toggle);
        });
    });
}());