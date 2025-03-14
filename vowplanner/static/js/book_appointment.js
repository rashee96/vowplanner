document.addEventListener("DOMContentLoaded", function () {
    let selectedDate = null;
    let calendarEl = document.getElementById("calendar");
    let confirmBookingBtn = document.getElementById("confirmBooking");

    if (!calendarEl || !confirmBookingBtn) {
        console.error("❌ Calendar or Confirm Button not found!");
        return;
    }

    // ✅ Get package ID from the HTML
    let packageId = calendarEl.dataset.packageId;
    if (!packageId) {
        console.error("❌ Package ID not found!");
        return;
    }

    let csrfTokenInput = document.getElementById("csrf_token");
    if (!csrfTokenInput) {
        console.error("❌ CSRF Token not found!");
        return;
    }
    let csrfToken = csrfTokenInput.value;

    let bookingUrl = confirmBookingBtn.dataset.url;
    let unavailableDates = new Set();  // Store unavailable dates

    console.log("✅ Package ID:", packageId);
    console.log("✅ Booking URL:", bookingUrl);
    console.log("✅ CSRF Token:", csrfToken);

    // ✅ Fetch unavailable dates from backend
    fetch(`/packages/${packageId}/get_availability/`)
        .then(response => response.json())
        .then(events => {
            console.log("📅 Unavailable dates:", events);
            events.forEach(event => unavailableDates.add(event.start));

            // ✅ Initialize the Calendar AFTER fetching unavailable dates
            let calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: "dayGridMonth",
                selectable: true,
                events: events, // Load unavailable dates
                dateClick: function (info) {
                    if (unavailableDates.has(info.dateStr)) {
                        alert("⚠ This date is unavailable. Please select another.");
                        return;
                    }
                    selectedDate = info.dateStr;
                    confirmBookingBtn.disabled = false;
                    console.log("📅 Selected Date:", selectedDate);
                }
            });

            calendar.render();
        })
        .catch(error => console.error("❌ Error fetching unavailable dates:", error));

    confirmBookingBtn.addEventListener("click", function () {
        if (!selectedDate) {
            console.warn("⚠ No date selected!");
            return;
        }

        // ✅ Prevent booking an unavailable date
        if (unavailableDates.has(selectedDate)) {
            alert("❌ This date is already booked. Please select another.");
            return;
        }

        console.log("📤 Sending booking request...");

        fetch(bookingUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({date: selectedDate})
        })
            .then(response => response.json())
            .then(data => {
                console.log("✅ Response received:", data);

                if (data.success) {
                    alert("🎉 Appointment booked successfully!");
                    window.location.href = data.redirect_url;
                } else {
                    alert("❌ Error: " + data.error);
                }
            })
            .catch(error => {
                console.error("❌ Fetch Error:", error);
            });
    });
});