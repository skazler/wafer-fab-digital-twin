<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import Button from 'primevue/button';
import SelectButton from 'primevue/selectbutton';
import { TelemetryService } from '../services/api';

// state management
const chartData = ref(null);
const rawHistory = ref([]);
const toggleOptions = ref(['Temperature', 'Threshold']);
const activeSeries = ref(['Temperature', 'Threshold']);

// analysis results
const remainingLife = ref(null);
const isDrifting = ref(false);
const rootCause = ref('');
const reason = ref('');
const recommendedAction = ref('');

// UI states
const isLoading = ref(true);
const wasInterlocked = ref(false); 
let pollInterval = null;

// computed properties
const isOnline = computed(() => {
    if (!rawHistory.value.length) return false;
    const lastPoint = new Date(rawHistory.value[rawHistory.value.length - 1].time);
    const now = new Date();
    return (now - lastPoint) < 5000;
});

const isShutDown = computed(() => {
    if (wasInterlocked.value) return true;
    if (!rawHistory.value.length) return false;

    const lastVal = rawHistory.value[rawHistory.value.length - 1].value;
    const interlockHit = lastVal >= 188.0;
    
    const inferredCrash = !isOnline.value && remainingLife.value !== null && remainingLife.value < 5;

    if (interlockHit || inferredCrash) {
        wasInterlocked.value = true;
        return true;
    }
    return false;
});

const currentTemp = computed(() => {
    if (!rawHistory.value.length) return '--';
    return rawHistory.value[rawHistory.value.length - 1].value.toFixed(1);
});

// logic & actions
const handleSystemReset = async () => {
    try {
        await TelemetryService.resetSystem();
        wasInterlocked.value = false;
        isDrifting.value = false;
        remainingLife.value = null;
        fetchData();
    } catch (err) {
        console.error("Reset failed:", err);
    }
};

const fetchData = async () => {
    try {
        const data = await TelemetryService.getHistory();
        const history = data.history || [];
        
        if (history.length > 0) {
            rawHistory.value = history.filter(h => h.metric === 'temperature').slice(-30);
        }

        if (data.interlock_active) wasInterlocked.value = true;

        remainingLife.value = data.predictions?.remaining_life_seconds;
        isDrifting.value = data.predictions?.is_drifting;
        
        if (!isShutDown.value) {
            rootCause.value = data.predictions?.root_cause || 'Analyzing...';
            reason.value = data.predictions?.reason || 'Historical trend analysis';
            recommendedAction.value = data.predictions?.recommended_action || 'Monitor Stability';
        }

        renderChart();
        
        if (isLoading.value) isLoading.value = false;
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

watch(activeSeries, () => renderChart());

onMounted(() => {
    fetchData();
    pollInterval = setInterval(fetchData, 3000);
});

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval);
});

const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: { ticks: { color: '#9ca3af', maxRotation: 0 }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
        y: { min: 150, max: 200, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    animation: false
});
</script>

