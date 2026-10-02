document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // SEARCH SCANS
    // ==============================

    const searchInput = document.getElementById("searchInput");
    const tableRows = document.querySelectorAll("tbody tr");

    if (searchInput) {

        searchInput.addEventListener("input", function () {

            const searchValue = this.value.toLowerCase().trim();

            tableRows.forEach(function (row) {

                const rowText = row.textContent.toLowerCase();

                if (rowText.includes(searchValue)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    }


    // ==============================
    // FILTER SCANS
    // ==============================

    const filterSelect = document.getElementById("statusFilter");

    if (filterSelect) {

        filterSelect.addEventListener("change", function () {

            const selectedStatus = this.value.toLowerCase();

            tableRows.forEach(function (row) {

                const statusElement = row.querySelector(".status");

                if (!statusElement) {
                    return;
                }

                const statusText =
                    statusElement.textContent.toLowerCase();

                if (
                    selectedStatus === "all" ||
                    statusText.includes(selectedStatus)
                ) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        });

    }


    // ==============================
    // IMAGE PREVIEW
    // ==============================

    const plantImages = document.querySelectorAll(".plant-image");

    plantImages.forEach(function (image) {

        image.addEventListener("click", function () {

            const modal = document.createElement("div");

            modal.className = "image-modal";

            modal.innerHTML = `
                <div class="image-modal-content">

                    <button class="close-modal">
                        ×
                    </button>

                    <img src="${this.src}" alt="Plant Scan">

                </div>
            `;

            document.body.appendChild(modal);

            // Close button
            const closeButton =
                modal.querySelector(".close-modal");

            closeButton.addEventListener("click", function () {
                modal.remove();
            });

            // Close by clicking outside image
            modal.addEventListener("click", function (event) {

                if (event.target === modal) {
                    modal.remove();
                }

            });

        });

    });


    // ==============================
    // ESC KEY CLOSE MODAL
    // ==============================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            const modal =
                document.querySelector(".image-modal");

            if (modal) {
                modal.remove();
            }

        }

    });


    // ==============================
    // TABLE ROW HOVER
    // ==============================

    tableRows.forEach(function (row) {

        row.addEventListener("mouseenter", function () {
            this.classList.add("row-active");
        });

        row.addEventListener("mouseleave", function () {
            this.classList.remove("row-active");
        });

    });

});