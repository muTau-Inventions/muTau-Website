(function () {
    'use strict';

    var STORAGE_KEY = 'mt_particles';
    var COUNT = 80;

    function initParticles() {
        var canvas = document.getElementById('particleCanvas');
        if (!canvas) return;

        var ctx = canvas.getContext('2d');

        function resize() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        resize();

        var particles = [];

        function makeParticle(data) {
            var p = {};
            if (data) {
                p.x       = data.x;
                p.y       = data.y;
                p.size    = data.size;
                p.speedY  = data.speedY;
                p.speedX  = data.speedX;
                p.opacity = data.opacity;
            } else {
                p.x       = Math.random() * canvas.width;
                p.y       = Math.random() * canvas.height;
                p.size    = Math.random() * 2.5 + 0.5;
                p.speedY  = Math.random() * 0.8 + 0.3;
                p.speedX  = Math.random() * 0.4 - 0.2;
                p.opacity = Math.random() * 0.4 + 0.1;
            }
            return p;
        }

        // Restore from sessionStorage if available
        var restored = false;
        try {
            var saved = sessionStorage.getItem(STORAGE_KEY);
            if (saved) {
                var data = JSON.parse(saved);
                if (Array.isArray(data) && data.length === COUNT) {
                    for (var i = 0; i < COUNT; i++) {
                        particles.push(makeParticle(data[i]));
                    }
                    restored = true;
                }
            }
        } catch (e) {}

        if (!restored) {
            for (var j = 0; j < COUNT; j++) {
                particles.push(makeParticle(null));
            }
        }

        function updateParticle(p) {
            p.y -= p.speedY;
            p.x += p.speedX;

            // Reset when off top
            if (p.y < -10) {
                p.x       = Math.random() * canvas.width;
                p.y       = canvas.height + Math.random() * 50;
                p.size    = Math.random() * 2.5 + 0.5;
                p.speedY  = Math.random() * 0.8 + 0.3;
                p.speedX  = Math.random() * 0.4 - 0.2;
                p.opacity = Math.random() * 0.4 + 0.1;
            }

            // Wrap horizontally so particles don't drift off forever
            if (p.x < -10)                  p.x = canvas.width  + 10;
            if (p.x > canvas.width  + 10)   p.x = -10;
        }

        function drawParticle(p) {
            ctx.fillStyle = 'rgba(99,102,241,' + p.opacity + ')';
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (var i = 0; i < particles.length; i++) {
                updateParticle(particles[i]);
                drawParticle(particles[i]);
            }
            requestAnimationFrame(animate);
        }

        animate();

        // Save state before navigating away so the next page can restore it
        window.addEventListener('pagehide', function () {
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(particles));
            } catch (e) {}
        });

        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(resize, 120);
        });
    }

    document.addEventListener('DOMContentLoaded', initParticles);
}());