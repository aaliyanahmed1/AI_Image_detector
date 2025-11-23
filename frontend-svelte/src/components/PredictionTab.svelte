<script>
  import { apiService } from '../utils/api.js'
  
  export let showToast, status
  
  let files = []
  let previews = []
  let results = []
  let loading = false
  let dragActive = false
  
  function handleDrag(e) {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      dragActive = true
    } else if (e.type === 'dragleave') {
      dragActive = false
    }
  }
  
  function handleDrop(e) {
    e.preventDefault()
    e.stopPropagation()
    dragActive = false
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }
  
  function handleFileInput(e) {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files))
    }
  }
  
  function handleFiles(newFiles) {
    const imageFiles = newFiles.filter(file => file.type.startsWith('image/'))
    if (imageFiles.length === 0) {
      showToast('Please select image files only', 'error')
      return
    }
    
    files = [...files, ...imageFiles]
    imageFiles.forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        previews = [...previews, { file: file.name, url: e.target.result }]
      }
      reader.readAsDataURL(file)
    })
  }
  
  function removeFile(index) {
    files = files.filter((_, i) => i !== index)
    previews = previews.filter((_, i) => i !== index)
    results = results.filter((_, i) => i !== index)
  }
  
  async function handlePredict() {
    if (files.length === 0) {
      showToast('Please select at least one image', 'warning')
      return
    }
    
    loading = true
    results = [] // Clear previous results
    
    try {
      console.log('Starting prediction for', files.length, 'files')
      const response = await apiService.predictBatch(files)
      console.log('Prediction response:', response)
      
      if (response.success) {
        results = response.results || []
        const successful = response.successful || 0
        showToast(`Analyzed ${successful} of ${response.total} image(s)`, 'success')
      } else {
        showToast('Prediction failed', 'error')
      }
    } catch (error) {
      console.error('Prediction error:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Prediction failed. Check console for details.'
      showToast(errorMsg, 'error')
    } finally {
      loading = false
    }
  }
</script>

<div class="space-y-6">
  <!-- Upload Area -->
  <div class="glass rounded-3xl p-8 shadow-xl">
    <h2 class="text-3xl font-bold mb-2 gradient-text">Image Detection</h2>
    <p class="text-gray-600 mb-6">Upload images to detect if they're real or AI-generated</p>

    <div
      on:dragenter={handleDrag}
      on:dragleave={handleDrag}
      on:dragover={handleDrag}
      on:drop={handleDrop}
      class="relative border-2 border-dashed rounded-2xl p-12 text-center transition-all {dragActive 
        ? 'border-blue-500 bg-blue-50/50 scale-105' 
        : 'border-gray-300 hover:border-blue-400 bg-gray-50/50'}"
    >
      <input
        type="file"
        multiple
        accept="image/*"
        on:change={handleFileInput}
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <div class="animate-float">
        <svg class="w-16 h-16 text-blue-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <p class="text-lg font-semibold text-gray-700 mb-2">
        Drag & drop images here
      </p>
      <p class="text-sm text-gray-500">or click to browse</p>
    </div>

    <!-- File Previews -->
    {#if previews.length > 0}
      <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each previews as preview, index}
          <div class="relative group">
            <div class="aspect-square rounded-xl overflow-hidden bg-gray-100">
              <img
                src={preview.url}
                alt={preview.file}
                class="w-full h-full object-cover"
              />
            </div>
            <button
              on:click={() => removeFile(index)}
              class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            <p class="text-xs text-gray-600 mt-1 truncate">{preview.file}</p>
          </div>
        {/each}
      </div>
    {/if}

    <!-- Predict Button -->
    {#if files.length > 0}
      <button
        on:click={handlePredict}
        disabled={loading}
        class="mt-6 w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {#if loading}
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Analyzing...
        {:else}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Detect Authenticity
        {/if}
      </button>
    {/if}
  </div>

  <!-- Results -->
  {#if results.length > 0}
    <div class="glass rounded-3xl p-8 shadow-xl">
      <h3 class="text-2xl font-bold mb-6 gradient-text">Detection Results</h3>
      <div class="grid gap-4">
        {#each results as result}
          <div class="p-6 rounded-xl border-2 {result.success && result.prediction?.label === 'real'
            ? 'bg-green-50 border-green-200'
            : result.success && result.prediction?.label === 'ai'
            ? 'bg-red-50 border-red-200'
            : 'bg-gray-50 border-gray-200'}"
          >
            {#if result.success}
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    {#if result.prediction.label === 'real'}
                      <svg class="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                    {:else}
                      <svg class="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                      </svg>
                    {/if}
                    <h4 class="font-bold text-lg">{result.filename}</h4>
                  </div>
                  <div class="ml-9 space-y-1">
                    <p class="text-sm text-gray-600">
                      Label: <span class="font-semibold capitalize">{result.prediction.label}</span>
                    </p>
                    <p class="text-sm text-gray-600">
                      Confidence: <span class="font-semibold">{(result.prediction.confidence * 100).toFixed(1)}%</span>
                    </p>
                    {#if result.prediction.reasons}
                      <p class="text-xs text-gray-500 mt-1">
                        {result.prediction.reasons.join(' • ')}
                      </p>
                    {/if}
                  </div>
                </div>
                <div class="text-right">
                  <div class="px-4 py-2 rounded-full font-bold {result.prediction.label === 'real'
                    ? 'bg-green-500 text-white'
                    : 'bg-red-500 text-white'}"
                  >
                    {result.prediction.label === 'real' ? 'REAL' : 'AI'}
                  </div>
                </div>
              </div>
            {:else}
              <div class="flex items-center gap-3 text-red-600">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <p>{result.filename}: {result.error}</p>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

