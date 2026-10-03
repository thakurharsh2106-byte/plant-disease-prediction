/**
 * PlantGuard AI - Interactive Frontend Core
 */

document.addEventListener('DOMContentLoaded', () => {
  initFileUpload();
  initCamera();
  initSampleChips();
  initMarketplace();
  initEncyclopedia();
});

// ==========================================================================
// 1. File Upload & Drag-and-Drop
// ==========================================================================
function initFileUpload() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const previewArea = document.getElementById('preview-area');
  const previewImg = document.getElementById('preview-img');
  const fileInfo = document.getElementById('file-info');
  const removeBtn = document.getElementById('remove-file-btn');
  const uploadPrompt = document.getElementById('upload-prompt');
  const submitBtn = document.getElementById('diagnose-submit-btn');

  if (!dropzone || !fileInput) return;

  // Click dropzone to open file picker
  dropzone.addEventListener('click', (e) => {
    if (e.target.closest('#remove-file-btn') || e.target.closest('#open-camera-btn')) return;
    fileInput.click();
  });

  // Drag over / leave
  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  // Drop files
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      fileInput.files = dt.files;
      handleFileSelected(dt.files[0]);
    }
  });

  // File input change
  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  // Remove file
  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.value = '';
      previewArea.style.display = 'none';
      uploadPrompt.style.display = 'block';
      if (submitBtn) submitBtn.disabled = true;
    });
  }

  function handleFileSelected(file) {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please select a valid image file (JPG, PNG, WebP).');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewArea.style.display = 'block';
      uploadPrompt.style.display = 'none';
      if (fileInfo) {
        const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
        fileInfo.textContent = `${file.name} (${sizeMb} MB)`;
      }
      if (submitBtn) submitBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  // Handle Form Submission Spinner
  const diagnosisForm = document.getElementById('diagnosis-form');
  if (diagnosisForm) {
    diagnosisForm.addEventListener('submit', () => {
      const loader = document.getElementById('analysis-loader');
      if (loader) loader.style.display = 'flex';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Running PyTorch Neural Analysis...
        `;
      }
    });
  }
}

// ==========================================================================
// 2. Real-Time Camera Stream & Capture
// ==========================================================================
let cameraStream = null;

function initCamera() {
  const openCameraBtn = document.getElementById('open-camera-btn');
  const cameraModal = document.getElementById('camera-modal');
  const closeCameraBtn = document.getElementById('close-camera-btn');
  const videoFeed = document.getElementById('camera-video-feed');
  const shutterBtn = document.getElementById('shutter-btn');
  const fileInput = document.getElementById('file-input');
  const previewImg = document.getElementById('preview-img');
  const previewArea = document.getElementById('preview-area');
  const uploadPrompt = document.getElementById('upload-prompt');
  const fileInfo = document.getElementById('file-info');
  const submitBtn = document.getElementById('diagnose-submit-btn');

  if (!openCameraBtn || !cameraModal) return;

  openCameraBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    cameraModal.style.display = 'flex';
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });
      if (videoFeed) {
        videoFeed.srcObject = cameraStream;
        videoFeed.play();
      }
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Unable to access device camera. Please check your browser permissions.');
      closeCamera();
    }
  });

  function closeCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
    }
    if (videoFeed) {
      videoFeed.srcObject = null;
    }
    cameraModal.style.display = 'none';
  }

  if (closeCameraBtn) {
    closeCameraBtn.addEventListener('click', closeCamera);
  }

  cameraModal.addEventListener('click', (e) => {
    if (e.target === cameraModal) {
      closeCamera();
    }
  });

  if (shutterBtn && videoFeed) {
    shutterBtn.addEventListener('click', () => {
      const canvas = document.createElement('canvas');
      canvas.width = videoFeed.videoWidth || 640;
      canvas.height = videoFeed.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoFeed, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (!blob) return;
        const capturedFile = new File([blob], `leaf_snapshot_${Date.now()}.jpg`, { type: 'image/jpeg' });
        
        // Attach to file input via DataTransfer
        if (fileInput) {
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(capturedFile);
          fileInput.files = dataTransfer.files;
        }

        // Update preview
        const dataUrl = canvas.toDataURL('image/jpeg');
        if (previewImg) previewImg.src = dataUrl;
        if (previewArea) previewArea.style.display = 'block';
        if (uploadPrompt) uploadPrompt.style.display = 'none';
        if (fileInfo) fileInfo.textContent = `Camera Snapshot (${(blob.size / 1024).toFixed(1)} KB)`;
        if (submitBtn) submitBtn.disabled = false;

        closeCamera();
      }, 'image/jpeg', 0.95);
    });
  }
}

// ==========================================================================
// 3. Quick Demo Sample Chips
// ==========================================================================
function initSampleChips() {
  const chips = document.querySelectorAll('.sample-leaf-chip');
  const fileInput = document.getElementById('file-input');
  const previewImg = document.getElementById('preview-img');
  const previewArea = document.getElementById('preview-area');
  const uploadPrompt = document.getElementById('upload-prompt');
  const fileInfo = document.getElementById('file-info');
  const submitBtn = document.getElementById('diagnose-submit-btn');

  if (!chips || chips.length === 0) return;

  chips.forEach(chip => {
    chip.addEventListener('click', async () => {
      const imgPath = chip.getAttribute('data-img-src');
      const filename = chip.getAttribute('data-filename');
      const label = chip.getAttribute('data-label');

      try {
        const resp = await fetch(imgPath);
        const blob = await resp.blob();
        const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });

        if (fileInput) {
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(file);
          fileInput.files = dataTransfer.files;
        }

        if (previewImg) previewImg.src = imgPath;
        if (previewArea) previewArea.style.display = 'block';
        if (uploadPrompt) uploadPrompt.style.display = 'none';
        if (fileInfo) fileInfo.textContent = `${label} (${(blob.size / 1024).toFixed(1)} KB)`;
        if (submitBtn) {
          submitBtn.disabled = false;
          // Smooth scroll to submit button
          submitBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } catch (err) {
        console.error('Failed to load sample image:', err);
      }
    });
  });
}

// ==========================================================================
// 4. Marketplace Search & Filter
// ==========================================================================
function initMarketplace() {
  const searchInput = document.getElementById('market-search');
  const filterBtns = document.querySelectorAll('.market-filter-btn');
  const productCards = document.querySelectorAll('.market-product-col');
  const emptyState = document.getElementById('market-empty-state');

  if (!productCards || productCards.length === 0) return;

  let currentCategory = 'all';
  let currentSearch = '';

  function filterCards() {
    let visibleCount = 0;
    productCards.forEach(col => {
      const category = col.getAttribute('data-category'); // 'healthy' or 'diseased'
      const plant = (col.getAttribute('data-plant') || '').toLowerCase();
      const name = (col.getAttribute('data-name') || '').toLowerCase();
      const disease = (col.getAttribute('data-disease') || '').toLowerCase();

      const matchesCategory = (currentCategory === 'all') || (category === currentCategory);
      const matchesSearch = !currentSearch || name.includes(currentSearch) || disease.includes(currentSearch) || plant.includes(currentSearch);

      if (matchesCategory && matchesSearch) {
        col.style.display = 'block';
        visibleCount++;
      } else {
        col.style.display = 'none';
      }
    });

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      filterCards();
    });
  }

  if (filterBtns) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.getAttribute('data-filter');
        filterCards();
      });
    });
  }
}

// ==========================================================================
// 5. Encyclopedia Search & Filter
// ==========================================================================
function initEncyclopedia() {
  const searchInput = document.getElementById('encyclopedia-search');
  const cropSelect = document.getElementById('encyclopedia-crop-select');
  const diseaseCards = document.querySelectorAll('.disease-card-col');
  const emptyState = document.getElementById('encyclopedia-empty-state');

  if (!diseaseCards || diseaseCards.length === 0) return;

  function filterEncyclopedia() {
    const search = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const selectedCrop = cropSelect ? cropSelect.value.trim().toLowerCase() : 'all';

    let count = 0;
    diseaseCards.forEach(card => {
      const plant = (card.getAttribute('data-plant') || '').toLowerCase();
      const name = (card.getAttribute('data-name') || '').toLowerCase();
      const desc = (card.getAttribute('data-desc') || '').toLowerCase();

      const matchesCrop = (selectedCrop === 'all') || (plant === selectedCrop);
      const matchesSearch = !search || name.includes(search) || desc.includes(search) || plant.includes(search);

      if (matchesCrop && matchesSearch) {
        card.style.display = 'block';
        count++;
      } else {
        card.style.display = 'none';
      }
    });

    if (emptyState) {
      emptyState.style.display = count === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) searchInput.addEventListener('input', filterEncyclopedia);
  if (cropSelect) cropSelect.addEventListener('change', filterEncyclopedia);
}
