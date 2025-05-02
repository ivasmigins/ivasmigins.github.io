export function loadBackground(count = 25) {
    const toggle = document.getElementById('darkModeToggle');
    const icon = toggle.querySelector('.mode-icon');
    const body = document.body;

    const darkStored = localStorage.getItem('darkMode') === 'true';
    if (darkStored) {
        body.classList.add('dark-mode');
        icon.textContent = '☀️';
    }

    toggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        icon.textContent = isDark ? '☀️' : '🌕';
        localStorage.setItem('darkMode', isDark);
    });

    const squares = document.querySelector(".floating-squares");

    for (let i = 0; i < count; i++) {
        const square = document.createElement("div");
        square.className = "square";
        square.style.top = `${Math.random() * 100}%`;
        square.style.left = `${Math.random() * 100}%`;
        square.style.animationDelay = `${Math.random() * 10}s`;
        square.style.opacity = 0.1 + Math.random() * 0.2;
        squares.appendChild(square);
    }
}