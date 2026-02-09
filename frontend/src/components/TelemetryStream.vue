<script setup>
import Chart from 'primevue/chart';
import Card from 'primevue/card';
import { ref, onMounted } from 'vue';

const chartData = ref(null);
const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: { color: '#ffffff' }
        }
    },
    scales: {
        x: {
            ticks: { color: '#9ca3af' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        y: {
            min: 150,
            max: 200,
            ticks: { color: '#9ca3af' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            title: { display: true, text: 'Temperature (°C)', color: '#9ca3af' }
        }
    },
    animation: { duration: 500 }
});

const updateChart = async () => {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/history`);
        const data = await response.json();
        const history = data.history || [];
        const tempData = history.filter(h => h.metric === 'temperature');

        chartData.value = {
            labels: tempData.map(h => new Date(h.time).toLocaleTimeString()),
            datasets: [
                {
                    label: 'Chamber Temperature',
                    data: tempData.map(h => h.value),
                    fill: false,
                    borderColor: '#3B82F6',
                    tension: 0.4,
                    pointRadius: 2
                },
                {
                    label: 'Safety Threshold (188°C)',
                    data: tempData.map(() => 188),
                    borderColor: '#EF4444',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        };
    } catch (error) {
        console.error("Failed to fetch telemetry from InfluxDB:", error);
    }
};

onMounted(() => {
    updateChart();
    setInterval(updateChart, 3000);
});
</script>

<template>
    <Card>
        <template #title>
            <div class="flex align-items-center gap-2">
                <i class="pi pi-chart-line text-blue-400"></i>
                <span>Live Telemetry (InfluxDB Stream)</span>
            </div>
        </template>
        <template #content>
            <div style="height: 350px;">
                <Chart v-if="chartData" type="line" :data="chartData" :options="chartOptions" class="h-full" />
                <div v-else class="h-full flex align-items-center justify-content-center border-round bg-gray-800 border-dashed border-1 border-gray-600">
                    <p class="text-gray-500">Connecting to InfluxDB...</p>
                </div>
            </div>
        </template>
    </Card>
</template>