<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Card from 'primevue/card';

const quarantineLogs = ref([]);
const systemStatus = ref({ status: 'Online', tool: 'ETCH-001' });

const fetchQuarantine = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/quarantine');
    if (res.ok) {
      quarantineLogs.value = await res.json();
    }
  } catch (err) {
    console.error("Backend unreachable. Check FastAPI status.");
  }
};

onMounted(() => {
  fetchQuarantine();
  setInterval(fetchQuarantine, 3000); 
});
</script>

<template>
  <div class="my-app-dark p-4 bg-gray-900 min-h-screen text-white">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold m-0 text-blue-400">Greenfield <span class="text-white">Digital Twin</span></h1>
      <Tag :value="systemStatus.status" severity="success"></Tag>
    </div>

    <div class="grid">
      <div class="col-12">
        <Card>
          <template #title>Live Telemetry (InfluxDB Stream)</template>
          <template #content>
             <div class="h-10rem flex align-items-center justify-content-center border-round bg-gray-800 border-dashed border-1 border-gray-600">
                <p class="text-gray-500">Live Chart (Chart.js) Integration Pending</p>
             </div>
          </template>
        </Card>
      </div>

      <div class="col-12 mt-4">
        <Card>
          <template #title>⚠️ Safety Interlock & Quarantine Logs (PostgreSQL)</template>
          <template #content>
            <DataTable :value="quarantineLogs" paginator :rows="5" responsiveLayout="scroll">
              <Column field="wafer_id" header="Wafer ID" sortable></Column>
              <Column field="metric_name" header="Violation"></Column>
              <Column field="violation_value" header="Value">
                <template #body="slotProps">
                  <span class="text-red-400 font-bold">{{ slotProps.data.violation_value }}°C</span>
                </template>
              </Column>
              <Column field="timestamp" header="Event Time"></Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  background-color: #111827;
}
.p-card {
  background: #1f2937 !important;
  color: white !important;
}
.my-app-dark {
    background-color: var(--p-content-background); 
    color: var(--p-content-color);
}
</style>
