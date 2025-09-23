document.addEventListener("DOMContentLoaded", function () {
    let sidebar = document.getElementById("sidebar");

    window.expandSidebar = function () {
        sidebar.style.width = "250px";
        document.querySelectorAll("#sidebar span").forEach(el => el.classList.remove("d-none"));
    };

    window.collapseSidebar = function () {
        sidebar.style.width = "80px";
        document.querySelectorAll("#sidebar span").forEach(el => el.classList.add("d-none"));
    };
});
