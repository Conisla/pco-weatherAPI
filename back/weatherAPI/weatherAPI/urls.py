from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from forecasts.views import train_model, predict

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('train_model/', train_model, name='train_model'),
    path('predict/<int:model_id>/', predict, name='predict'),
    path('api/', include('forecasts.urls'))

]
