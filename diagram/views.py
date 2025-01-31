from rest_framework import generics
from .serializers import  *
from rest_framework.permissions import IsAuthenticated
from common.utils import format_first_error
from common.responses import ErrorResponse, SuccessResponse
from .models import Diagram, DatabaseTable, DatabaseColumn, Relationship, DiagramMember
from .datatypes import mappings
from account.services import send_invite_email

# Create your views here.

class GrantWriteRequestView(generics.GenericAPIView):
    serializer_class = GrantWriteRequestSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            grant_to_id = serializer.validated_data.get('grant_to')
            diagram_id = serializer.validated_data.get('diagram')
            
            try:
                diagram = Diagram.objects.get(id=diagram_id)
            except Diagram.DoesNotExist:
                return ErrorResponse(message="Diagram not found")
            
            try:
                grant_to = UserAccount.objects.get(id=grant_to_id)
            except UserAccount.DoesNotExist:
                return ErrorResponse(message="User not found")
            
            if diagram.creator == request.user or diagram.writer == request.user:
                diagram.writer = grant_to
                diagram.save()
                return SuccessResponse(message="Access granted successfully", data=UserSerializer(grant_to).data)
            
            return ErrorResponse(message="You cannot grant access on this diagram currently")
            
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))

class GetDiagramMembers(generics.GenericAPIView):
    serializer_class = DiagramMemberSerializer
    def get(self, request, *args, **kwargs):
        try:
            diagram = Diagram.objects.get(id=kwargs.get('diagram_id'))
        except Diagram.DoesNotExist:
            return ErrorResponse(message="Diagram does not exist")
        
        members = DiagramMember.objects.filter(diagram=diagram)
        return SuccessResponse(message="members", data=self.get_serializer(members, many=True).data)        


class InviteUserView(generics.GenericAPIView):
    serializer_class = InviteUserSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                diagram = Diagram.objects.get(id=kwargs.get('diagram_id'))
            except Diagram.DoesNotExist:
                return ErrorResponse(message="Diagram not found")
            
            if request.user != diagram.creator:
                return ErrorResponse(message="Oops, only creators are allowed to invite members")
            
            user = UserAccount.objects.get(email=email)
            if DiagramMember.objects.filter(diagram=diagram, user=user).exists()  or email==diagram.creator.email:
                return ErrorResponse(message="User is already a member")
            
            
            diagram_member = DiagramMember.objects.create(user=user, diagram=diagram)
            send_invite_email(user.email, diagram)
            return SuccessResponse(message=f"{user.first_name} {user.last_name} has been invited successfully", data=DiagramMemberSerializer(diagram_member).data)
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))
        
        

class DeleteTableView(generics.DestroyAPIView):
    queryset = DatabaseTable.objects.all()
    lookup_field = 'id'
    permission_classes= [IsAuthenticated]

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