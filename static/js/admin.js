// =====================================================
// PlantAI Admin Panel JavaScript
// =====================================================

// =====================================================
// SIDEBAR TOGGLE
// =====================================================

function toggleSidebar() {

```
const sidebar = document.getElementById("sidebar");

if (sidebar) {
    sidebar.classList.toggle("active");
}
```

}

// =====================================================
// USER SEARCH
// =====================================================

function searchUsers() {

```
const input = document.getElementById("userSearch");
const table = document.getElementById("usersTable");

if (!input || !table) {
    return;
}

const searchText = input.value.toLowerCase().trim();

const rows = table.querySelectorAll("tbody tr");

rows.forEach(function(row) {

    const text = row.innerText.toLowerCase();

    if (text.includes(searchText)) {
        row.style.display = "";
    } else {
        row.style.display = "none";
    }

});
```

}

// =====================================================
// VIEW USER
// =====================================================

function viewUser(userId) {

```
const row = document.querySelector(
    `.action-btn[onclick="viewUser('${userId}')"]`
);

if (!row) {
    alert("User information not found.");
    return;
}

const tableRow = row.closest("tr");

if (!tableRow) {
    return;
}

const name =
    tableRow.cells[0].innerText.trim();

const email =
    tableRow.cells[1].innerText.trim();

const scans =
    tableRow.cells[2].innerText.trim();

const joined =
    tableRow.cells[3].innerText.trim();

alert(
    "User Details\n\n" +
    "User ID: " + userId + "\n" +
    "Name: " + name + "\n" +
    "Email: " + email + "\n" +
    "Scans: " + scans + "\n" +
    "Joined: " + joined
);
```

}

// =====================================================
// EXPORT REPORT
// =====================================================

function exportReport() {

```
window.print();
```

}

// =====================================================
// NOTIFICATION
// =====================================================

function showNotifications() {

```
alert(
    "PlantAI Notifications\n\n" +
    "You have 3 new notifications."
);
```

}

// =====================================================
// PAGE LOAD
// =====================================================

document.addEventListener("DOMContentLoaded", function() {

```
// =================================================
// SIDEBAR NAVIGATION
// =================================================

const navItems =
    document.querySelectorAll(".nav-item");

navItems.forEach(function(item) {

    item.addEventListener("click", function() {

        navItems.forEach(function(nav) {

            nav.classList.remove("active");

        });

        this.classList.add("active");

    });

});


// =================================================
// NOTIFICATION BUTTON
// =================================================

const notification =
    document.querySelector(".notification");

if (notification) {

    notification.addEventListener("click", function() {

        showNotifications();

    });

}


// =================================================
// ADD USER
// =================================================

const addUserButton =
    document.querySelector("#users .primary-btn");

if (addUserButton) {

    addUserButton.addEventListener("click", function() {

        alert(
            "Add User feature is coming soon."
        );

    });

}


// =================================================
// ADD DISEASE
// =================================================

const addDiseaseButton =
    document.querySelector("#diseases .primary-btn");

if (addDiseaseButton) {

    addDiseaseButton.addEventListener("click", function() {

        alert(
            "Add Disease feature is coming soon."
        );

    });

}


// =================================================
// SETTINGS SWITCHES
// =================================================

const settings =
    document.querySelectorAll(
        '.settings-panel input[type="checkbox"]'
    );

settings.forEach(function(setting) {

    setting.addEventListener("change", function() {

        const row =
            this.closest(".setting-row");

        if (!row) {
            return;
        }

        const title =
            row.querySelector("h3");

        if (!title) {
            return;
        }

        if (this.checked) {

            console.log(
                title.innerText + " enabled"
            );

        } else {

            console.log(
                title.innerText + " disabled"
            );

        }

    });

});


// =================================================
// LOGOUT CONFIRMATION
// =================================================

const logout =
    document.querySelector(
        ".sidebar-bottom .logout"
    );

if (logout) {

    logout.addEventListener("click", function(event) {

        const confirmLogout =
            confirm(
                "Are you sure you want to logout?"
            );

        if (!confirmLogout) {

            event.preventDefault();

        }

    });

}
```

});
