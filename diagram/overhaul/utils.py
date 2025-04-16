from uuid import UUID
from diagram.overhaul.overhaul_serializers import RelSerializer
from ..serializers import DatabaseColumnCreateSerializer, DatabaseColumnSerializer, DatabaseColumnUpdateSerializer, DatabaseTableSyncSerializer, DatabaseTableCreateSerializer, RelationshipCreateSerializer, RelationshipSerializer
from ..models import DatabaseColumn, DatabaseTable, Relationship


def parse_relationship(relationship):
    from_column_value = relationship.get('from_column')
    print('the from column value', from_column_value)
    
    if from_column_value and isinstance(from_column_value, str):
        try:
            try:
                column_id = int(from_column_value)
                relationship['from_column'] = column_id
            except ValueError:
                print('attempting to get column from uuid')
                uuid_obj = UUID(from_column_value)
                column = DatabaseColumn.objects.filter(flow_id=uuid_obj).first()
                print('column from uuid', column)
                if column:
                    relationship['from_column'] = column.id
        except (ValueError, TypeError):
            pass
    
    to_column_value = relationship.get('to_column')
    if to_column_value and isinstance(to_column_value, str):
        try:
            try:
                column_id = int(to_column_value)
                relationship['to_column'] = column_id
            except ValueError:
                uuid_obj = UUID(to_column_value)
                column = DatabaseColumn.objects.filter(flow_id=uuid_obj).first()
                if column:
                    relationship['to_column'] = column.id
        except (ValueError, TypeError):
            pass
    return relationship

def update_or_create_table(table_id, table_data) -> DatabaseTable:
    existing_table = DatabaseTable.objects.filter(id=table_id).first() if table_id else None
    if existing_table:
        table_serializer = DatabaseTableSyncSerializer(existing_table, data=table_data, partial=True)
    else:
        table_serializer = DatabaseTableCreateSerializer(data=table_data)
    if table_serializer.is_valid():
            return table_serializer.save()
    return None

def update_or_create_column(column_id, column_data):
    existing_column = DatabaseColumn.objects.filter(id=column_id).first() if column_id else None
    if existing_column:
        column_serializer = DatabaseColumnUpdateSerializer(existing_column, data=column_data, partial=True)
    else:
        column_serializer = DatabaseColumnCreateSerializer(data=column_data)

    
    if column_serializer.is_valid():
        return column_serializer.save()
    return None

def update_or_create_relationship(relationship_id, relationship_data, diagram):
    print('rel', relationship_data)
    existing_relationship = Relationship.objects.filter(id=relationship_id).first() if relationship_id else None
    if existing_relationship:
        relationship_serializer = RelationshipSerializer(existing_relationship, data=relationship_data, partial=True)
    else:
        relationship_serializer = RelationshipCreateSerializer(data=relationship_data)
    
    
    if relationship_serializer.is_valid():
        return relationship_serializer.save(diagram=diagram)
    return None