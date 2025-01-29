from rest_framework import generics
from .serializers import  DiagramCreateSerializer, DiagramDetailSerializer, \
    DatabaseTableCreateSerializer, DatabasePositionsSerializer ,DatabaseTableSyncSerializer, \
        RelationshipCreateSerializer, DatabaseColumnCreateSerializer, DatabaseColumnSerializer, RelationshipSerializer
from rest_framework.permissions import IsAuthenticated
from common.utils import format_first_error
from common.responses import ErrorResponse, SuccessResponse
from .models import Diagram, DatabaseTable, DatabaseColumn, Relationship
from .datatypes import mappings
# Create your views here.





class DeleteDiagramView(generics.DestroyAPIView):
    queryset = Diagram.objects.all()
    lookup_field='id'
    permission_classes = [IsAuthenticated]


class GetDatatypeList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        datatype = kwargs.get('type')
        
        type_list = mappings.get(datatype, [])
        return SuccessResponse(message=f"Datatypes for {datatype}", data=type_list)
        

class UpdateRelationShipView(generics.UpdateAPIView):
    queryset = Relationship.objects.all()
    lookup_field ='id'
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticated]

class SyncDatabaseColumn(generics.UpdateAPIView):
    serializer_class = DatabaseColumnSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatabaseColumn.objects.all()
    lookup_field = 'id'


class SyncDatabaseTable(generics.UpdateAPIView):
    serializer_class = DatabaseTableSyncSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatabaseTable.objects.all()
    lookup_field = 'id'
    

class UpdateTablePosition(generics.GenericAPIView):
    serializer_class = DatabasePositionsSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        table_id = kwargs.get('id')
        x_position = request.data.get('x_position')
        y_position = request.data.get('y_position')
        
        try:
            table = DatabaseTable.objects.get(id=table_id)
            table.x_position = x_position
            table.y_position = y_position
            table.save()
        except DatabaseTable.DoesNotExist:
            return ErrorResponse(message="Table not found")
        return SuccessResponse(message="Table position updated successfully")


class RelationshipDeleteView(generics.DestroyAPIView):
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    queryset = Relationship.objects.all()


class RelationshipCreateView(generics.CreateAPIView):
    serializer_class = RelationshipCreateSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data =request.data)
        if serializer.is_valid():
            from_column = serializer.validated_data.get('from_column')
            response = serializer.save(diagram=from_column.db_table.diagram)
            return SuccessResponse(message="Relationship created successfully", data=RelationshipSerializer(response).data)
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))

class DatabaseColumnCreateView(generics.CreateAPIView):
    serializer_class = DatabaseColumnCreateSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class DatabaseTableCreateView(generics.CreateAPIView):
    serializer_class = DatabaseTableCreateSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class DiagramDetailView(generics.RetrieveAPIView):
    """
    Get diagram by id 
    
    ---
    """
    serializer_class = DiagramDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        return Diagram.objects.all()
    # def get_queryset(self):
    #     return Diagram.objects.filter(creator=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class UserDiagramsListView(generics.ListAPIView):
    serializer_class = DiagramCreateSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Diagram.objects.filter(creator=user)


class CreateDiagramView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiagramCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().create(request, *args, **kwargs)
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))