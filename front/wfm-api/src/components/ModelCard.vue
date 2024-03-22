<template>
  <div class="model-card">
    <div class="model-header">
      <h2>{{ model.name }}</h2>
      <p class="model-date">{{ formatDate(model.createdat) }}</p>
    </div>
    <div class="model-metrics">
      <p>{{ extractMetrics(model.metrics) }} %</p>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    model: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-GB'); // Format DD/MM/YYYY
    },
    extractMetrics(metricsString) {
      try {
        // Remplacez les guillemets simples par des guillemets doubles pour le JSON
        // et échappez les guillemets doubles à l'intérieur des valeurs si nécessaire
        const validJsonString = metricsString.replace(/'/g, '"').replace(/\\/, '\\\\');
        const metricsObject = JSON.parse(validJsonString);
        const entries = Object.entries(metricsObject);

        // Créez une chaîne de texte avec toutes les entrées du JSON
        return entries.map(([key, value]) => `${key} = ${value}`).join(', ');
      } catch (e) {
        console.error("Error parsing metrics JSON:", e);
        return "Invalid metrics data";
      }
    }
  }
};
</script>
<style scoped>
.model-card {
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 10px;
  padding: 15px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-header h2 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.model-date {
  margin: 0;
  color: #666;
  font-size: 11px;
}

.model-metrics {
  margin-top: 20px;
}

.model-metrics p {
  margin: 0;
  color: #333;
  font-size: 1rem;
}
</style>