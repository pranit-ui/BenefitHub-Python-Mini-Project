document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('applicationModal');
    const closeBtn = modal.querySelector('.close-modal');
    const proceedBtn = document.getElementById('proceedToApplication');
    
    // Handle apply button clicks
    document.querySelectorAll('.apply-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const schemeData = JSON.parse(this.dataset.scheme);
            showApplicationSteps(schemeData);
        });
    });

    // Close modal
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    function showApplicationSteps(scheme) {
        // Update documents list based on scheme
        const documentsList = document.getElementById('required-documents');
        documentsList.innerHTML = scheme.documents.map(doc => 
            `<li>${doc}</li>`
        ).join('');

        // Show modal
        modal.style.display = "block";

        // Update proceed button link
        proceedBtn.onclick = function() {
            window.location.href = scheme.applyLink;
        }
    }
});