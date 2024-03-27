import csv
import os
import json
import pandas as pd
from .ml_utils import *
from sklearn.model_selection import train_test_split
from lazypredict.Supervised import LazyClassifier, LazyRegressor

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ModelSerializer

from .models import Model, Prediction
from .forms import TrainModelForm

from rest_framework import viewsets

class ModelViewset(viewsets.ModelViewSet):
    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Model.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # afficher les erreurs :
            print("Erreurs lors de la création :", serializer.errors)
            # Puis retourner une réponse avec ces erreurs :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            print(e)
            raise serializer.ValidationError({"Erreurs lors de la création :", serializer.errors})
    
@api_view(['POST'])
def train_model(request):
    form = TrainModelForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = form.cleaned_data['csv_file']
        features_list = form.cleaned_data['features'].split(',')  # Assurez-vous de les séparer correctement
        target = form.cleaned_data['target']
        model_type = form.cleaned_data['model_type']
        model_name = form.cleaned_data['model_name']
        train_test_size = form.cleaned_data['train_test_size']
        batch_size = form.cleaned_data['batch_size']
        epochs = form.cleaned_data['epochs']
        validation_split = 1 - (train_test_size / 100)
        
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return Response({'error': f'Error reading CSV file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            train_data, test_data = train_test_split(df, test_size=validation_split, shuffle=False)
            # Entraînez votre modèle ici
            model = create_linreg_model(train_data[features_list].shape[1], 1)

            history = model.fit(
                x=train_data[features_list],
                y=train_data[target],
                batch_size=batch_size,
                epochs=epochs,
                validation_split=validation_split
            )

            models_dir = os.path.join(settings.BASE_DIR, 'models')
            os.makedirs(models_dir, exist_ok=True)
            save_path = os.path.join(models_dir, f'{model_name}.keras')
            model.save(save_path)

            pred_array = model.predict(x=test_data[features_list])
            pred_data = test_data.copy()
            pred_data['predictions'] = pred_array

            rrmse = get_rrmse(pred_data,target,'predictions')

            return Response({
                'message': 'Model trained successfully',
                'rrmse': rrmse,
                'predictions':pred_data,
                'model_path': save_path,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Error training model: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print('form invalid')
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict(request, model_id):
    try:
        model_instance = Model.objects.get(id=model_id, user=request.user)
        model = load_keras_model(model_instance.path)
        
        # Lecture du fichier CSV
        csv_file = request.FILES['csv_file']
        df = pd.read_csv(csv_file)
        
        # Préparation des données d'entrée
        features = request.data.get('features').split(',')  # Transformer la chaîne de caractères en liste
    
        pred_array = model.predict(x=df[features])
        pred_data = df.copy()
        pred_data['predictions'] = pred_array
        pred_data_dict = pred_data.to_dict()
        
        # Optionnel : Calcul du rRMSE si les données réelles et prédites sont disponibles
        # Vous devrez adapter cette partie en fonction de vos données spécifiques
        # rrmse = get_rrmse(df, 'colonne_mesuree', 'colonne_predite')

        return JsonResponse({'predictions':pred_data_dict})
    except Model.DoesNotExist:
        return JsonResponse({'error': 'Modèle non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def automl(request):
    try:
        # Lecture du fichier CSV
        csv_file = request.FILES['file']
        list_features = request.POST.get('features')
        list_features = list_features.split(',')
        target_column = request.POST.get('target')
        datetime_key = request.POST.get('datetime_key')
        model_list = request.POST.get('models_list')
        model_list = model_list.split(',')

        df = pd.read_csv(csv_file)
        print('csv loaded')

        X = df[list_features]
        
        y = df[target_column]
        
        # Division des données
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
    
        # Détermination du type de problème (classification ou régression)
        if set(y.unique()) == {0, 1}:
            clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None, predictions=True)
            models, predictions = clf.fit(X_train, X_test, y_train, y_test)
        else:
            clf = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None, predictions=True)
            models, predictions = clf.fit(X_train, X_test, y_train, y_test)

        df_test = df.loc[:int(df.shape[0] * 0.2)]
        df_test[datetime_key] = pd.to_datetime(df_test[datetime_key])
        df_test_sorted = df_test.sort_values(by=datetime_key)
        
        print('passed : df_test creation')
        models_perf = {}
        print('passed : models_perf creation')

        best_models = models[:3].index.to_list()

        for model in best_models : 
            print(model)
            df_test_sorted[model] = predictions[model].values
            models_perf[model] = get_rrmse(df_test_sorted,target_column,model)
            print('passed : ', model)

        for model_id in model_list:
            model_instance = Model.objects.get(id=model_id, user=request.user)
            model = load_keras_model(model_instance.path)
            pred_array = model.predict(x=X_test)
            df_test_sorted[model_instance.name] = pred_array
            models_perf[model_instance.name] = get_rrmse(df_test_sorted,target_column,model_instance.name)
            print('passed : ', model_instance.name)

        print(type(models_perf))
        print(type(df_test_sorted.to_dict()))

        return JsonResponse({
            'message': 'AutoML completed successfully',
            'models_performance': models_perf,
            'predictions': df_test_sorted.to_dict(orient='records'),
            }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)