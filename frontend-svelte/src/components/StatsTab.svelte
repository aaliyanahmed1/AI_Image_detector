<script>
  import { onMount } from 'svelte'
  import { apiService } from '../utils/api.js'
  
  export let status
  
  let stats = null
  
  onMount(() => {
    if (status?.detector?.is_trained) {
      loadStats()
    }
  })
  
  $: if (status?.detector?.is_trained && !stats) {
    loadStats()
  }
  
  async function loadStats() {
    try {
      const data = await apiService.getStats()
      stats = data
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }
</script>

  <div class="space-y-6">
    <!-- Overview Cards -->
    <div class="grid md:grid-cols-4 gap-6">
      <div class="glass rounded-2xl p-6 shadow-lg">
        <svg class="w-8 h-8 text-green-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
        <p class="text-sm text-gray-600 mb-1">Real Images</p>
        <p class="text-2xl font-bold text-gray-800">{status.directories?.real_images || 0}</p>
      </div>
      
      <div class="glass rounded-2xl p-6 shadow-lg">
        <svg class="w-8 h-8 text-red-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
        <p class="text-sm text-gray-600 mb-1">Fake Images</p>
        <p class="text-2xl font-bold text-gray-800">{status.directories?.fake_images || 0}</p>
      </div>
      
      <div class="glass rounded-2xl p-6 shadow-lg">
        <svg class="w-8 h-8 text-blue-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        <p class="text-sm text-gray-600 mb-1">Variance Explained</p>
        <p class="text-2xl font-bold text-gray-800">
          {stats?.total_variance ? `${(stats.total_variance * 100).toFixed(1)}%` : '-'}
        </p>
      </div>
      
      <div class="glass rounded-2xl p-6 shadow-lg">
        <svg class="w-8 h-8 text-purple-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
        <p class="text-sm text-gray-600 mb-1">Status</p>
        <p class="text-2xl font-bold text-gray-800">Baseline</p>
      </div>
    </div>

    <!-- Detailed Stats -->
    {#if stats}
      <div class="glass rounded-3xl p-8 shadow-xl">
        <div class="flex items-center gap-3 mb-6">
          <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h2 class="text-2xl font-bold gradient-text">Model Statistics</h2>
        </div>

        <div class="space-y-4">
          {#if stats.explained_variance}
            <div>
              <p class="text-sm font-semibold text-gray-700 mb-2">PCA Variance Explained</p>
              <div class="space-y-2">
                {#each stats.explained_variance as v, i}
                  <div class="flex items-center gap-3">
                    <span class="text-sm text-gray-600 w-20">PC{i + 1}:</span>
                    <div class="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        class="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-1000"
                        style="width: {v * 100}%"
                      />
                    </div>
                    <span class="text-sm font-semibold text-gray-700 w-16 text-right">
                      {(v * 100).toFixed(1)}%
                    </span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          {#if stats.real_centroid && stats.fake_centroid}
            <div class="grid md:grid-cols-2 gap-4 mt-6">
              <div class="p-4 bg-green-50 rounded-xl border border-green-200">
                <p class="text-sm font-semibold text-green-700 mb-2">Real Centroid</p>
                <p class="text-xs text-gray-600 font-mono">
                  [{stats.real_centroid.map(v => v.toFixed(3)).join(', ')}]
                </p>
              </div>
              <div class="p-4 bg-red-50 rounded-xl border border-red-200">
                <p class="text-sm font-semibold text-red-700 mb-2">Fake Centroid</p>
                <p class="text-xs text-gray-600 font-mono">
                  [{stats.fake_centroid.map(v => v.toFixed(3)).join(', ')}]
                </p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>

