<script>
  import { onMount } from 'svelte'
  import Header from './components/Header.svelte'
  import StatusIndicator from './components/StatusIndicator.svelte'
  import PredictionTab from './components/PredictionTab.svelte'
  import StatsTab from './components/StatsTab.svelte'
  import Toast from './components/Toast.svelte'
  import { apiService } from './utils/api.js'

  let activeTab = 'predict'
  let status = null
  let toasts = []

  onMount(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  })

  function fetchStatus() {
    apiService.getStatus()
      .then(data => status = data)
      .catch(error => console.error('Failed to fetch status:', error))
  }

  function showToast(message, type = 'info') {
    const id = Date.now()
    toasts = [...toasts, { id, message, type }]
    setTimeout(() => {
      toasts = toasts.filter(t => t.id !== id)
    }, 5000)
  }

  const tabs = [
    { id: 'predict', label: 'Detect', icon: '🔮' },
    { id: 'stats', label: 'Analytics', icon: '📊' },
  ]
</script>

<div class="min-h-screen">
  <!-- Background Effects -->
  <div class="fixed inset-0 -z-10 overflow-hidden">
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl animate-pulse-slow" />
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s" />
    <div class="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-400/20 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 4s" />
  </div>

  <Header />
  <StatusIndicator {status} />

  <main class="container mx-auto px-4 py-8 max-w-7xl">
    <!-- Tab Navigation -->
    <div class="flex justify-center mb-8">
      <div class="glass rounded-2xl p-2 flex gap-2 shadow-xl">
        {#each tabs as tab}
          <button
            on:click={() => activeTab = tab.id}
            class="px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 {activeTab === tab.id
              ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg scale-105'
              : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'}"
          >
            <span class="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        {/each}
      </div>
    </div>

    <!-- Tab Content -->
    <div class="transition-all duration-300">
      {#if activeTab === 'predict'}
        <PredictionTab {showToast} {status} />
      {:else if activeTab === 'stats'}
        <StatsTab {status} />
      {/if}
    </div>
  </main>

  <!-- Toast Container -->
  <div class="fixed bottom-4 right-4 z-50 space-y-2">
    {#each toasts as toast}
      <Toast {...toast} />
    {/each}
  </div>
</div>

