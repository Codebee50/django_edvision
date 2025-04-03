from rest_framework import serializers

from diagram.models import DatabaseColumn, DatabaseTable, Relationship
from ..serializers import DatabaseTableSerializer, RelationshipSerializer


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = DatabaseColumn
        read_only_fields = ["synced"]


class OHDiagramColumnsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    column = ColumnSerializer()


class TableSerializer(serializers.ModelSerializer):
    columns = OHDiagramColumnsSerializer(many=True)

    class Meta:
        fields = "__all__"
        model = DatabaseTable
        read_only_fields = ["diagram", "synced", "flow_id"]


class OHDiagramTableSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    table = TableSerializer()


class OHRelationshipsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Relationship
        read_only_fields = ["synced", "diagram"]


class DiagramOverhaulSerializer(serializers.Serializer):
    table_list = OHDiagramTableSerializer(many=True)
    relationships = OHRelationshipsSerializer(many=True)
