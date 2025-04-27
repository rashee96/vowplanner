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

    fetch(`/packages/vendor/package/archive/${packageId}/`, {
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
        events: "/events/get_all_events/",  // Fetch from both DB & Google

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
        },
        eventDidMount: function (info) {
            if (info.event.extendedProps.state === "booked") {
                info.el.style.backgroundColor = "#28a745";
            } else if (info.event.extendedProps.state === "on_hold") {
                info.el.style.backgroundColor = "#ffc107";
            }
        }
    });

    calendar.render();

    // Add Event with Additional Details
    document.getElementById("saveEventBtn").addEventListener("click", function () {
        let eventTitle = document.getElementById("eventTitle").value.trim();
        let customerName = document.getElementById("customerName").value.trim();
        let customerEmail = document.getElementById("customerEmail").value.trim();
        let contactNumber = document.getElementById("contactNumber").value.trim();
        let eventDate = document.getElementById("eventDate").value;
        let eventStatus = document.getElementById("eventStatus").value;
        let vendorPackage = document.getElementById("vendorPackage").value;

        if (!eventTitle || !customerName || !contactNumber || !eventDate || !customerEmail || !vendorPackage) {
            alert("Please fill in all required fields.");
            return;
        }

        let eventData = {
            title: eventTitle,
            customer_name: customerName,
            email: customerEmail,
            contact_no: contactNumber,
            date: eventDate,
            status: eventStatus,
            vendor_package: vendorPackage
        };

        fetch("/events/create_event/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
                "Content-Type": "application/json",
            },
            body: JSON.stringify(eventData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    calendar.refetchEvents();
                    document.getElementById("addEventForm").reset();
                    bootstrap.Modal.getInstance(document.getElementById("addEventModal")).hide();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
    });

    // Delete Event from DB & Google
    document.getElementById("confirmDeleteEventBtn").addEventListener("click", function () {
        let eventId = document.getElementById("deleteEventId").value;

        fetch("/events/delete_google_event/", {
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

document.getElementById("syncEventsBtn").addEventListener("click", function () {
    fetch("/events/fetch_and_save_google_events/", {
        method: "GET",
        headers: {"X-CSRFToken": getCSRFToken()},
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Events Synced!");
                window.location.reload();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
});

document.addEventListener("DOMContentLoaded", function () {
    const reauthorizeBtn = document.getElementById("reauthorizeGoogleBtn");
    if (reauthorizeBtn) {
        reauthorizeBtn.addEventListener("click", function () {
            window.location.href = "{% url 'events:google_auth' %}"; // Replace with your actual URL
        });
    }
    // Sync Events Button
    document.getElementById("syncEventsBtn").addEventListener("click", function () {
        fetch("/events/fetch_and_save_google_events/", {
            method: "GET",
            headers: {"X-CSRFToken": getCSRFToken()},
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Events Synced!");
                    calendar.refetchEvents();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
    });
});