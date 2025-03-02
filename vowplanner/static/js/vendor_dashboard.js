function toggleDoneButton(packageId) {
    let reasonField = document.getElementById("archiveReason-" + packageId);
    let doneButton = document.getElementById("archiveDone-" + packageId);

    if (reasonField.value.trim().length > 0) {
        doneButton.style.display = "block";  // Show "Done" button
    } else {
        doneButton.style.display = "none";  // Hide "Done" button if empty
    }
}

function archivePackage(packageId) {
    let reasonField = document.getElementById("archiveReason-" + packageId);
    let reason = reasonField.value.trim();
    let packageRow = document.getElementById("package-row-" + packageId);
    let modal = document.getElementById("archiveModal-" + packageId);

    if (reason.length === 0) {
        alert("Please enter a reason before archiving.");
        return;
    }

    fetch(`/users/vendor/package/archive/${packageId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({reason: reason})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                packageRow.remove();
                alert("Package archived successfully!");


                let bootstrapModal = bootstrap.Modal.getInstance(modal);
                bootstrapModal.hide();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
}

document.addEventListener("DOMContentLoaded", function () {
    let calendarEl = document.getElementById("calendar");
    let selectedDate;  // Store the selected date

    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        selectable: true,
        editable: true,
        events: "/users/fetch_google_events/",  // ✅ Fetch Google Calendar events

        select: function (info) {
            selectedDate = info.startStr;
            document.getElementById("eventDate").value = selectedDate;
            let addEventModal = new bootstrap.Modal(document.getElementById("addEventModal"));
            addEventModal.show();
        },

        eventClick: function (info) {
            document.getElementById("deleteEventId").value = info.event.id;
            let deleteEventModal = new bootstrap.Modal(document.getElementById("deleteEventModal"));
            deleteEventModal.show();
        }
    });

    calendar.render();

    // Add Event
    document.getElementById("saveEventBtn").addEventListener("click", function () {
        let eventTitle = document.getElementById("eventTitle").value;
        if (!eventTitle.trim()) {
            alert("Event title is required!");
            return;
        }

        fetch("/users/add_google_event/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({title: eventTitle, date: selectedDate}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    calendar.refetchEvents();
                    document.getElementById("eventTitle").value = "";  // Clear input
                    bootstrap.Modal.getInstance(document.getElementById("addEventModal")).hide();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
    });

    // Delete Event
    document.getElementById("confirmDeleteEventBtn").addEventListener("click", function () {
        let eventId = document.getElementById("deleteEventId").value;

        fetch("/users/delete_google_event/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({event_id: eventId}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    calendar.refetchEvents();
                    bootstrap.Modal.getInstance(document.getElementById("deleteEventModal")).hide();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const reauthorizeBtn = document.getElementById("reauthorizeGoogleBtn");
    if (reauthorizeBtn) {
        reauthorizeBtn.addEventListener("click", function () {
            window.location.href = "{% url 'google_auth' %}"; // Replace with your actual URL
        });
    }
});