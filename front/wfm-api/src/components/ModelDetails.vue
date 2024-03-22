<template>
  <div class="model-details">
    <h2>{{ model.name }}</h2>
    <p class="model-date">{{ formatDate(model.createdat) }}</p>
    <p>{{ extractMetrics(model.metrics) }} %</p>
  </div>
</template>

<script>
export default {
  props: {
    model: Object,
  },
  methods:{
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
        return entries.map(([key, value]) => `${key} : ${value}`).join(', ');
      } catch (e) {
        console.error("Error parsing metrics JSON:", e);
        return "Invalid metrics data";
      }
    }
  },
  created(){
    console.log(this.model);
  }
};
</script>
