function togglePassword() {
    const input = document.getElementById("password");
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
}

function continueAsGuest() {
    window.location.href = "/guest";
}
