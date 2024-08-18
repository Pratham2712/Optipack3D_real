// If you want to handle click functionality instead of hover, use this script.

document.addEventListener('DOMContentLoaded', function() {
    const profileDropdown = document.querySelector('.profile-dropdown');

    profileDropdown.addEventListener('click', function() {
        const dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.style.display = (dropdownContent.style.display === 'block') ? 'none' : 'block';
    });

    // Close dropdown if clicked outside
    window.addEventListener('click', function(e) {
        if (!profileDropdown.contains(e.target)) {
            profileDropdown.querySelector('.dropdown-content').style.display = 'none';
        }
    });
});
