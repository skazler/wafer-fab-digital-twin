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
const remainingLife = ref(null);
const isDrifting = ref(false);

let pollInterval = null;

const isOnline = computed(() => {
    if (!rawHistory.value.length) return false;
    const lastPoint = new Date(rawHistory.value[rawHistory.value.length - 1].time);
    const now = new Date();
    return (now - lastPoint) < 7000;
});

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
    plugins: { legend: { display: false } },
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
        remainingLife.value = data.predictions?.remaining_life_seconds;
        isDrifting.value = data.predictions?.is_drifting;

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
    if (pollInterval) clearInterval(pollInterval);
});
</script>

<template>
    <Card class="telemetry-card shadow-4">
        <template #title>
            <div class="flex justify-content-between align-items-center">
                <div class="flex align-items-center gap-3">
                    <div class="flex align-items-center gap-2">
                        <i class="pi pi-bolt text-yellow-400"></i>
                        <span class="text-gray-100">Live Telemetry</span>
                    </div>
                    <span 
                        class="px-2 py-1 border-round text-xs font-bold uppercase tracking-wider"
                        :class="isOnline ? 'bg-green-900 text-green-400 border-1 border-green-700' : 'bg-gray-800 text-gray-500 border-1 border-gray-700'"
                    >
                        {{ isOnline ? '● Online' : '○ Offline' }}
                    </span>
                </div>
                <div class="text-2xl font-mono" :class="isOnline ? 'text-blue-400' : 'text-gray-600'">
                    {{ currentTemp }}<span class="text-sm text-gray-500 ml-1">°C</span>
                </div>
            </div>
        </template>
        
        <template #content>
            <div v-if="isDrifting" class="pdm-alert-container p-3 border-round mb-4 animate-fadein">
                <div class="flex align-items-center justify-content-between">
                    <div class="flex align-items-center gap-3">
                        <i class="pi pi-exclamation-circle text-orange-500 text-xl pulse-warning"></i>
                        <div>
                            <span class="text-orange-400 text-xs font-bold uppercase tracking-widest block">Prognostic Alert</span>
                            <h3 class="m-0 text-white font-medium">Thermal Drift Detected</h3>
                        </div>
                    </div>
                    
                    <div class="text-right" v-if="remainingLife !== null">
                        <span class="text-gray-500 text-xs block">EST. TIME TO FAILURE</span>
                        <span class="text-3xl font-mono font-bold" :class="remainingLife < 60 ? 'text-red-500 pulse-red' : 'text-orange-400'">
                            {{ Math.floor(remainingLife) }}s
                        </span>
                    </div>
                </div>
                
                <div class="mt-3 bg-gray-800 border-round overflow-hidden" style="height: 6px;">
                    <div 
                        class="pdm-progress-bar" 
                        :class="remainingLife < 60 ? 'bg-red-500' : 'bg-orange-500'"
                        :style="{ width: Math.min(100, (remainingLife / 300) * 100) + '%' }"
                    ></div>
                </div>
            </div>

            <div class="flex justify-content-center mb-4">
                <SelectButton v-model="activeSeries" :options="toggleOptions" multiple />
            </div>

            <div class="chart-container" style="height: 300px; position: relative;">
                <Chart v-if="chartData" type="line" :data="chartData" :options="chartOptions" class="h-full w-full" />
                <div v-else class="h-full flex flex-column align-items-center justify-content-center border-round bg-gray-800">
                    <i class="pi pi-spin pi-spinner text-3xl mb-2 text-blue-500"></i>
                    <p class="text-gray-500 font-italic">Synchronizing with InfluxDB...</p>
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
/* (Keep existing styles) */
:deep(.p-selectbutton .p-button.p-highlight) {
    background: #3B82F6;
    border-color: #3B82F6;
    color: #ffffff;
}
.telemetry-card {
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.pdm-alert-container {
    background: rgba(251, 146, 60, 0.1);
    border: 1px solid rgba(251, 146, 60, 0.2);
}
.pdm-progress-bar {
    height: 100%;
    transition: width 1s linear, background-color 0.5s ease;
}
.pulse-warning { animation: warning-glow 2s infinite; }
.pulse-red { animation: critical-pulse 1s infinite; }
@keyframes warning-glow {
    0%, 100% { opacity: 1; filter: drop-shadow(0 0 2px rgba(251, 146, 60, 0.5)); }
    50% { opacity: 0.7; filter: drop-shadow(0 0 8px rgba(251, 146, 60, 0.8)); }
}
@keyframes critical-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
}
.animate-fadein { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
