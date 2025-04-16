from rest_framework import serializers

from billing.utils import get_active_subscription
from .models import Diagram, DatabaseTable, DatabaseColumn, DiagramInvitation, DiagramInvitationStatusChoices, Relationship, DiagramMember
from account.models import UserAccount
from account.serializers import UserFieldsSerializer, UserSerializer


class DiagramSerializer(serializers.ModelSerializer):
    creator = UserFieldsSerializer()
    class Meta:
        model = Diagram
        fields = '__all__'
        
        
class DiagramInvitationIdSerializer(serializers.Serializer):
    invitation = serializers.IntegerField()
    def validate_invitation(self, value):
        try:
            diagram_invitation = DiagramInvitation.objects.get(id=value)
            
            if not diagram_invitation.status == DiagramInvitationStatusChoices.PENDING:
                raise serializers.ValidationError(f"Invitation is already {diagram_invitation.status}")
        except DiagramInvitation.DoesNotExist:
            raise serializers.ValidationError("Invitation not found")
        return diagram_invitation

class DiagramInvitationSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    diagram = DiagramSerializer()
    class Meta:
        model=DiagramInvitation
        fields ='__all__'
    
    def get_is_active(self, obj):
        return obj.is_active

class DiagramIdSerializer(serializers.Serializer):
    diagram = serializers.UUIDField()
    def validate_diagram(self, value):
        try:
            diagram = Diagram.objects.get(id=value)
            return diagram
        except Diagram.DoesNotExist:
            raise serializers.ValidationError("Diagram not found")

class GrantWriteRequestSerializer(serializers.Serializer):
    grant_to = serializers.UUIDField()
    diagram = serializers.UUIDField()


class DiagramMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    diagram=DiagramSerializer()

    class Meta:
        model = DiagramMember
        fields = "__all__"


class InviteUserSerializer(serializers.Serializer):
    email = serializers.CharField()

    # def validate_email(self, value):
    #     if not UserAccount.objects.filter(email=value).exists():
    #         raise serializers.ValidationError("User does not exist")
    #     return value


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = "__all__"


class RelationshipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = [
            "to_column",
            "from_column",
            "rel_type",
            "source_suffix",
            "target_suffix",
        ]


class RelationshipSerializer(serializers.ModelSerializer):
    source_node = serializers.SerializerMethodField()
    target_node = serializers.SerializerMethodField()

    class Meta:
        model = Relationship
        fields = "__all__"

    def get_source_node(self, obj):
        return obj.from_column.db_table.id

    def get_target_node(self, obj):
        return obj.to_column.db_table.id


class DatabaseTableSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseTable
        fields = ["name", "x_position", "y_position", "comment", "description"]


class DatabasePositionsSerializer(serializers.Serializer):
    x_position = serializers.FloatField()
    y_position = serializers.FloatField()


class DatabaseColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseColumn
        fields = "__all__"


class DatabaseColumnUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseColumn
        exclude = ["flow_id"]


class DatabaseTableSerializer(serializers.ModelSerializer):
    columns = serializers.SerializerMethodField()

    class Meta:
        model = DatabaseTable
        fields = "__all__"

    def get_columns(self, obj):
        columns = DatabaseColumn.objects.filter(db_table=obj).order_by('created_at')
        return DatabaseColumnSerializer(columns, many=True).data


class DiagramDetailSerializer(serializers.ModelSerializer):
    tables = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()
    relationships = serializers.SerializerMethodField()
    creator = UserSerializer()
    writer = UserSerializer()

    class Meta:
        model = Diagram
        fields = "__all__"

    def get_tables(self, obj):
        tables = DatabaseTable.objects.filter(diagram=obj)
        return DatabaseTableSerializer(tables, many=True).data

    def get_columns(self, obj):
        # columns = DatabaseColumn.objects.filter(db_table__diagram=obj)
        # return DatabaseColumnSerializer(columns, many=True).data
        return []

    def get_relationships(self, obj):
        relationships = Relationship.objects.filter(diagram=obj)
        return RelationshipSerializer(relationships, many=True).data


class DatabaseColumnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseColumn
        fields = ["db_table", "name", "datatype", "id", "flow_id"]
        read_only_fields = ["id"]


class DatabaseTableCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseTable
        fields = ["diagram", "name", "x_position", "y_position", "id"]
        read_only_fields = ["id"]


class DiagramCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = "__all__"
        read_only_fields = ["creator"]

    def create(self, validated_data):
        request = self.context.get("request")
        active_subscription = get_active_subscription(request.user)

        validated_data["creator"] = request.user
        if not active_subscription:
            validated_data['pay_per_diagram'] = True
            validated_data['has_paid'] = False
        else:
            validated_data['pay_per_diagram'] = False
            validated_data['has_paid'] = True
        return super().create(validated_data)
