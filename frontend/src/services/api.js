const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const TelemetryService = {
    async getHistory() {
        const response = await fetch(`${BASE_URL}/history`);
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    },

    async getQuarantineLogs() {
        const response = await fetch(`${BASE_URL}/quarantine`);
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    }
};