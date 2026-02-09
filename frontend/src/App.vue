<script setup>
import Tag from 'primevue/tag';
import TelemetryStream from './components/TelemetryStream.vue';
import QuarantineTable from './components/QuarantineTable.vue';
</script>

<template>
  <div class="my-app-dark p-4 bg-gray-900 min-h-screen text-white">
    
    <header class="flex justify-content-between align-items-center mb-5 border-bottom-1 border-gray-800 pb-3">
      <div>
        <h1 class="text-3xl font-bold m-0 tracking-tight">
          <span class="text-blue-500">Greenfield</span> <span class="text-white font-light">Digital Twin</span>
        </h1>
        <p class="text-gray-500 text-sm m-0 mt-1">Industrial IoT Monitoring Platform | v1.0.4</p>
      </div>

      <div class="flex align-items-center gap-4">
        <div class="text-right">
          <div class="text-xs text-gray-500 uppercase tracking-wider">Asset ID</div>
          <div class="font-mono text-blue-200">ETCH-001-GREENFIELD</div>
        </div>
        
        <Tag severity="success" class="px-3 py-2 border-round-xl">
          <div class="flex align-items-center gap-2">
            <span class="status-indicator-container">
              <span class="pulse-ring"></span>
              <span class="pulse-dot"></span>
            </span>
            <span class="font-bold tracking-wide">SYSTEM LIVE</span>
          </div>
        </Tag>
      </div>
    </header>

    <main class="grid">
      <div class="col-12 lg:col-12 px-3">
        <TelemetryStream />
      </div>

      <div class="col-12 mt-4 px-3">
        <QuarantineTable />
      </div>
    </main>

    <footer class="mt-5 pt-4 text-center border-top-1 border-gray-800">
      <p class="text-gray-600 text-xs">
        &copy; 2026 Sky H. Yoo | Digital Transformation Portfolio 
        <span class="mx-2">|</span> 
        Secure Sandbox Environment
      </p>
    </footer>
  </div>
</template>

<style>
.my-app-dark { 
  background-color: var(--p-content-background); 
  color: var(--p-content-color); 
}

.status-indicator-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 10px;
  height: 10px;
}

.pulse-ring {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: #4ade80;
  border-radius: 9999px;
  animation: ring-expand 2s cubic-bezier(0, 0, 0.2, 1) infinite !important;
}

.pulse-dot {
  position: relative;
  width: 8px;
  height: 8px;
  background-color: #22c55e;
  border-radius: 9999px;
  animation: dot-heartbeat 2s ease-in-out infinite !important;
}

.grid {
  margin-right: -1rem;
  margin-left: -1rem;
}
</style>