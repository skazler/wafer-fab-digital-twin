<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
const logs = ref([]);

const fetchLogs = async () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  const response = await fetch(`${baseUrl}/quarantine`);

  try {
    const res = await fetch(`${baseUrl}/quarantine`);
    if (res.ok) logs.value = await res.json();
  } catch (err) {
    console.error("Postgres Fetch Error:", err);
  }
};

onMounted(() => {
    fetchLogs();
    setInterval(fetchLogs, 5000);
});
</script>

<template>
    <div class="card">
        <h3>⚠️ Active Quarantine Queue</h3>
        <DataTable :value="logs" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="wafer_id" header="Wafer ID"></Column>
            <Column field="metric_name" header="Violation"></Column>
            <Column field="violation_value" header="Value">
                <template #body="slotProps">
                    <span class="text-red-500 font-bold">{{ slotProps.data.violation_value }}°C</span>
                </template>
            </Column>
            <Column field="timestamp" header="Detected At"></Column>
            <Column header="Status">
                <template #body>
                    <Tag value="Pending Review" severity="danger" />
                </template>
            </Column>
        </DataTable>
    </div>
</template>
