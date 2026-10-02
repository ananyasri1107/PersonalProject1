document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".contact-form");
    const submitButton = document.querySelector(".contact-submit-btn");

    if (!form) {
        return;
    }

    // Form submit
    form.addEventListener("submit", function (event) {

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const subject = document.getElementById("subject").value.trim();
        const message = document.getElementById("message").value.trim();

        // Basic validation
        if (!name || !email || !subject || !message) {
            event.preventDefault();

            alert("Please fill in all fields.");
            return;
        }

        // Email validation
        const emailPattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email)) {
            event.preventDefault();

            alert("Please enter a valid email address.");
            return;
        }

        // Prevent multiple clicks
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = "📨 Sending...";
        }

    });


    // Character counter for message
    const messageBox = document.getElementById("message");

    if (messageBox) {

        const counter = document.createElement("small");

        counter.className = "message-counter";

        counter.textContent = "0 characters";

        messageBox.parentNode.appendChild(counter);


        messageBox.addEventListener("input", function () {

            const length = messageBox.value.length;

            counter.textContent =
                length + " characters";

        });

    }

});