
<template>
    <div class="train-model-form">
      <h2>Train model</h2>
      <form @submit.prevent="submitForm">
        <input type="file" @change="handleFileUpload" accept=".csv">
        
        <div class="table-container" v-if="csvHeaders.length > 0">

          <!-- Datetime Column -->
          <label for="datetime_key">Colonne datetime</label>
          <select id="datetime_key" v-model="datetime_key">
            <option value="">None</option>
            <option v-for="(header, index) in csvHeaders" :key="`header-${index}`">
              {{ header }}
            </option>
          </select>

          <!-- Features & Target -->
          <table>
            <thead>
              <tr>
                <th 
                v-for="(header, index) in filteredHeaders"
                :key="`header-${index}`"
                v-if="header !== datetime_key"
                >
                  {{ header }}
                  <input type="radio" name="target" :value="header" v-model="target">
                  <input type="checkbox" :value="header" v-model="selectedFeatures">
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in filteredPreviewData" :key="`row-${rowIndex}`">
                <td v-for="(cell, cellIndex) in row" :key="`cell-${cellIndex}`" v-if="csvHeaders[cellIndex] !== datetime_key">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="columns.length > 0">
          <!-- Model Name -->
          <label for="name">Model Name:</label>
          <input id="name" type="text" placeholder="Model Name" v-model="modelName">

          <!-- Model Type -->
          <select v-model="modelType">
            <option disabled value="">Select a model type</option>
            <option>Linear Regression</option>
          </select>

          <!-- Nb Episode -->
          <label for="epochs">Number epochs:</label>
          <input id="epochs" type="number" v-model.number="epochs" placeholder="Epochs">
          <button type="submit" :disabled="isRequesting">
            <span v-if="isRequesting">Chargement...</span>
            <span v-else>Train Model</span>
          </button>
        </div>
      </form>

      <div v-if="trainResponse">
        <h3>{{ trainResponse.message }}</h3>
        {{ trainResponse.model_path }}
        <p>RRMSE: {{ trainResponse.rrmse }} %</p>
        <div ref="plotContainer"></div> 
        <button @click="createModel">Save Model</button>
      </div>
    </div>
  </template>
  
  <script>
    import axios from 'axios';
    import Papa from 'papaparse';
    import Plotly from 'plotly.js-dist-min'
    export default {
      data() {
        return {
          isRequesting: false,
          datetime_key:'',
          csvData: [],
          csvHeaders: [],
          csvPreviewData: [],
          file: null,
          modelName:'',
          columns: [],
          selectedFeatures: [],
          target: '',
          modelType: '',
          epochs: 0,
          train_test_size:80,
          batchSize:16,
          trainResponse:null,
          model: {
            name: '',
            features: '',
            taregt:'',
            metrics: '',
            parameters: '',
            path: ''
          }
        };
      },
      methods: {
        prepareModelData() {
          // Convertit la liste des features en chaîne de caractères JSON
          const featuresStr = JSON.stringify(this.selectedFeatures);

          // Crée un objet metrics avec la métrique rrmse (s'assurer que trainResponse est bien rempli)
          const metrics = this.trainResponse ? {'rrmse': this.trainResponse.rrmse} : {};

          // Chemin vers le modèle (s'assurer que trainResponse est bien rempli)
          const modelPath = this.trainResponse ? this.trainResponse.model_path : '';

          // Crée un objet parameters avec les paramètres du modèle
          const parameters = {
            'modelType': this.modelType,
            'train_test_size': this.train_test_size,
            'batch_size': this.batchSize,
            'epochs': this.epochs
          };

          // Met à jour l'objet model dans les données du composant
          this.model = {
            name: this.modelName,
            features: featuresStr,
            target:this.target,
            metrics: JSON.stringify(metrics), // Convertit l'objet metrics en chaîne de caractères JSON
            parameters: JSON.stringify(parameters), // Convertit l'objet parameters en chaîne de caractères JSON
            path: modelPath
          };
        },
        createModel() {
          this.prepareModelData();

          const apiUrl = 'http://localhost:8000/api/models/';
          const token = localStorage.getItem('jwt'); // Récupérer le token JWT stocké après la connexion
          
          // Configurer l'entête d'autorisation
          const authHeader = {
            headers: {
              Authorization: `Bearer ${token}`
            }
          };

          // Envoyer la requête POST
          axios.post(apiUrl, this.model, authHeader)
            .then(response => {
              console.log('Model created:', response.data);
              // Gérer la réponse ici, par exemple rediriger l'utilisateur ou afficher un message
              this.$emit('model-created');
            })
            .catch(error => {
              console.error('Error creating model:', error);
              // Gérer l'erreur ici, par exemple afficher un message à l'utilisateur
            });
        },  
        drawPlot() {
          if (!this.trainResponse || !this.trainResponse.predictions) {
            console.error("Données de prédiction non disponibles.");
            return;
          }
          const time = this.trainResponse.predictions.time;
          const predictions = this.trainResponse.predictions.predictions;

          const data = [{
            x: time,
            y: predictions,
            mode: 'lines',
            type: 'scatter',
            name: 'Speed Prediction'
          }];

          const layout = {
            title: 'Speed Predictions Over Time',
            xaxis: {
              title: 'Time'
            },
            yaxis: {
              title: 'predictions'
            }
          };

          Plotly.newPlot(this.$refs.plotContainer, data, layout);
        },
        handleFileUpload(event) {
          this.file = event.target.files[0];
          Papa.parse(this.file, {
            complete: (result) => {
              console.log(result.meta.fields)
              this.columns = result.meta.fields;
              this.csvHeaders = result.meta.fields;
              this.csvData = result.data.slice(1);
              this.csvPreviewData = this.csvData.slice(0, 5);
            },
            header: true,
            skipEmptyLines: true,
          });
        },
        submitForm() {
          this.isRequesting = true;
          const formData = new FormData();
          formData.append('csv_file', this.file);
          formData.append('features', this.selectedFeatures);
          formData.append('target', this.target);
          formData.append('model_type', this.modelType);
          formData.append('model_name', this.modelName);
          formData.append('train_test_size', this.train_test_size);
          formData.append('batch_size', this.batchSize);
          formData.append('epochs', this.epochs);
    
          axios.post('http://localhost:8000/train_model/', formData, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('jwt')}`,
              'Content-Type': 'multipart/form-data',
            },
          })
          .then(response => {
            console.log(response.data);
            this.trainResponse = response.data;
          })
          .catch(error => {
            console.error("Error:", error);
          })
          .finally(() => {
            this.isRequesting = false;
          });
        },
      },
      mounted() {
        this.$nextTick(() => {
          if (this.trainResponse) {
            this.drawPlot();
          }
        });
      },
      computed: {
        filteredHeaders() {
          return this.csvHeaders.filter(header => header !== this.datetime_key);
        },
        filteredPreviewData() {
          if (!this.datetime_key) return this.csvPreviewData;
          const datetimeIndex = this.csvHeaders.indexOf(this.datetime_key);
          return this.csvPreviewData.map(row =>{
            const filteredEntries = Object.entries(row).filter(([key, _]) => key !== this.datetime_key);
            return Object.fromEntries(filteredEntries);
        });
        }
      },
      watch: {
        trainResponse(newVal, oldVal) {
          if (newVal !== oldVal) {
            this.$nextTick(() => {
              this.drawPlot();
            });
          }
        }
      }
    };
  </script>
  
  <style>
    .train-model-form h2 {
      margin: 1rem 0;
      text-align: center;
    }

    .table-container {
      overflow-x: auto; 
      max-width: 100%; 
    }
    
    table {
      width: 100%;
    }
  
    .table-container table {
      transform-origin: top left;
    }
    

    .table-container table {
      font-size: 0.75rem;
    }
    
    .table-container th,
    .table-container td {
      padding: 0.25em;
    }

    input{
      color: aliceblue;
    }

    
  </style>