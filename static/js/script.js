// =====================================================
// ---------- PARTIKEL-ANIMATION ----------
// =====================================================

function initParticles() {

    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resizeCanvas();

    const particles = [];
    const particleCount = 100;

    class Particle {

        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = canvas.height + Math.random() * 100;
            this.size = Math.random() * 3 + 1;
            this.speedY = Math.random() * 1 + 0.5;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.5 + 0.3;
        }

        update() {
            this.y -= this.speedY;
            this.x += this.speedX;

            if (this.y < -10) {
                this.reset();
            }
        }

        draw() {
            ctx.fillStyle = `rgba(99,102,241,${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            p.update();
            p.draw();
        });

        requestAnimationFrame(animate);
    }

    animate();

    // Debounced Resize (Performance)
    let resizeTimeout;

    window.addEventListener('resize', () => {

        clearTimeout(resizeTimeout);

        resizeTimeout = setTimeout(() => {
            resizeCanvas();
        }, 100);
    });
}


// =====================================================
// ---------- SCROLL ANIMATION ----------
// =====================================================

function animateOnScroll() {

    const elements = document.querySelectorAll('.card, .paper, .product, .team-member');

    const observer = new IntersectionObserver(entries => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });

    }, { threshold: 0.1 });

    elements.forEach(el => {

        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';

        observer.observe(el);
    });
}


// =====================================================
// ---------- PRODUKT TABS ----------
// =====================================================

function showTab(productId, tabName) {

    const container = document.querySelector(`#product-${productId}`) || document;

    const tabs = container.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    const contents = container.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    const activeContent = document.getElementById(`${productId}-${tabName}`);

    if (activeContent) {
        activeContent.classList.add('active');
    }
}


// =====================================================
// ---------- DOKUMENTATIONS NAVIGATION ----------
// =====================================================

function showDocsSection(event, sectionId) {

    if (event) event.preventDefault();

    const sections = document.querySelectorAll('.docs-section');

    sections.forEach(section => {
        section.style.display = 'none';
    });

    const activeSection = document.getElementById(sectionId + '-section');

    if (activeSection) {
        activeSection.style.display = 'block';
    }

    const links = document.querySelectorAll('.docs-sidebar a');

    links.forEach(link => link.classList.remove('active'));

    if (event) {
        event.target.classList.add('active');
    }

    // URL Hash setzen (Deep Linking)
    history.replaceState(null, null, "#" + sectionId);
}


// =====================================================
// ---------- FORM DEMOS ----------
// =====================================================

function handleSubmit(e) {
    e.preventDefault();
    alert('Vielen Dank für Ihre Nachricht!');
    e.target.reset();
}

function handleLogin(e) {
    e.preventDefault();
    alert('Login erfolgreich!');
    window.location.href = '/';
}

function handleRegister(e) {
    e.preventDefault();
    alert('Registrierung erfolgreich!');
    window.location.href = '/login';
}

function handleForgotPassword(e) {
    e.preventDefault();
    alert('Reset Link gesendet.');
    window.location.href = '/login';
}


// =====================================================
// ---------- INITIALISIERUNG ----------
// =====================================================

document.addEventListener('DOMContentLoaded', function() {

    initParticles();
    animateOnScroll();
    updateCartCountFromServer();

    // Docs Deep Link Support
    const hash = window.location.hash.replace("#", "");

    if (hash) {
        showDocsSection(null, hash);
    }
});
