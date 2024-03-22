<template>
  <div>
    <nav-bar></nav-bar>
    <div class="main">
      <SideBar @model-selected="showModelDetails" />
      <div v-if="selectedModel" class="container">
         <!-- Zone d'affichage des détails du modèle -->
        <ModelDetails :model="selectedModel" />
        <!-- Formulaire d'inférence -->
        <PredictionForm :model="selectedModel"/>
      </div>
     
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
import TrainForm from '@/components/TrainForm.vue'
import SideBar from '../components/SideBar.vue';
import ModelDetails from '../components/ModelDetails.vue'
import PredictionForm from '@/components/PredictionForm.vue';

export default {
  data() {
    return {
      isTrainFormVisible: false,
      models: [],
      selectedModel:  null
    };
  },
  components: {
    NavBar,
    TrainForm,
    SideBar,
    ModelDetails,
    PredictionForm
  },
  methods: {
    showModelDetails(model) {
      this.selectedModel = model;
      // Activez une section pour afficher les détails ou un formulaire
    },
    async refreshToken() {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('http://localhost:8000/login/refresh/', {
          refresh: refreshToken,
        });
        localStorage.setItem('accessToken', response.data.access);
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      } catch (error) {
        console.error('Error refreshing token:', error);
      }
    }
  },
  mounted() {
    this.refreshToken()
    console.log('new token');
  },
};
</script>

<style>

.main{
  display: flex;
  padding-top: 8px;
  height: 88vh; /* Ajustez avec la hauteur de votre navbar */

}
.container{
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%; /* Ajustez selon l'espace que vous voulez allouer au contenu défilant */
  height: 100%; /* Prend toute la hauteur disponible */
}

</style>
