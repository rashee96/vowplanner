document.querySelectorAll(".delete-booking").forEach(button => {
        button.addEventListener("click", function () {
            let bookingId = this.dataset.bookingId;
            let row = document.getElementById(`booking-${bookingId}`);

            let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
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

                            // ✅ Check if there are any more bookings left
                            const tbody = document.querySelector("table tbody");
                            if (!tbody.querySelector("tr")) {
                                tbody.innerHTML = `
                                    <tr>
                                        <td colspan="5" class="text-center">No bookings found.</td>
                                    </tr>
                                `;
                            }
                        } else {
                            alert("❌ Error: " + data.error);
                        }
                    })
                    .catch(error => console.error("❌ Fetch Error:", error));
            }
        });
    });