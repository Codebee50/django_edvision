from uuid import UUID
from ..serializers import DatabaseColumnUpdateSerializer, DatabaseOverhaulColumnCreateSerializer, DatabaseTableSyncSerializer, DatabaseTableCreateSerializer, RelationshipCreateSerializer, RelationshipSerializer
from ..models import DatabaseTable


def parse_relationship(relationship, existing_columns:dict=None):
    from_column_value = relationship.get('from_column')
    # print('the from column value', from_column_value)
    
    if from_column_value and isinstance(from_column_value, str):
        try:
            try:
                column_id = int(from_column_value)
                relationship['from_column'] = column_id
            except ValueError:
                # print('attempting to get column from uuid')
                uuid_obj = UUID(from_column_value)
                column = existing_columns.get(uuid_obj)
                # print('column from uuid', column)
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
                column = existing_columns.get(uuid_obj)
                if column:
                    relationship['to_column'] = column.id
        except (ValueError, TypeError):
            pass
    return relationship

def update_or_create_table(table_id, table_data, existing_tables:dict=None, changed:bool=True) -> DatabaseTable:
    existing_table = None
    
    if table_id and existing_tables:
        existing_table = existing_tables.get(table_id)
        
    if existing_table and not changed: #the table already exists on our db and it was not changed on the frontend
        return existing_table
    
    if existing_table:
        table_serializer = DatabaseTableSyncSerializer(existing_table, data=table_data, partial=True)
    else:
        table_serializer = DatabaseTableCreateSerializer(data=table_data)
    if table_serializer.is_valid():
            return table_serializer.save()
    return None

def update_or_create_column(column_id, column_data, existing_columns:dict=None, changed:bool=True):
    existing_column = None
    if column_id and existing_columns:
        existing_column = existing_columns.get(column_id)
    
    if existing_column and not changed: #the column already exists on our db and it was not changed on the frontend
        return existing_column
        
    if existing_column:
        column_serializer = DatabaseColumnUpdateSerializer(existing_column, data=column_data, partial=True)
    else:
        column_serializer = DatabaseOverhaulColumnCreateSerializer(data=column_data)

    
    if column_serializer.is_valid():
        return column_serializer.save()
    return None

def update_or_create_relationship(relationship_id, relationship_data, diagram, existing_relationships:dict=None, changed:bool=True):
    existing_relationship = None
    if relationship_id and existing_relationships:
        existing_relationship = existing_relationships.get(relationship_id)
        
    if existing_relationship and not changed: #the relationship already exists on our db and it was not changed on the frontend
        return existing_relationship
    
    if existing_relationship:
        relationship_serializer = RelationshipSerializer(existing_relationship, data=relationship_data, partial=True)
    else:
        relationship_serializer = RelationshipCreateSerializer(data=relationship_data)
    
    
    if relationship_serializer.is_valid():
        return relationship_serializer.save(diagram=diagram)
    return None