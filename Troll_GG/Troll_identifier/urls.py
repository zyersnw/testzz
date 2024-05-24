from django.urls import path
from .views import troll_identifier

app_name = 'Troll_identifier'  # 앱의 이름을 지정합니다.
urlpatterns = [
    path('', troll_identifier, name='troll_identifier'),
]
