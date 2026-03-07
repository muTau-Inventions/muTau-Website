/* particles.js — floating particle animation on the background canvas */

(function () {
    'use strict';

    function initParticles() {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        resize();

        const COUNT = 80;
        const particles = [];

        function Particle() {
            this.reset = function () {
                this.x       = Math.random() * canvas.width;
                this.y       = canvas.height + Math.random() * 120;
                this.size    = Math.random() * 2.5 + 0.5;
                this.speedY  = Math.random() * 0.8 + 0.3;
                this.speedX  = Math.random() * 0.4 - 0.2;
                this.opacity = Math.random() * 0.4 + 0.1;
            };
            this.reset();
        }

        Particle.prototype.update = function () {
            this.y -= this.speedY;
            this.x += this.speedX;
            if (this.y < -10) this.reset();
        };

        Particle.prototype.draw = function () {
            ctx.fillStyle = `rgba(99,102,241,${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        };

        for (let i = 0; i < COUNT; i++) {
            const p = new Particle();
            p.y = Math.random() * canvas.height; // spread on load
            particles.push(p);
        }

        let raf;

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
            }
            raf = requestAnimationFrame(animate);
        }

        animate();

        let resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(resize, 120);
        });
    }

    document.addEventListener('DOMContentLoaded', initParticles);
}());
