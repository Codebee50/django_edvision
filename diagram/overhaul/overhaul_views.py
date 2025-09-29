from rest_framework import generics
from common.responses import ErrorResponse, SuccessResponse
from common.utils import format_first_error, measure_time_decorator
from diagram.models import DatabaseColumn, DatabaseTable, Diagram, Relationship
from diagram.overhaul.utils import parse_relationship, update_or_create_column, update_or_create_relationship, update_or_create_table
from diagram.serializers import DatabaseTableSyncSerializer, DiagramDetailSerializer
from .overhaul_serializers import DiagramOverhaulSerializer, TableSerializer

class OverHaulDiagramView(generics.GenericAPIView):
    serializer_class= DiagramOverhaulSerializer
    
    # @measure_time_decorator
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
    
        try:
            diagram = Diagram.objects.prefetch_related('tables', 'relationships').get(id=serializer.validated_data.get('diagram_id'))
        except Diagram.DoesNotExist:
            return ErrorResponse(message="Diagram not found", status=404)
        
        table_list = serializer.validated_data.get('table_list')
                
        updated_table_ids = []
        updated_column_ids = []
        updated_relationship_ids= []
        
        all_existing_tables = diagram.tables.all()
        existing_table_dict = {table.id: table for table in all_existing_tables}
        
        all_existing_columns = DatabaseColumn.objects.filter(db_table__diagram=diagram)
        existing_column_dict = {column.id: column for column in all_existing_columns}
        
        all_existing_relationships = diagram.relationships.all()
        existing_relationship_dict = {relationship.id: relationship for relationship in all_existing_relationships}
        
        for req_table in table_list:
            req_table['table']['diagram'] = diagram.id
            column_list = req_table['table'].pop('columns', [])
            
            table = update_or_create_table(req_table.get('id'), req_table.get('table'), existing_table_dict, req_table.get('changed'))
            if table:
                updated_table_ids.append(table.id)
                for req_column in column_list:
                    req_column['column']['db_table'] = table.id
                    column = update_or_create_column(req_column.get('id'), req_column.get('column'), existing_column_dict, req_column.get('changed'))
                    if column:
                        updated_column_ids.append(column.id)
        
        for req_rel in serializer.validated_data.get('relationships'):
            req_rel['relationship']['diagram'] = diagram.id
            parsed_relationship = parse_relationship(req_rel.get('relationship'), existing_column_dict)
            relationship = update_or_create_relationship(req_rel.get('id'), parsed_relationship, diagram, existing_relationship_dict, req_rel.get('changed'))
            if relationship:
                updated_relationship_ids.append(relationship.id)
        
        
        deleted_items = serializer.validated_data.get('deleted_items')
        for item in deleted_items:
            if item.get('item_type') == 'table':
                DatabaseTable.objects.filter(diagram=diagram, id=item.get('item_id')).delete() 
            if item.get('item_type') == 'relationship':
                Relationship.objects.filter(diagram=diagram, id=item.get('item_id')).delete()
            if item.get('item_type') == 'column':
                DatabaseColumn.objects.filter(db_table__diagram=diagram, id=item.get('item_id')).delete()

        diagram = Diagram.objects.get(id=serializer.validated_data.get('diagram_id'))
        
        return SuccessResponse(message="Overhaul successful", data=DiagramDetailSerializer(diagram).data)