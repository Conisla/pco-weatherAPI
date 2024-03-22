from django.db import models
from django.contrib.auth.models import User

class Model(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    features = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    metrics = models.TextField()
    parameters = models.TextField()
    path = models.CharField(max_length=255)
    createdat = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    results = models.TextField()