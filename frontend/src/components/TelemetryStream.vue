<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import SelectButton from 'primevue/selectbutton';
import { TelemetryService } from '../services/api';

const chartData = ref(null);
const rawHistory = ref([]);
const toggleOptions = ref(['Temperature', 'Threshold']);
const activeSeries = ref(['Temperature', 'Threshold']);
let pollInterval = null;

watch(activeSeries, () => {
    renderChart();
});

const currentTemp = computed(() => {
    if (!rawHistory.value.length) return '--';
    return rawHistory.value[rawHistory.value.length - 1].value.toFixed(1);
});

const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false }
    },
    scales: {
        x: {
            ticks: { color: '#9ca3af', maxRotation: 0 },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
            min: 150, max: 200,
            ticks: { color: '#9ca3af' },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
    },
    animation: false,
    hover: { mode: null }
});

const fetchData = async () => {
    try {
        const data = await TelemetryService.getHistory();
        const history = data.history || [];
        rawHistory.value = history.filter(h => h.metric === 'temperature').slice(-30);
        renderChart();
    } catch (error) {
        console.error("Telemetry Stream Error:", error);
    }
};

const renderChart = () => {
    const datasets = [];

    if (activeSeries.value.includes('Temperature')) {
        datasets.push({
            label: 'Chamber Temperature',
            data: rawHistory.value.map(h => h.value),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.2,
            pointRadius: 0
        });
    }

    if (activeSeries.value.includes('Threshold')) {
        datasets.push({
            label: 'Safety Threshold',
            data: rawHistory.value.map(() => 188),
            borderColor: '#EF4444',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
        });
    }

    chartData.value = {
        labels: rawHistory.value.map(h => 
            new Date(h.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        ),
        datasets: datasets
    };
};

onMounted(() => {
    fetchData();
    pollInterval = setInterval(fetchData, 3000);
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});
</script>

<template>
    <Card class="telemetry-card shadow-4">
        <template #title>
            <div class="flex justify-content-between align-items-center">
                <div class="flex align-items-center gap-2">
                    <i class="pi pi-bolt text-yellow-400"></i>
                    <span class="text-gray-100">Live Telemetry</span>
                </div>
                <div class="text-2xl font-mono text-blue-400">
                    {{ currentTemp }}<span class="text-sm text-gray-500 ml-1">°C</span>
                </div>
            </div>
        </template>
        
        <template #content>
            <div class="flex justify-content-center mb-4">
                <SelectButton 
                    v-model="activeSeries" 
                    :options="toggleOptions" 
                    multiple 
                    aria-label="Toggle Telemetry Series"
                />
            </div>

            <div class="chart-container" style="height: 300px; position: relative;">
                <Chart v-if="chartData" type="line" :data="chartData" :options="chartOptions" class="h-full w-full" />
                
                <div v-else class="h-full flex flex-column align-items-center justify-content-center border-round bg-gray-800-opacity">
                    <i class="pi pi-spin pi-spinner text-3xl mb-2 text-blue-500"></i>
                    <p class="text-gray-500 font-italic">Synchronizing with InfluxDB...</p>
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
:deep(.p-selectbutton .p-button.p-highlight) {
    background: #3B82F6;
    border-color: #3B82F6;
    color: #ffffff;
}

.telemetry-card {
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
</style>