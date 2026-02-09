<script setup>
import Chart from 'primevue/chart';
import { ref, onMounted } from 'vue';

const chartData = ref(null);
const chartOptions = ref({
    stacked: false,
    maintainAspectRatio: false,
    aspectRatio: 0.6,
    plugins: {
        legend: { labels: { color: '#495057' } }
    },
    scales: {
        x: { ticks: { color: '#495057' }, grid: { color: '#ebedef' } },
        y: { 
            min: 150, max: 200,
            ticks: { color: '#495057' }, 
            grid: { color: '#ebedef' },
            title: { display: true, text: 'Temperature (°C)' }
        }
    },
    animation: { duration: 500 }
});

const updateChart = async () => {
    try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL;
        const response = await fetch(`${baseUrl}/history`);
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
        console.error("Failed to fetch telemetry:", error);
    }
};

onMounted(() => {
    updateChart();
    setInterval(updateChart, 3000);
});
</script>

<template>
    <div style="height: 350px;">
        <Chart type="line" :data="chartData" :options="chartOptions" class="h-full" />
    </div>
</template>