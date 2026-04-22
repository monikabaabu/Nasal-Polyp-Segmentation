// ── DOM ELEMENTS ───────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
const uploadArea      = document.getElementById('uploadArea');
const fileInput       = document.getElementById('fileInput');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const previewImage    = document.getElementById('previewImage');
const analyzeBtn      = document.getElementById('analyzeBtn');
const modelSelect     = document.getElementById('model');
const loading         = document.getElementById('loading');
const results         = document.getElementById('results');
const severityBadge   = document.getElementById('severityBadge');
const polypArea       = document.getElementById('polypArea');
const polypPixels     = document.getElementById('polypPixels');
const modelUsed       = document.getElementById('modelUsed');
const originalImage   = document.getElementById('originalImage');
const maskImage       = document.getElementById('maskImage');
const overlayImage    = document.getElementById('overlayImage');
const changeBtn = document.getElementById("changeBtn");

changeBtn.addEventListener("click", () => {
    fileInput.click();
});
previewImage.addEventListener('click', (e) => {
    e.stopPropagation();
});

// ── UPLOAD HANDLING ────────────────────────────────────────────
uploadArea.addEventListener('click', () => {
    // only allow click when NO image is shown
    if (previewImage.style.display !== 'block') {
        fileInput.click();
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#6d8af1';
    uploadArea.style.background  = 'rgba(61, 90, 241, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#3d5af1';
    uploadArea.style.background  = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#3d5af1';
    uploadArea.style.background  = 'transparent';
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    // show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src       = e.target.result;
        previewImage.style.display  = 'block';
        uploadPlaceholder.style.display = 'none';
        originalImage.src      = e.target.result;
    };
    reader.readAsDataURL(file);

    // enable analyze button
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze CT Scan';

    // hide previous results
    results.style.display = 'none';
    changeBtn.style.display = "block";
}

// ── ANALYZE BUTTON ─────────────────────────────────────────────
analyzeBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const selectedModel = modelSelect.value;

    // show loading
    loading.style.display  = 'block';
    results.style.display  = 'none';
    analyzeBtn.disabled    = true;
    analyzeBtn.textContent = 'Analyzing...';

    // build form data
    const formData = new FormData();
    formData.append('file',  file);
    formData.append('model', selectedModel);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body:   formData
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        // ── show results ───────────────────────────────────────
        loading.style.display  = 'none';
        results.style.display  = 'block';

        // severity badge
        severityBadge.textContent  = data.severity;
        severityBadge.className    = 'severity-badge severity-' + data.severity_color;

        // stats
        polypArea.textContent   = data.polyp_area_mm2 + ' mm²';
        polypPixels.textContent = data.polyp_pixels + ' px';
        modelUsed.textContent   = selectedModel;

        // images
        maskImage.src    = 'data:image/png;base64,' + data.mask;
        overlayImage.src = 'data:image/png;base64,' + data.overlay;

        // scroll to results
        results.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        alert('Something went wrong: ' + err.message);
    } finally {
        loading.style.display  = 'none';
        analyzeBtn.disabled    = false;
        analyzeBtn.textContent = 'Analyze CT Scan';
    }
});});