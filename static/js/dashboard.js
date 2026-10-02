document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("leaf_image");
    const fileNameEl = document.getElementById("file-name");
    const previewImg = document.getElementById("preview-img");
    const dropLabel = document.getElementById("drop-label");

    if (!fileInput) return;

    function showPreview(file) {
        if (!file) return;
        fileNameEl.textContent = file.name;

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.style.display = "block";
        };
        reader.readAsDataURL(file);
    }

    fileInput.addEventListener("change", () => {
        showPreview(fileInput.files[0]);
    });

    // Basic drag-and-drop support onto the same drop zone.
    ["dragover", "dragleave", "drop"].forEach((evtName) => {
        dropLabel.addEventListener(evtName, (e) => e.preventDefault());
    });

    dropLabel.addEventListener("drop", (e) => {
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            showPreview(file);
        }
    });
});
