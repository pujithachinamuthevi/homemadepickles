// ─── Navbar scroll effect ──────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('mainNav');
  if (nav) {
    nav.style.boxShadow = window.scrollY > 40
      ? '0 4px 24px rgba(0,0,0,0.12)'
      : '0 2px 16px rgba(0,0,0,0.07)';
  }
});

// ─── Payment option selection ──────────────────────────────────
document.querySelectorAll('.payment-option').forEach(option => {
  option.addEventListener('click', () => {
    document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
    option.classList.add('selected');
  });
});

// ─── Auto-dismiss flash messages ───────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(alert => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    bsAlert.close();
  });
}, 4000);

// ─── Cart quantity buttons ─────────────────────────────────────
document.querySelectorAll('.qty-form .qty-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    // Allow form submit naturally
  });
});

// ─── Animate on scroll (simple) ───────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .review-card, .value-card, .feature-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
