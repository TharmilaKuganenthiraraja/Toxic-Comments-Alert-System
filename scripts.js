

function deleteComment(commentId) {
    // Ask for confirmation before deleting
    if (confirm("Are you sure you want to delete this comment?")) {
        // If the user clicks "OK", proceed with the deletion
        fetch(`/delete_comment/${commentId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.result);  // Show alert for success
            location.reload();  // Reload the page to see updated data
        })
        .catch(error => console.error('Error:', error));
    } else {
        // If the user clicks "Cancel", do nothing
        console.log('Deletion canceled');
    }
}

function filterComments(filterType) {
    // Get all rows in the comments table
    const rows = document.querySelectorAll('#comments-table tbody tr');

    rows.forEach(row => {
        // Get the class name (either 'toxic' or 'non-toxic') to determine the comment type
        const isToxic = row.classList.contains('toxic');

        // Show or hide rows based on the selected filter type
        if (filterType === 'all') {
            row.style.display = '';  // Show all comments
        } else if (filterType === 'toxic' && isToxic) {
            row.style.display = '';  // Show only toxic comments
        } else if (filterType === 'non-toxic' && !isToxic) {
            row.style.display = '';  // Show only non-toxic comments
        } else {
            row.style.display = 'none';  // Hide the rows that don't match the filter
        }
    });
}

function updateNotifications() {
    fetch('/get_toxic_comments')
    .then(response => response.json())
    .then(data => {
        let notificationCount = data.length;
        document.getElementById('notifications-count').textContent = notificationCount;

        let notificationList = document.getElementById('notifications-list');
        notificationList.innerHTML = '';  // Clear the list

        data.forEach(comment => {
            let listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            listItem.innerHTML = `<strong>Comment:</strong> ${comment.comment}<br><small><strong>Time:</strong> ${comment.timestamp}</small>`;
            notificationList.appendChild(listItem);
        });
    })
    .catch(error => console.error('Error fetching toxic comments:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    updateNotifications();
});

$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $('#content').toggleClass('active');
    })
}); 

function updateNotificationsCount() {
    $.ajax({
        url: '/notifications_count',
        type: 'GET',
        success: function (data) {
            $('#notifications-count').text(data.count);
            updateNotifications(); // Call this function to update the list
        },
        error: function () {
            console.error("Error fetching notifications count.");
        }
    });
}

// Call the function every 30 seconds to check for new notifications
setInterval(updateNotificationsCount, 60000);

// Fetch notification count on page load
updateNotificationsCount();      

