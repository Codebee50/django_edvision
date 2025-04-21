from http import server
from rest_framework import serializers

from diagram.models import DatabaseColumn, DatabaseTable, Relationship
from ..serializers import DatabaseTableSerializer, RelationshipSerializer
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID
import uuid


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = DatabaseColumn
        read_only_fields = ["synced", "db_table"]

    def to_internal_value(self, data):
        print("executing to internal", data.get("flow_id"))
        """Set flow_id to None if an invalid UUID is provided"""
        if "flow_id" in data:
            if isinstance(data.get("flow_id", 0), int):
                data.pop("flow_id")  # Remove if it's an integer
            else:
                try:
                    data["flow_id"] = str(uuid.UUID(data["flow_id"])) if data["flow_id"] else None
                except (ValueError, TypeError, AttributeError):
                    print(f'failed to convert {data.get('flow_id')} to integer')
                    data.pop("flow_id")  # Remove if invalid
        return super().to_internal_value(data)


class OHDiagramColumnsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    column = ColumnSerializer(partial=True)


class TableSerializer(serializers.ModelSerializer):
    columns = OHDiagramColumnsSerializer(many=True, required=False)

    class Meta:
        fields = "__all__"
        model = DatabaseTable

    def save(self, **kwargs):
        self.validated_data.pop("columns")
        print("validated", self.validated_data)
        return super().save(**kwargs)


class OHDiagramTableSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    table = TableSerializer(partial=True)


class RelSerializer(serializers.ModelSerializer):
    from_column = serializers.CharField()
    to_column = serializers.CharField()

    class Meta:
        fields = "__all__"
        model = Relationship
        read_only_fields = ["synced", "diagram"]

    # def to_internal_value(self, data):
    #     # Handle from_column field if it's a string
    #     from_column_value = data.get("from_column")
    #     if from_column_value and isinstance(from_column_value, str):
    #         try:
    #             # Try to convert to int first (for primary key)
    #             try:
    #                 # If it's an integer ID
    #                 column_id = int(from_column_value)
    #                 data["from_column"] = column_id
    #             except ValueError:
    #                 # If it's a UUID string
    #                 uuid_obj = UUID(from_column_value)
    #                 column = DatabaseColumn.objects.filter(flow_id=uuid_obj).first()
    #                 if column:
    #                     data["from_column"] = column.id
    #                 else:
    #                     print("the from column does not exist")
    #         except (ValueError, TypeError):
    #             # If conversion fails, let the normal validation handle it
    #             pass

    #     # Handle to_column field if it's a string
    #     to_column_value = data.get("to_column")
    #     if to_column_value and isinstance(to_column_value, str):
    #         try:
    #             # Try to convert to int first (for primary key)
    #             try:
    #                 # If it's an integer ID
    #                 column_id = int(to_column_value)
    #                 data["to_column"] = column_id
    #             except ValueError:
    #                 # If it's a UUID string
    #                 uuid_obj = UUID(to_column_value)
    #                 column = DatabaseColumn.objects.filter(flow_id=uuid_obj).first()
    #                 if column:
    #                     data["to_column"] = column.id
    #                 else:
    #                     print("the to column does not exist")
    #         except (ValueError, TypeError):
    #             # If conversion fails, let the normal validation handle it
    #             pass

    #     # Let the parent class handle the rest of the validation
        # return super().to_internal_value(data)

    # def validate_from_column(self, value):
    #     print('the value in the serilizer is', value)
    #     return value

    # def validate_to_column(self, value):
    #     return value.id


class OHRelationshipsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    relationship = RelSerializer()


class DeletedItemSerializer(serializers.Serializer):
    item_type = serializers.CharField()
    item_id = serializers.IntegerField()


class DiagramOverhaulSerializer(serializers.Serializer):
    table_list = OHDiagramTableSerializer(many=True)
    relationships = OHRelationshipsSerializer(many=True)
    diagram_id = serializers.UUIDField()
    deleted_items = serializers.ListField(child=DeletedItemSerializer())

    def __init__(self, *args, **kwargs):
        # Pass partial to child serializers
        partial = kwargs.pop("partial", False)
        super().__init__(*args, **kwargs)

        if partial:
            for field in self.fields.values():
                if isinstance(field, serializers.Serializer):
                    field.partial = True
