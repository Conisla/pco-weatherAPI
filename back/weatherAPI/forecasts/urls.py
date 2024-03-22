from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelViewset

router = DefaultRouter()
router.register(r'models', ModelViewset, basename='model')

urlpatterns = [
    path('', include(router.urls)),
]