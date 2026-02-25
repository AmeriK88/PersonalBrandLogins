(function () {
    const banner = document.getElementById("cookie-banner");
    if (!banner) return;

    const consent = localStorage.getItem("cookieConsent");

    // If accepted - use banner
    if (consent === "all" || consent === "essential") {
        banner.style.display = "none";
        return;
    }

    const btnAll = document.getElementById("cookie-accept-all");
    const btnEssential = document.getElementById("cookie-accept-essential");

    if (btnAll) {
        btnAll.addEventListener("click", function () {
            localStorage.setItem("cookieConsent", "all");
            banner.style.display = "none";

            // If google analityrs - this is future update
            // loadAnalytics();
        });
    }

    if (btnEssential) {
        btnEssential.addEventListener("click", function () {
            localStorage.setItem("cookieConsent", "essential");
            banner.style.display = "none";
        });
    }
})();
