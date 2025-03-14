document.addEventListener("DOMContentLoaded", function () {
    const priceRange = document.getElementById("priceRange");
    const priceValue = document.getElementById("priceValue");
    const minPriceInput = document.getElementById("min_price");
    const maxPriceInput = document.getElementById("max_price");

    // ✅ Update price value display on slider change
    priceRange.addEventListener("input", function () {
        maxPriceInput.value = this.value;
        priceValue.innerText = minPrice + " - " + this.value + " LKR";
    });

    // ✅ Reset price filter when vendor type changes
    vendorType.addEventListener("change", function () {
        priceRange.value = maxPrice;  // Reset slider to max
        maxPriceInput.value = maxPrice;
        priceValue.innerText = minPrice + " - " + maxPrice + " LKR";
    });
});