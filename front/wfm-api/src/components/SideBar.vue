<template>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>Mes modèles</h1>
            <!-- Bouton pour ouvrir le modal -->
            <button @click="toggleTrainForm" class="btn-create-model">+</button>
        
            <!-- Modal -->
            <div v-if="isTrainFormVisible" class="modal ">
                <div class="modal-content">
                    <span class="close" @click="toggleTrainForm">&times;</span>
                    <TrainForm @model-created="handleModelCreated"/>
                </div>
            </div>
        </div>
        <div class="model_list">
            <div class="before-blur"></div>
            <ModelCard v-for="model in models" :key="model.name" :model="model" @click="selectModel(model)" />
            <div class="after-blur"></div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import ModelCard from './ModelCard.vue'
import TrainForm from './TrainForm.vue';

export default {
    name:'SideBar',
    components:{
        ModelCard,
        TrainForm,
    },
    data() {
    return {
        isTrainFormVisible: false,
        models: [],
        selectedModel: null
    };
  },
  methods: {
    selectModel(model) {
      this.selectedModel = model;
      console.log(model);
      this.$emit('model-selected', model);
    },
    toggleTrainForm() {
      this.isTrainFormVisible = !this.isTrainFormVisible;
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
    handleModelCreated() {
      this.toggleTrainForm();
      this.fetchModels();
    }
  },
  created() {
    this.fetchModels();
  },
}
</script>

<style scoped>

.sidebar{
    width: 270px;
    height: 85vh;
    border-radius: 0px 45px 45px 0px;
    align-self: center;
    display: flex;
    flex-direction: column;
    background-color: #d5e1f0cb;
    margin-right: 1rem;
    box-shadow: inset 0px 0px 8px 2px rgba(0, 19, 30, 0.542),
                0px 0px 8px 2px rgba(95, 102, 106, 0.542);
}

.sidebar-header {
    width: 80%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin: 20px auto;
    align-items : center;
}

.sidebar-header .btn-create-model{

    display: flex;
    padding: 0;
    width: 50px;
    height: 50px;
    font-weight: bolder;
    font-size: 24px;
    border-radius: 50%;
    border: 0;
    justify-content: center;
    text-align: center;
    align-items: center;
    background-color: #5C8FBF;
}
.sidebar-header h1 {
    font-size: 24px;
    color: black;
    font-weight: bold;
}

.sidebar .model_list {
    margin-right: 10px;
    height: 80%;
    overflow-y: scroll;
}

/* SCROLLBAR */
/* width */
::-webkit-scrollbar {
    width: 15px;
}

/* Track */
::-webkit-scrollbar-track {
  background-color: #00000020;
  border-radius: 10px;
}
 
/* Handle */
::-webkit-scrollbar-thumb {
  background: #77808ba6; 
  border-radius: 10px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
    background-color: #77808b;
}

.modal {
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.4);
    border: 0;
    
  }
  
  .modal-content {
    background-color: #0036465c;
    margin: 10% auto;
    padding: 20px;

    width: 80%;
    backdrop-filter: blur(10px); /* Flou sur l'arrière-plan */
    border-radius: 25px;
  }
  
  .close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
  }
  
  .close:hover,
  .close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
  }
</style>
