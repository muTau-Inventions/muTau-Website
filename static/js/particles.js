(function () {
    'use strict';

    var STORAGE_KEY = 'mt_particles';
    var COUNT = 80;

    function initParticles() {
        var canvas = document.getElementById('particleCanvas');
        if (!canvas) return;

        var ctx      = canvas.getContext('2d');
        var oldWidth = 0;
        var oldHeight = 0;
        var particles = [];

        function resize() {
            oldWidth  = canvas.width;
            oldHeight = canvas.height;

            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;

            // Remove particles that fell outside the new bounds
            for (var i = particles.length - 1; i >= 0; i--) {
                var p = particles[i];
                if (p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
                    particles.splice(i, 1);
                }
            }

            // Spawn replacements when the viewport grew
            if (particles.length < COUNT) {
                var toAdd = Math.min(COUNT - particles.length, 20);
                for (var k = 0; k < toAdd; k++) {
                    var nx = canvas.width  > oldWidth
                        ? oldWidth  + Math.random() * (canvas.width  - oldWidth)
                        : Math.random() * canvas.width;
                    var ny = canvas.height > oldHeight
                        ? oldHeight + Math.random() * (canvas.height - oldHeight)
                        : Math.random() * canvas.height;
                    particles.push(makeParticle(nx, ny));
                }
            }
        }

        function setup() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
            oldWidth  = canvas.width;
            oldHeight = canvas.height;
        }

        function makeParticle(x, y) {
            return {
                x:       x,
                y:       y,
                size:    Math.random() * 2.5 + 0.5,
                speedY:  Math.random() * 0.8  + 0.3,
                speedX:  Math.random() * 0.4  - 0.2,
                opacity: Math.random() * 0.4  + 0.1
            };
        }

        setup();

        // Restore from sessionStorage if available
        var restored = false;
        try {
            var saved = sessionStorage.getItem(STORAGE_KEY);
            if (saved) {
                var data = JSON.parse(saved);
                if (Array.isArray(data) && data.length > 0) {
                    for (var i = 0; i < data.length; i++) {
                        particles.push(makeParticle(data[i].x, data[i].y));
                    }
                    restored = true;
                }
            }
        } catch (e) {}

        if (!restored || particles.length === 0) {
            for (var j = 0; j < COUNT; j++) {
                particles.push(makeParticle(
                    Math.random() * canvas.width,
                    Math.random() * canvas.height
                ));
            }
        }

        function updateParticle(p) {
            p.y -= p.speedY;
            p.x += p.speedX;

            if (p.y < -10) {
                p.x       = Math.random() * canvas.width;
                p.y       = canvas.height + Math.random() * 50;
                p.size    = Math.random() * 2.5 + 0.5;
                p.speedY  = Math.random() * 0.8  + 0.3;
                p.speedX  = Math.random() * 0.4  - 0.2;
                p.opacity = Math.random() * 0.4  + 0.1;
            }

            if (p.x < -10)               p.x = canvas.width  + 10;
            if (p.x > canvas.width + 10) p.x = -10;
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