<script>
  export let status
</script>

{#if status}
  <div class="fixed top-24 left-4 z-40 glass rounded-xl p-3 shadow-lg">
    <div class="flex items-center gap-2">
      <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span class="text-sm font-medium text-gray-700">Ready to Detect</span>
    </div>
  </div>
{/if}

