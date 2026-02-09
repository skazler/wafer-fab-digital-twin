<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import Card from 'primevue/card';
import { TelemetryService } from '../services/api';

const logs = ref([]);
const dt = ref();
let pollInterval = null;

const fetchLogs = async () => {
  try {
    logs.value = await TelemetryService.getQuarantineLogs();
  } catch (err) {
    console.error("Postgres Fetch Error:", err);
  }
};

const exportCSV = () => {
    dt.value.exportCSV();
};

onMounted(() => {
    fetchLogs();
    pollInterval = setInterval(fetchLogs, 5000);
});

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval);
});
</script>

<template>
    <Card class="quarantine-card mt-4 shadow-4">
        <template #title>
            <div class="flex justify-content-between align-items-center">
                <div class="flex align-items-center gap-2">
                    <i class="pi pi-exclamation-triangle text-orange-500"></i>
                    <span class="text-white font-bold tracking-tight">Active Quarantine Queue</span>
                </div>
                <Button 
                    icon="pi pi-external-link" 
                    label="Export CSV" 
                    @click="exportCSV" 
                    class="p-button-outlined p-button-sm p-button-secondary" 
                />
            </div>
        </template>

        <template #content>
            <DataTable 
                ref="dt"
                :value="logs" 
                stripedRows 
                responsiveLayout="scroll" 
                class="p-datatable-sm custom-table"
                removableSort
                paginator 
                :rows="5"
                :alwaysShowPaginator="false" 
            >
                <template #empty>
                    <div class="text-center p-5 text-gray-400">
                        <i class="pi pi-check-circle text-green-500 mr-2 text-xl"></i>
                        <span class="font-light">System Nominal: No active tool excursions detected.</span>
                    </div>
                </template>

                <Column field="wafer_id" header="Wafer ID" sortable></Column>
                <Column field="metric_name" header="Violation" sortable></Column>
                
                <Column field="violation_value" header="Value" sortable>
                    <template #body="slotProps">
                        <span class="text-red-400 font-bold">
                            {{ slotProps.data.violation_value.toFixed(2) }}°C
                        </span>
                    </template>
                </Column>

                <Column field="timestamp" header="Detected At" sortable>
                    <template #body="slotProps">
                        {{ new Date(slotProps.data.timestamp).toLocaleString() }}
                    </template>
                </Column>

                <Column header="Status">
                    <template #body="slotProps">
                        <Tag 
                            :value="slotProps.data.status || 'Hold - Engineering'" 
                            severity="danger" 
                            rounded
                        />
                    </template>
                </Column>
            </DataTable>
        </template>
    </Card>
</template>

<style scoped>
.quarantine-card {
    background: rgba(31, 41, 55, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

:deep(.p-datatable-thead > tr > th) {
    background-color: rgba(31, 41, 55, 0.8) !important;
    color: #ffffff !important;
    border-color: #374151;
}

:deep(.p-datatable-tbody > tr) {
    background-color: transparent !important;
    color: #e5e7eb !important;
}

:deep(.p-datatable-striped .p-datatable-tbody > tr:nth-child(even)) {
    background-color: rgba(255, 255, 255, 0.03) !important;
}

:deep(.p-paginator) {
    background-color: transparent !important;
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding: 0.5rem 0 !important;
}

:deep(.p-paginator .p-paginator-first),
:deep(.p-paginator .p-paginator-prev),
:deep(.p-paginator .p-paginator-next),
:deep(.p-paginator .p-paginator-last),
:deep(.p-paginator .p-paginator-pages .p-paginator-page) {
    color: #9ca3af !important;
    background: transparent !important;
    border: none !important;
    min-width: 2.5rem;
    height: 2.5rem;
    transition: all 0.2s ease;
}

:deep(.p-paginator .p-paginator-pages .p-paginator-page.p-highlight) {
    background: rgba(59, 130, 246, 0.15) !important;
    color: #60a5fa !important;
    font-weight: bold;
}

:deep(.p-paginator button:not(.p-disabled):not(.p-highlight):hover) {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #ffffff !important;
}
</style>