// web_all Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('web_all Dashboard loaded');
    
    // Add any global initialization here
    initializeAnimations();
});

function initializeAnimations() {
    // Add fade-in animations to feature cards
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s, transform 0.5s';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}
