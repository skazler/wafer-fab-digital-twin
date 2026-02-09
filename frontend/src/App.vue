<script setup>
import Tag from 'primevue/tag';
import TelemetryStream from './components/TelemetryStream.vue';
import QuarantineTable from './components/QuarantineTable.vue';
</script>

<template>
  <div class="my-app-dark p-4 bg-gray-900 min-h-screen text-white">
    <header class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold m-0 text-blue-400">
        <span class="text-white">Greenfield Digital Twin</span>
      </h1>
      <div class="flex align-items-center gap-3">
        <span class="text-sm text-gray-400">Tool: ETCH-001</span>
        <Tag value="Online" severity="success"></Tag>
      </div>
    </header>

    <main class="grid">
      <div class="col-12">
        <TelemetryStream />
      </div>
      <div class="col-12 mt-4">
        <QuarantineTable />
      </div>
    </main>
  </div>
</template>

<style>
body { margin: 0; background-color: #111827; }
.my-app-dark { background-color: var(--p-content-background); color: var(--p-content-color); }
</style>