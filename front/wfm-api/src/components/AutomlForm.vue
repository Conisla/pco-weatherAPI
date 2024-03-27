<template>
    <div class="form-container">
        <!-- Formulaire de téléchargement de fichiers CSV -->
        <input type="file" @change="handleFileUpload" accept=".csv">
        
        <!-- CSV data preview and feature selection -->
        <div class="table-container" v-if="csvPreviewData.length">
            <!-- datetime_key -->
            <label for="datetime_key">Colonne datetime</label>
            <select id="datetime_key" v-model="datetime_key">
                <option value="">None</option>
                <option v-for="(header, index) in csvHeaders" :key="`header-${index}`">
                    {{ header }}
                </option>
            </select>
            <!-- Features & Target -->
            <p>Selected Features : {{selectedFeatures}}</p>
            <p>Target : {{ target }}</p>
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
        
        <!-- Liste des modèles entrainés à utiliser -->
        <div class="dropdown">
            <button class="dropdown-toggle" @click="toggleDropdown">
                Select Models {{ selectedModels }}
            </button>
            <div v-if="showDropdown" class="dropdown-menu">
                <label v-for="(model, index) in list_models" :key="model.id" class="dropdown-item">
                    <input type="checkbox" :value="model.id" v-model="selectedModels">
                    {{ model.name }}
                </label>
            </div>
        </div>
    </div>
    <!-- Bouton d'inférence -->
    <button class="submit-btn" @click="submitAutoML" :disabled="!isFormValid || isRequesting">
        <span v-if="isRequesting">Chargement...</span>
        <span v-else>AutoML</span>
    </button>
    
    <div v-if="predictions" class="result-table">
        
        <!-- Zone d'affichage du graphique -->
        <div ref="plotContainer"></div>
        
        <!-- Tableau pour afficher les performances des modèles -->
        <table>
            <thead>
                <tr>
                    <th>ModelName</th>
                    <th>rrmse</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(rrmse, modelName) in models_performance" :key="modelName">
                    <td>{{ modelName }}</td>
                    <td>{{ rrmse }} %</td>
                </tr>
            </tbody>
        </table>
    </div> 
    
</div>
</template>

<script>
import axios from 'axios';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

export default {
    props: {
        list_models: Object,
    },
    data() {
        return {
            predictions:null,
            isRequesting:false,
            datetime_key:'',
            columns: [],
            csvHeaders: [],
            csvData: [],
            csvPreviewData: [],
            selectedFeatures: [],
            selectedTarget: '',
            file: null,
            models:[],
            selectedModels: [],
            showDropdown: false,
            features: [], 
            target: [],
            models_performance:null,
            best_predictions: null
        };
    },
    methods: {
        toggleDropdown(){
            this.showDropdown = !this.showDropdown
            console.log(this.selectedModels);
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
        transformModelData(jsonData) {
            const metricKeys = Object.keys(jsonData);
            let modelsList = [];
            metricKeys.forEach((metric) => {
                Object.keys(jsonData[metric]).forEach((modelName) => {
                    let model = modelsList.find(model => model.name === modelName);
                    if (!model) {
                        model = { name: modelName };
                        modelsList.push(model);
                    }
                    model[metric] = jsonData[metric][modelName];
                });
            });
            return modelsList;
        },
        submitAutoML() {
            this.isRequesting = true
            const formData = new FormData();
            formData.append('file', this.file);
            formData.append('features', this.selectedFeatures.join(','));
            formData.append('target', this.target);
            formData.append('datetime_key', this.datetime_key);
            formData.append('models_list', this.selectedModels);
            
            axios.post('http://localhost:8000/automl/', formData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`,
                    'Content-Type': 'multipart/form-data',
                },
            })
            .then(response => {
                console.log(response.data);
                this.predictions = response.data;
                this.models_performance = this.predictions.models_performance;
                this.best_predictions = this.predictions.predictions
                
                this.$nextTick(() => {
                    this.drawPlot();
                });
            })
            .catch(error => {
                
                console.error("Error:", error);
            })
            .finally(() => {
                this.isRequesting = false;
            });
        },
        drawPlot() {
            if (this.predictions && this.$refs.plotContainer) {
                const time = this.best_predictions.map(p => p.time);
                
                let traces = [];
                
                const modelNames = Object.keys(this.models_performance);
                
                console.log(modelNames)
                modelNames.forEach((modelName, index) => {
                    // On suppose ici que this.best_predictions est un tableau d'objets et que chaque objet contient les prédictions pour un modèle
                    const modelPredictions = this.best_predictions.map(p => p[modelName]);
                    
                    if (modelPredictions && modelPredictions.length > 0) {
                        traces.push({
                            x: time, // l'axe X commun pour toutes les prédictions
                            y: modelPredictions, // les prédictions pour le modèle spécifique
                            mode: 'lines',
                            type: 'scatter',
                            name: modelName, // nom du modèle
                            line: { color: this.getColorForModel(index, modelNames.length) }
                        });
                    }
                });
                console.log(traces.length)
                if (traces.length > 0) {
                    const layout = {
                        title: 'Predictions AutoML',
                        xaxis: { title: 'Time' },
                        yaxis: { title: 'Predicted Value' }
                    };
                    
                    Plotly.newPlot(this.$refs.plotContainer, traces, layout);
                } else {
                    console.error('No valid prediction data available to plot.');
                }
            }
        },
        
        getColorForModel(index, totalModels) {
            const hue = (index / totalModels) * 360;
            return `hsl(${hue}, 100%, 50%)`;
        }
        
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
        },
        isFormValid() {
            return (
            this.file 
            && this.target.length > 0 
            && this.selectedFeatures.length > 0 
            && this.selectedModels.length > 0
            );
        }
    },
};
</script>

<style>
.form-container{
    background-color: #bbf5ed1c;
    align-items: center;
    padding: 3% 5%;
    margin:2% 5%;
    border-radius: 25px;
}

.automl-form {
    display: flex;
    flex-direction: column;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
}

.form-group select {
    width: 100%;
    padding: 0.5em;
    margin-top: 0.5em;
}

.table-container{
    display: block;
    height: 100%;
    
}

button {
    padding: 0.5em 1em;
    border: none;
    cursor: pointer;
}

.submit-btn{
    align-self: center;
    margin-top : 10px;
}


.dropdown {
    position: relative;
}

.dropdown-toggle {
    /* Utilisez les styles PicoCSS pour les boutons, si désiré */
}

.dropdown-menu {
    position: absolute;
    left: 0;
    right: 0;
    /*background-color: white;*/
    border: 1px solid #ccc;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.dropdown-menu.show {
    display: block;
}

.dropdown-item {
    padding: 0.5rem 1rem;
    cursor: pointer;
    display: block;
}

.dropdown-item input[type="checkbox"] {
    margin-right: 0.5rem;
}
</style>
