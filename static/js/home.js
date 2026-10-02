// The floating-leaf and scroll animations on this page are handled purely
// with CSS (see .moving-leaf and `scroll-behavior: smooth` in home.css).
// This file is kept as a hook for any future client-side behavior
// (e.g. scroll-spy highlighting of the active nav link).

document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".navbar nav a[href^='#']");
    const sections = Array.from(navLinks)
        .map((link) => document.querySelector(link.getAttribute("href")))
        .filter(Boolean);

    if (!("IntersectionObserver" in window) || sections.length === 0) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                navLinks.forEach((link) => {
                    link.classList.toggle(
                        "active",
                        link.getAttribute("href") === `#${entry.target.id}`
                    );
                });
            });
        },
        { rootMargin: "-50% 0px -50% 0px" }
    );

    sections.forEach((section) => observer.observe(section));
});
