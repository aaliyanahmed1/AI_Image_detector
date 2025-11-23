<script>
  import { onMount } from 'svelte'
  import { apiService } from '../utils/api.js'
  
  export let showToast
  
  let stats = null
  let loading = false
  
  async function loadStats() {
    loading = true
    try {
      // Note: Need to add getMemoryStats to apiService
      const response = await fetch('http://localhost:8000/api/memory')
      stats = await response.json()
    } catch (error) {
      showToast('Failed to load memory stats', 'error')
    } finally {
      loading = false
    }
  }
  
  onMount(() => {
    loadStats()
  })
</script>

{#if stats?.success}
  <div class="glass rounded-3xl p-8 shadow-xl">
    <h3 class="text-2xl font-bold mb-6 gradient-text">Memory & Storage</h3>
    
    <div class="grid md:grid-cols-3 gap-6">
      <div class="p-4 bg-blue-50 rounded-xl border border-blue-200">
        <p class="text-sm font-semibold text-blue-700 mb-2">System Memory</p>
        <p class="text-xs text-gray-600">Total: {stats.memory?.total_gb} GB</p>
        <p class="text-xs text-gray-600">Available: {stats.memory?.available_gb} GB</p>
        <p class="text-xs text-gray-600">Used: {stats.memory?.used_percent}%</p>
      </div>
      
      <div class="p-4 bg-green-50 rounded-xl border border-green-200">
        <p class="text-sm font-semibold text-green-700 mb-2">Disk Storage</p>
        <p class="text-xs text-gray-600">Total: {stats.disk?.total_gb} GB</p>
        <p class="text-xs text-gray-600">Free: {stats.disk?.free_gb} GB</p>
        <p class="text-xs text-gray-600">Used: {stats.disk?.used_percent}%</p>
      </div>
      
      <div class="p-4 bg-purple-50 rounded-xl border border-purple-200">
        <p class="text-sm font-semibold text-purple-700 mb-2">Application Data</p>
        <p class="text-xs text-gray-600">Uploads: {stats.storage?.uploads_mb} MB</p>
        <p class="text-xs text-gray-600">Models: {stats.storage?.models_mb} MB</p>
        <p class="text-xs text-gray-600">History: {stats.storage?.history_mb} MB</p>
      </div>
    </div>
  </div>
{/if}

