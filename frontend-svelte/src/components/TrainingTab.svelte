<script>
  import { onMount } from 'svelte'
  import { apiService } from '../utils/api.js'
  
  export let showToast, status
  
  let realImages = []
  let fakeImages = []
  let training = false
  let dragCategory = null
  
  onMount(() => {
    loadImages()
  })
  
  async function loadImages() {
    try {
      const [real, fake] = await Promise.all([
        apiService.listRealImages(),
        apiService.listFakeImages(),
      ])
      realImages = real.images || []
      fakeImages = fake.images || []
    } catch (error) {
      console.error('Failed to load images:', error)
    }
  }
  
  function handleDrag(e, category) {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      dragCategory = category
    } else if (e.type === 'dragleave') {
      dragCategory = null
    }
  }
  
  function handleDrop(e, category) {
    e.preventDefault()
    e.stopPropagation()
    dragCategory = null
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFiles(Array.from(e.dataTransfer.files), category)
    }
  }
  
  function handleFileInput(e, category) {
    if (e.target.files) {
      uploadFiles(Array.from(e.target.files), category)
    }
  }
  
  async function uploadFiles(files, category) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'))
    if (imageFiles.length === 0) {
      showToast('Please select image files only', 'error')
      return
    }
    
    try {
      const response = await apiService.uploadBatch(imageFiles, category)
      showToast(`Uploaded ${response.uploaded.length} ${category} image(s)`, 'success')
      loadImages()
    } catch (error) {
      showToast(error.response?.data?.detail || 'Upload failed', 'error')
    }
  }
  
  async function handleDelete(filename, category) {
    try {
      if (category === 'real') {
        await apiService.deleteRealImage(filename)
      } else {
        await apiService.deleteFakeImage(filename)
      }
      showToast('Image deleted', 'success')
      loadImages()
    } catch (error) {
      showToast('Delete failed', 'error')
    }
  }
  
  async function handleTrain() {
    if (realImages.length === 0 || fakeImages.length === 0) {
      showToast('Need at least one real and one fake image', 'warning')
      return
    }
    
    training = true
    try {
      const response = await apiService.trainDetector()
      showToast('Model trained successfully!', 'success')
      setTimeout(() => window.location.reload(), 2000)
    } catch (error) {
      showToast(error.response?.data?.detail || 'Training failed', 'error')
    } finally {
      training = false
    }
  }
</script>

<div class="space-y-6">
  <!-- Real Images Section -->
  <div class="glass rounded-3xl p-8 shadow-xl">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
        <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-gray-800">Real Images</h2>
        <p class="text-sm text-gray-600">{realImages.length} images uploaded</p>
      </div>
    </div>

    <div
      on:dragenter={(e) => handleDrag(e, 'real')}
      on:dragleave={(e) => handleDrag(e, 'real')}
      on:dragover={(e) => handleDrag(e, 'real')}
      on:drop={(e) => handleDrop(e, 'real')}
      class="border-2 border-dashed rounded-2xl p-8 text-center transition-all {dragCategory === 'real'
        ? 'border-green-500 bg-green-50/50 scale-105'
        : 'border-gray-300 hover:border-green-400 bg-gray-50/50'}"
    >
      <input
        type="file"
        multiple
        accept="image/*"
        on:change={(e) => handleFileInput(e, 'real')}
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <svg class="w-12 h-12 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="font-semibold text-gray-700 mb-2">Upload real images</p>
      <p class="text-sm text-gray-500">Drag & drop or click to browse</p>
    </div>

    {#if realImages.length > 0}
      <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each realImages as img}
          <div class="relative group">
            <div class="aspect-square rounded-xl overflow-hidden bg-gray-100">
              <img
                src={`http://localhost:8000/uploads/real/${img.filename}`}
                alt={img.filename}
                class="w-full h-full object-cover"
                on:error={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage%3C/text%3E%3C/svg%3E'
                }}
              />
            </div>
            <button
              on:click={() => handleDelete(img.filename, 'real')}
              class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Fake Images Section -->
  <div class="glass rounded-3xl p-8 shadow-xl">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center">
        <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-gray-800">AI-Generated Images</h2>
        <p class="text-sm text-gray-600">{fakeImages.length} images uploaded</p>
      </div>
    </div>

    <div
      on:dragenter={(e) => handleDrag(e, 'fake')}
      on:dragleave={(e) => handleDrag(e, 'fake')}
      on:dragover={(e) => handleDrag(e, 'fake')}
      on:drop={(e) => handleDrop(e, 'fake')}
      class="border-2 border-dashed rounded-2xl p-8 text-center transition-all {dragCategory === 'fake'
        ? 'border-red-500 bg-red-50/50 scale-105'
        : 'border-gray-300 hover:border-red-400 bg-gray-50/50'}"
    >
      <input
        type="file"
        multiple
        accept="image/*"
        on:change={(e) => handleFileInput(e, 'fake')}
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <svg class="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="font-semibold text-gray-700 mb-2">Upload AI-generated images</p>
      <p class="text-sm text-gray-500">Drag & drop or click to browse</p>
    </div>

    {#if fakeImages.length > 0}
      <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each fakeImages as img}
          <div class="relative group">
            <div class="aspect-square rounded-xl overflow-hidden bg-gray-100">
              <img
                src={`http://localhost:8000/uploads/fake/${img.filename}`}
                alt={img.filename}
                class="w-full h-full object-cover"
                on:error={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage%3C/text%3E%3C/svg%3E'
                }}
              />
            </div>
            <button
              on:click={() => handleDelete(img.filename, 'fake')}
              class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Train Button -->
  <div class="glass rounded-3xl p-8 shadow-xl text-center">
    <div class="mb-6">
      <svg class="w-16 h-16 text-purple-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
      <h2 class="text-2xl font-bold gradient-text mb-2">Train the Model</h2>
      <p class="text-gray-600">
        Once you have uploaded real and AI images, train the detector to learn the patterns
      </p>
    </div>
    <button
      on:click={handleTrain}
      disabled={training || realImages.length === 0 || fakeImages.length === 0}
      class="bg-gradient-to-r from-purple-500 to-pink-500 text-white py-4 px-12 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 mx-auto"
    >
      {#if training}
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Training...
      {:else}
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
        Train Detector
      {/if}
    </button>
    <p class="text-sm text-gray-500 mt-4">
      Real: {realImages.length} | Fake: {fakeImages.length}
    </p>
  </div>
</div>

