// script.js
document.addEventListener('DOMContentLoaded', () => {
    const containerModal = document.getElementById('newContainerModal');
    const locationModal = document.getElementById('newLocationModal');
    const containerBtn = document.querySelector('#standard-container-types');
    const shippingLocationBtn = document.querySelector('#standard-shipping-location');
    const destinationLocationBtn = document.querySelector('#standard-destination-location');
    const containerClose = containerModal.getElementsByClassName('close')[0];
    const locationClose = locationModal.getElementsByClassName('close')[0];

    // Show modals
    containerBtn.addEventListener('change', function() {
        if (this.value === 'add-new-container') {
            containerModal.style.display = 'block';
        }
    });

    shippingLocationBtn.addEventListener('change', function() {
        if (this.value === 'add-new-location') {
            locationModal.style.display = 'block';
        }
    });

    destinationLocationBtn.addEventListener('change', function() {
        if (this.value === 'add-new-destination') {
            locationModal.style.display = 'block';
        }
    });

    // Close modals
    containerClose.onclick = function() {
        containerModal.style.display = 'none';
    }

    locationClose.onclick = function() {
        locationModal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == containerModal) {
            containerModal.style.display = 'none';
        }
        if (event.target == locationModal) {
            locationModal.style.display = 'none';
        }
    }

    // Validate positive numbers
    const positiveNumberFields = document.querySelectorAll('input[type="number"]');
    positiveNumberFields.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });

        // Prevent negative input on keypress
        input.addEventListener('keypress', function(event) {
            const key = event.key;
            if (key === '-' || key === '+') {
                event.preventDefault();
            }
        });

        // Prevent pasting negative values
        input.addEventListener('paste', function(event) {
            const paste = (event.clipboardData || window.clipboardData).getData('text');
            if (paste.includes('-')) {
                event.preventDefault();
            }
        });
    });

    // Handle form submission
    document.getElementById('newContainerForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/add-container/', {
            method: 'POST',
            body: JSON.stringify({
                containerName: formData.get('containerName'),
                containerLength: formData.get('containerLength'),
                containerWidth: formData.get('containerWidth'),
                containerHeight: formData.get('containerHeight')
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Container added successfully');
                containerModal.style.display = 'none';
            } else {
                alert('Error adding container');
            }
        });
    });

    document.getElementById('newLocationForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/add-location/', {
            method: 'POST',
            body: JSON.stringify({
                locationName: formData.get('locationName')
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Location added successfully');
                locationModal.style.display = 'none';
            } else {
                alert('Error adding location');
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    // Select the reload button and the settings form
    const reloadButton = document.getElementById('reloadButton');
    const settingsForm = document.getElementById('settingsForm');

    // Add a click event listener to the reload button
    if (reloadButton && settingsForm) {
        reloadButton.addEventListener('click', () => {
            // Find all select elements within the form
            const selectElements = settingsForm.querySelectorAll('select');
            
            // Iterate over each select element and reset to the first option
            selectElements.forEach(select => {
                select.selectedIndex = 0; // Set to the first option
            });

            console.log('Form has been reset to default values.');
        });
    }
});

