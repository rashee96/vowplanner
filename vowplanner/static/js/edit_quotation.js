document.addEventListener("DOMContentLoaded", function () {
    function updateTotals() {
        let subtotal = 0;
        document.querySelectorAll(".quotation-line input[name$='-price']").forEach(input => {
            subtotal += parseFloat(input.value) || 0;
        });

        let discount = parseFloat(document.getElementById("discount").value) || 0;
        let netTotal = subtotal - discount;

        document.getElementById("subtotal").textContent = subtotal.toFixed(2);
        document.getElementById("nettotal").textContent = netTotal.toFixed(2);
        document.getElementById("total_price").value = subtotal.toFixed(2);  // ✅ Set field
        document.getElementById("net_total").value = netTotal.toFixed(2);   // ✅ Set field
    }

    document.getElementById("quotationTable").addEventListener("input", updateTotals);
    document.getElementById("discount").addEventListener("input", updateTotals);

    document.getElementById("addLine").addEventListener("click", function () {
        let formIdx = document.getElementById("id_form-TOTAL_FORMS").value;
        let newRow = document.getElementById("empty-form").innerHTML.replace(/__prefix__/g, formIdx);
        document.querySelector("#quotationTable tbody").insertAdjacentHTML('beforeend', newRow);
        document.getElementById("id_form-TOTAL_FORMS").value = parseInt(formIdx) + 1;
    });

    document.getElementById("quotationTable").addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-line")) {
            event.target.closest("tr").remove();
            updateTotals();
        }
    });

    document.getElementById("quotationTable").addEventListener("input", updateTotals);
    document.getElementById("discount").addEventListener("input", updateTotals);

    document.getElementById("quotationForm").addEventListener("submit", function (event) {
        updateTotals();  // ✅ Ensure latest values are set before form submission
    });

    updateTotals();
});