<template>
    <Card class="telemetry-card shadow-4">
        <template #content>
            <div v-if="isLoading" class="flex flex-column align-items-center justify-content-center py-8 animate-fadein">
                <i class="pi pi-spin pi-database text-4xl text-blue-500 mb-4"></i>
                <h2 class="text-white m-0 font-medium">Connecting to InfluxDB</h2>
            </div>

            <div v-else class="animate-fadein">
                <div class="flex justify-content-between align-items-center mb-4">
                    <div class="flex align-items-center gap-3">
                        <div class="flex align-items-center gap-2">
                            <i class="pi pi-bolt text-yellow-400"></i>
                            <span class="text-gray-100 font-bold">Live Telemetry</span>
                        </div>
                        <span 
                            class="px-2 py-1 border-round text-xs font-bold uppercase tracking-wider"
                            :class="isShutDown ? 'bg-red-900 text-red-400 border-1 border-red-700' : (isOnline ? 'bg-green-900 text-green-400 border-1 border-green-700' : 'bg-gray-800 text-gray-500 border-1 border-gray-700')"
                        >
                            {{ isShutDown ? '● Interlocked' : (isOnline ? '● Online' : '○ Offline') }}
                        </span>
                        
                        <Button v-if="isShutDown" 
                                icon="pi pi-refresh" 
                                label="Reset System" 
                                class="p-button-sm p-button-outlined p-button-secondary py-1"
                                @click="handleSystemReset" />
                    </div>
                    <div class="text-2xl font-mono" :class="isShutDown ? 'text-red-500' : (isOnline ? 'text-blue-400' : 'text-gray-600')">
                        {{ currentTemp }}<span class="text-sm text-gray-500 ml-1">°C</span>
                    </div>
                </div>

                <div v-if="isDrifting || isShutDown" 
                     class="pdm-alert-container p-3 border-round mb-4"
                     :class="{ 'critical-state': isShutDown }">
                    
                    <div class="flex align-items-center justify-content-between">
                        <div class="flex align-items-center gap-3">
                            <i class="pi text-xl" 
                               :class="[isShutDown ? 'pi-exclamation-triangle text-red-500' : 'pi-exclamation-circle text-orange-500 pulse-warning']"></i>
                            <div>
                                <span class="text-xs font-bold uppercase tracking-widest block"
                                      :class="isShutDown ? 'text-red-400' : 'text-orange-400'">
                                    {{ isShutDown ? 'Critical System Alert' : 'Prognostic Alert' }}
                                </span>
                                <h3 class="m-0 text-white font-medium">
                                    {{ isShutDown ? 'Safety Interlock Engaged' : 'Thermal Drift Detected' }}
                                </h3>
                            </div>
                        </div>
                        
                        <div class="text-right">
                            <span class="text-gray-500 text-xs block uppercase">Status</span>
                            <span class="text-3xl font-mono font-bold" 
                                  :class="isShutDown ? 'text-red-500' : (remainingLife < 60 ? 'text-red-500 pulse-red' : 'text-orange-400')">
                                {{ isShutDown ? 'SHUTDOWN' : Math.floor(remainingLife) + 's' }}
                            </span>
                        </div>
                    </div>

                    <div class="mt-3 bg-gray-800 border-round overflow-hidden" style="height: 6px;">
                        <div 
                            class="pdm-progress-bar" 
                            :class="[
                                isShutDown ? 'bg-red-600' : (remainingLife < 60 ? 'bg-red-500 bar-glow-red' : 'bg-orange-500'),
                            ]"
                            :style="{ 
                                width: isShutDown ? '100%' : Math.min(100, (remainingLife / 300) * 100) + '%',
                                transition: isShutDown ? 'none' : 'width 1s linear'
                            }"
                        ></div>
                    </div>

                    <div class="mt-4 grid border-top-1 border-gray-700 pt-3">
                        <div class="col-7">
                            <span class="text-gray-500 text-xs uppercase block font-bold tracking-wider">Diagnosis</span>
                            <span class="text-blue-300 font-mono text-sm uppercase">
                                {{ isShutDown ? 'CRITICAL_LIMIT_EXCEEDED' : rootCause }}
                            </span>
                            <small class="block text-gray-400 italic mt-1">
                                {{ isShutDown ? 'Thermal threshold exceeded. Hardware interlock active.' : reason }}
                            </small>
                        </div>
                        <div class="col-5 text-right">
                            <span class="text-gray-500 text-xs uppercase block font-bold tracking-wider">
                                {{ isShutDown ? 'Action Taken' : 'Recommended Action' }}
                            </span>
                            <div class="mt-1">
                                <span class="px-2 py-1 border-round text-xs font-bold border-1"
                                      :class="[isShutDown ? 'bg-red-900 text-red-100 border-red-700' : 'bg-blue-900 text-blue-200 border-blue-700']">
                                    {{ isShutDown ? 'EMERGENCY_STOP_TRIGGERED' : recommendedAction }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex justify-content-center mb-4">
                    <SelectButton v-model="activeSeries" :options="toggleOptions" multiple />
                </div>

                <div class="chart-container" style="height: 300px; position: relative;">
                    <Chart v-if="chartData" type="line" :data="chartData" :options="chartOptions" class="h-full w-full" />
                </div>
            </div>
        </template>
    </Card>
</template>

<style scoped>
:deep(.p-selectbutton .p-button.p-highlight) { background: #3B82F6; border-color: #3B82F6; color: #ffffff; }
.telemetry-card { background: rgba(31, 41, 55, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); }
.pdm-alert-container { background: rgba(251, 146, 60, 0.1); border: 1px solid rgba(251, 146, 60, 0.2); transition: all 0.5s ease; }
.critical-state { background: rgba(220, 38, 38, 0.15); border-color: rgba(220, 38, 38, 0.4); }
.pdm-progress-bar { height: 100%; transition: width 1s linear, background-color 0.5s ease; }

/* ANIMATIONS */
.pulse-warning { animation: warning-glow 2s infinite; }
.pulse-red { animation: critical-pulse 1s infinite; }
.bar-glow-red { animation: bar-critical-glow 1.5s infinite; }

@keyframes warning-glow {
    0%, 100% { opacity: 1; filter: drop-shadow(0 0 2px rgba(251, 146, 60, 0.5)); }
    50% { opacity: 0.7; filter: drop-shadow(0 0 8px rgba(251, 146, 60, 0.8)); }
}
@keyframes critical-pulse { 
    0%, 100% { transform: scale(1); opacity: 1; } 
    50% { transform: scale(1.05); opacity: 0.8; } 
}
@keyframes bar-critical-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(239, 68, 68, 0.5); }
    50% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.8); }
}
.animate-fadein { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>