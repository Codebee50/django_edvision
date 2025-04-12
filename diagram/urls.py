from django.urls import path
from . import views
from .overhaul import overhaul_views

urlpatterns = [
    path('create/', views.CreateDiagramView.as_view(), name='create-diagram'),
    path('list/', views.UserDiagramsListView.as_view(), name='list-diagrams'),
    path('detail/<uuid:id>/', views.DiagramDetailView.as_view(), name='diagram-detail'),
    path('table/create/', views.DatabaseTableCreateView.as_view(), name='database-table-create-view'),
    path('table/position/update/<int:id>/', views.UpdateTablePosition.as_view(), name='update-table-position'),
    path('table/sync/<int:id>/', views.SyncDatabaseTable.as_view(), name='sync-table'),
    path('table/delete/<int:id>/', views.DeleteTableView.as_view(), name='delete-table'),
    
    path('column/create/', views.DatabaseColumnCreateView.as_view(), name='create-db-column'),
    path('column/delete/<int:id>/', views.ColumnDeleteView.as_view(), name='delete-db-column'),
    
    path('relationship/create/', views.RelationshipCreateView.as_view(), name='create-relationship'),
    path('column/sync/<int:id>/', views.SyncDatabaseColumn.as_view(), name='sync-column'),
    path('relationship/delete/<int:id>/', views.RelationshipDeleteView.as_view(), name='delete-relationship'),
    path('relationship/sync/<int:id>/', views.UpdateRelationShipView.as_view(), name='update-relationship'),
    
    path('datatypes/<str:type>/', views.GetDatatypeList.as_view(), name='get-datatype-list'),
    path('delete/<uuid:id>/', views.DeleteDiagramView.as_view(), name='delete-diagram-view'),
    
    path('invite/<uuid:diagram_id>/', views.InviteUserView.as_view(), name='invite-user'),
    path('members/<uuid:diagram_id>/', views.GetDiagramMembers.as_view(), name='diagram-members'),
    path('access/grant/',views.GrantWriteRequestView.as_view(), name='grant-write-request'),
    path('overhaul/', overhaul_views.OverHaulDiagramView.as_view(), name='overhaul-diagram')

]