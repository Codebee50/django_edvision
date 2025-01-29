from django.urls import path
from . import views


urlpatterns = [
    path('messages/<uuid:diagram_id>/', views.GetDiagramMessagesView.as_view(), name='get-diagram-ids')
]