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
        let newRow = document.createElement("tr");
        newRow.classList.add("quotation-line");
        newRow.innerHTML = `
                    <td><input type="text" name="description" class="form-control"></td>
                    <td style="text-align: center;"><input type="number" name="lines-0-price" class="form-control w-50 mx-auto" step="0.01"></td>
                    <td style="text-align: center;"><button type="button" class="btn btn-danger btn-sm remove-line">Remove</button></td>
                `;
        document.querySelector("#quotationTable tbody").appendChild(newRow);
        updateTotals();
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