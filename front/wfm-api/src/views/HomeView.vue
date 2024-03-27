<template>
  <div class="grid-container">
    <nav-bar class="navbar"></nav-bar>
    <SideBar @model-selected="showModelDetails" @open-automl-form="showAutomlForm" class="sidebar" />
    <div class="content">
      <!-- Zone d'affichage des détails du modèle et formulaire d'inférence -->
      <div v-if="isDetailsVisible" class="container predict">
        <ModelDetails :model="selectedModel" />
        <PredictionForm :key="predictionFormKey" :model="selectedModel" />
      </div>
      <div v-if="isAutomlFormVisible" class="container">
        <AutomlForm @close="hideAutomlForm" :list_models="models" />
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";
import NavBar from "../components/NavBar.vue";
import TrainForm from "@/components/TrainForm.vue";
import SideBar from "../components/SideBar.vue";
import ModelDetails from "../components/ModelDetails.vue";
import PredictionForm from "@/components/PredictionForm.vue";
import AutomlForm from "@/components/AutomlForm.vue";

export default {
  data() {
    return {
      isTrainFormVisible: false,
      isDetailsVisible: false,
      models: [],
      selectedModel: null,
      predictionFormKey:0,
      isAutomlFormVisible: false,
    };
  },
  components: {
    NavBar,
    TrainForm,
    SideBar,
    ModelDetails,
    PredictionForm,
    AutomlForm
  },
  methods: {
    showModelDetails(model) {
      if (this.isAutomlFormVisible) {
        this.hideAutomlForm()
      }
      this.selectedModel = model;
      this.isDetailsVisible = true;
      this.resetPredictionForm();
    },
    hideModelDetails() {
      this.isDetailsVisible = false; 
      this.selectedModel = null;
    },
    async refreshToken() {
      try {
        const response = await axios.post(
          "http://localhost:8000/login/refresh/",
          {
            refresh: localStorage.getItem("jwt_refresh"),
          }
        );
        localStorage.setItem("jwt", response.data.access);
        axios.defaults.headers.common["Authorization"] =
          "Bearer " + response.data.access;
      } catch (error) {
        console.error(error);
      } 
    },
    resetPredictionForm() {
      this.predictionFormKey++; // Incrémente la clé pour forcer la réinitialisation
    },
    showAutomlForm() {
      this.hideModelDetails()
      this.models = this.fetchModels()
      this.isAutomlFormVisible = true;
    },
    hideAutomlForm() {
      this.isAutomlFormVisible = false;
    },
    async fetchModels() {
      try {
        const response = await axios.get('http://localhost:8000/api/models/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt')}`
          }
        });
        this.models = response.data;
      } catch (error) {
        console.error('There was an error fetching the models:', error);
      }
    },
  },
  created() {
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          await this.refreshToken();
          return axios(originalRequest);
        }
        return Promise.reject(error);
      }
    );
  },
  mounted(){
    this.models = this.fetchModels()
  }
};
</script>

<style>
.grid-container {
  display: grid;
  grid-template-columns: 250px 1fr; /* Sidebar width and remaining space */
  grid-template-rows: auto 1fr; /* Navbar height and remaining space */
  height: 100vh; /* Full viewport height */
  gap: 2%;
}

.navbar {
  grid-column: 1 / -1; /* Navbar spans the whole width */
  grid-row: 1;
}

.sidebar {
  grid-column: 1;
  grid-row: 2;
}

.content {
  grid-column: 2;
  grid-row: 2;
  overflow-y: auto;
  overflow-X: hidden;
  width: 100%;

}

.predict{
  margin: 2% 5%;
  width: 90%;
}
</style>


