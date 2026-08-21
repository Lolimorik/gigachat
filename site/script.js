// Скрипт для плавного появления элементов при скроллинге

document.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section');

    sections.forEach((section) => {
        // Проверяем, достаточно ли прокручено страницы, чтобы элемент начал появляться
        const triggerPoint = section.getBoundingClientRect().top + window.innerHeight * 0.5;

        if (triggerPoint <= 0 && !section.classList.contains('shown')) {
            // Элемент начинает показываться
            section.classList.add('shown');

            // Добавляем анимацию появления
            section.style.animation = 'fadeIn 1s forwards';
        }
    });
});

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}