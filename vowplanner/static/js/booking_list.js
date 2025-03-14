document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-booking").forEach(button => {
        button.addEventListener("click", function () {
            let bookingId = this.dataset.bookingId;
            let row = document.getElementById(`booking-${bookingId}`);

            let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value; // ✅ Get CSRF token safely
            if (!csrfToken) {
                console.error("❌ CSRF Token not found!");
                return;
            }

            if (confirm("Are you sure you want to delete this booking?")) {
                fetch(`/events/delete_booking/${bookingId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert("✅ Booking deleted successfully!");
                            row.remove();
                        } else {
                            alert("❌ Error: " + data.error);
                        }
                    })
                    .catch(error => console.error("❌ Fetch Error:", error));
            }
        });
    });
});