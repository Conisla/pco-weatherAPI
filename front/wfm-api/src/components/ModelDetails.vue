<template>
  <div class="model-details">
    <div class="header">
      <h2>{{ model.name }}</h2>
      <p class="model-date">{{ formatDate(model.createdat) }}</p>
      <div class="metrics">{{ extractMetrics(model.metrics) }} %</div>
    </div>
    <div class="features tile">
      <h4>Features</h4>
      {{ model.features }}
    </div>
    <div class="target tile">
      <h4>Target</h4>
      {{ model.target }}
    </div>
    <div class="parameters tile">
      <h4>Parameters</h4>
      {{ model.parameters }}
    </div>
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

<style>
.model-details {
  display: flex;
  flex-direction: row;
  margin: auto;
  border-radius: 8px;
}

.header {
  color: #fff;
  padding: 20px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.model-details h2 {
  margin-top: 0;
}

.model-date {
  font-size: 0.9rem;
}

.tile {
  margin: 10px;
  padding: 15px;
  border-radius: 8px;

}

.metrics, .features, .target, .parameters {
  display: block;
  clear: both;
}

.tile:not(:last-child) {
  margin-bottom: 10px;
}
</style>
