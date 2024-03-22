<template>
    <div>
        <!-- Formulaire de téléchargement de fichiers CSV -->
        <input type="file" @change="handleFileUpload" accept=".csv">

        <!-- CSV data preview and feature selection -->
        <div class="table-container" v-if="csvPreviewData.length">
            <table>
                <thead>
                    <tr>
                        <th v-for="header in csvHeaders" :key="header">
                            {{ header }}
                            <input type="checkbox" :value="header" v-model="selectedFeatures">
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, index) in csvPreviewData" :key="index">
                        <td v-for="cell in row">{{ cell }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        
        <!-- Bouton d'inférence -->
        <button @click="submitPrediction">Prédire</button>
        <!-- Zone d'affichage du graphique -->
        <div v-if="predictions" ref="plotContainer"></div>
    </div>
</template>

<script>
import axios from 'axios';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

export default {
    props: {
        model: Object,
    },
    data() {
        return {
            file: null,
            csvHeaders: [],
            csvPreviewData: [],
            selectedFeatures: [],
            predictions: null,
            // Ajouter d'autres données nécessaires pour le modèle
        };
    },
    methods: {
        handleFileUpload(event) {
            this.file = event.target.files[0];
            Papa.parse(this.file, {
                complete: (result) => {
                    this.csvHeaders = result.meta.fields;
                    this.csvData = result.data;
                    // Supposons que vous ne voulez que les 5 premières lignes pour l'aperçu
                    this.csvPreviewData = this.csvData.slice(0, 5);
                },
                header: true,
                skipEmptyLines: true,
            });
        },
        async submitPrediction() {
        const formData = new FormData();
        formData.append('csv_file', this.file);
        formData.append('features', this.selectedFeatures);
        try {
            const response = await axios.post('http://localhost:8000/predict/'+this.model.id+'/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': 'Bearer ' + localStorage.getItem('jwt') // Assurez-vous d'envoyer le token d'autorisation
                },
            });
            this.predictions = response.data;
            this.$nextTick(() => {
                this.drawPlot();
            });
        } catch (error) {
            console.error("Erreur lors de la récupération des prédictions:", error);
        }
        },
        drawPlot() {
            if (this.predictions && this.$refs.plotContainer){
                const time = Object.values(this.predictions.predictions.time);
                const predictions = Object.values(this.predictions.predictions.predictions);
                if (Array.isArray(time) && Array.isArray(predictions) && time.length === predictions.length) {
                    const trace = {
                        x: time,  // Array of time values
                        y: predictions,  // Array of prediction values
                        mode: 'lines',
                        type: 'scatter',
                        name: 'Predictions'
                    };

                    const layout = {
                        title: 'Predictions Over Time',
                        xaxis: { title: 'Time' },
                        yaxis: { title: 'Predicted Value' }
                    };

                    Plotly.newPlot(this.$refs.plotContainer, [trace], layout);
                } else {
                    console.log('Type of time:', typeof time); 
                    console.log('Type of predictions:', typeof predictions);
                    console.error('The data for time or predictions is invalid');
                }
            }
        }
    }
};
</script>


