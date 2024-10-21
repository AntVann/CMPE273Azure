let selectedImage = null;

document.getElementById('imageUpload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        selectedImage = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.id = 'imagePreview';
            const container = document.getElementById('imageContainer');
            container.innerHTML = '';
            container.appendChild(img);
        }
        reader.readAsDataURL(file);
    }
});

function extractText() {
    if (!selectedImage) {
        alert('Please select an image first.');
        return;
    }

    const formData = new FormData();
    formData.append('image', selectedImage);

    fetch('/extract-text', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('extractedText').textContent = data.text;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while extracting text.');
    });
}
