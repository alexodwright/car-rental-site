const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        } else {
            entry.target.classList.remove('show');
        }
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const label = document.querySelector("#input");
    const slider = document.querySelector("#price_range");
    const hiddenElements = document.querySelectorAll('.hidden');
    hiddenElements.forEach((element) => observer.observe(element));
    label.innerHTML = slider.value
    slider.addEventListener("input", () => {
        label.innerHTML = slider.value;
    }, false);
}, false);
