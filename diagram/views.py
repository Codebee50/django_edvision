import uuid
from rest_framework import generics

from account.utils import notify_user
from billing.models import PRICE_PER_DIAGRAM, Transaction, TransactionTypeChoices
from billing.utils import get_active_subscription, request_paystack
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from common.utils import format_first_error
from common.responses import ErrorResponse, SuccessResponse
from .models import (
    Diagram,
    DatabaseTable,
    DatabaseColumn,
    DiagramInvitation,
    DiagramInvitationStatusChoices,
    Relationship,
    DiagramMember,
)
from .datatypes import mappings
from account.services import send_invite_email
from django.conf import settings
from django.utils import timezone
from .agents import export_diagram_using_claude
# Create your views here.

class ExportDiagramUsingAi(generics.GenericAPIView):
    serializer_class = ExportDiagramUsingAiSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))
        
        diagram = serializer.validated_data.get("diagram")
        format_name = serializer.validated_data.get("format_name")
        
        response = export_diagram_using_claude(diagram_id=str(diagram.id), format_name=format_name)
        
        return SuccessResponse(message="Diagram exported successfully")
        


class RejectInvitationView(generics.GenericAPIView):
    serializer_class = DiagramInvitationIdSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))

        invitation = serializer.validated_data.get("invitation")
        if not invitation.email == request.user.email:
            return ErrorResponse(
                message="You do not have the permission to perform this action"
            )

        invitation.is_accepted = False
        invitation.status = DiagramInvitationStatusChoices.REJECTED
        invitation.save()
        return SuccessResponse(
            message="Invitation rejected successfully",
            data=DiagramInvitationSerializer(invitation).data,
        )


class AcceptInvitationView(generics.GenericAPIView):
    serializer_class = DiagramInvitationIdSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))

        invitation = serializer.validated_data.get("invitation")
        if not invitation.email == request.user.email:
            return ErrorResponse(
                message="You do not have the permission to perform this action"
            )

        invitation.is_accepted = True
        invitation.status = DiagramInvitationStatusChoices.ACCEPTED
        invitation.save()

        DiagramMember.objects.create(user=request.user, diagram=invitation.diagram)
        return SuccessResponse(
            message="Invitation accepted successfully",
            data=DiagramInvitationSerializer(invitation).data,
        )


class ListMyInvitationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiagramInvitationSerializer

    def get_queryset(self):
        return DiagramInvitation.objects.filter(email=self.request.user.email).order_by(
            "-created_at"
        )


class GetInvitationView(generics.RetrieveAPIView):
    serializer_class = DiagramInvitationSerializer
    queryset = DiagramInvitation.objects.all()
    lookup_field = "id"


class InitializeDiagramPaymentView(generics.GenericAPIView):
    serializer_class = DiagramIdSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(message=format_first_error(serializer.errors))

        diagram = serializer.validated_data.get("diagram")
        if diagram.has_paid:
            return ErrorResponse(message="You do not need to pay for this diagram")

        price_per_diagram = PRICE_PER_DIAGRAM

        reference_uuid = uuid.uuid4()

        request_body = {
            "email": request.user.email,
            "amount": int(price_per_diagram) * 100,
            "reference": str(reference_uuid),
            "callback_url": f"{settings.FE_URL}/diagram/{diagram.id}",
        }
        response = request_paystack(
            "/transaction/initialize", method="post", data=request_body
        )

        if response.error:
            return ErrorResponse(message=response.message)

        Transaction.objects.create(
            user=request.user,
            trx_reference=reference_uuid,
            transaction_type=TransactionTypeChoices.DIAGRAM_CHARGE,
            payload=str(diagram.id),
        )
        return SuccessResponse(
            message="",
            data={
                "payment_url": response.body.get("data", {}).get(
                    "authorization_url", ""
                )
            },
        )
        # return SuccessResponse(
        #     message="", data={"payment_url": transaction["data"]["authorization_url"]}
        # )


class GrantWriteRequestView(generics.GenericAPIView):
    serializer_class = GrantWriteRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            grant_to_id = serializer.validated_data.get("grant_to")
            diagram_id = serializer.validated_data.get("diagram")

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
                return SuccessResponse(
                    message="Access granted successfully",
                    data=UserSerializer(grant_to).data,
                )

            return ErrorResponse(
                message="You cannot grant access on this diagram currently"
            )

        else:
            return ErrorResponse(message=format_first_error(serializer.errors))


class GetDiagramMembers(generics.GenericAPIView):
    serializer_class = DiagramMemberSerializer

    def get(self, request, *args, **kwargs):
        try:
            diagram = Diagram.objects.get(id=kwargs.get("diagram_id"))
        except Diagram.DoesNotExist:
            return ErrorResponse(message="Diagram does not exist")

        members = DiagramMember.objects.filter(diagram=diagram)
        invitations = DiagramInvitation.objects.filter(diagram=diagram)

        return SuccessResponse(
            message="members",
            data={
                "members": self.get_serializer(members, many=True).data,
                "invitations": DiagramInvitationSerializer(invitations, many=True).data,
            },
        )


class InviteUserView(generics.GenericAPIView):
    serializer_class = InviteUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            try:
                diagram = Diagram.objects.get(id=kwargs.get("diagram_id"))
            except Diagram.DoesNotExist:
                return ErrorResponse(message="Diagram not found")

            if request.user != diagram.creator:
                return ErrorResponse(
                    message="Oops, only creators are allowed to invite members"
                )

            if (
                DiagramMember.objects.filter(
                    diagram=diagram, user__email=email
                ).exists()
                or email == diagram.creator.email
            ):
                return ErrorResponse(message="User is already a member")

            active_invitations = DiagramInvitation.objects.filter(
                expiry_date__gt=timezone.now(),  # expiry date is in the future
                status=DiagramInvitationStatusChoices.PENDING,  # not yet accepted or rejected
                diagram=diagram,
                email=email,
            )

            if active_invitations.exists():
                return ErrorResponse(
                    message="You still have a pending invitation for this user on this diagram"
                )

            # diagram_member = DiagramMember.objects.create(user=user, diagram=diagram)
            diagram_invitation = DiagramInvitation.objects.create(
                email=email, diagram=diagram
            )
            send_invite_email(email, diagram, diagram_invitation)

            user = UserAccount.objects.filter(email=email).first()
            if user:
                notify_user(
                    user,
                    "New collaboration invitation",
                    f"You have been invited by {diagram.creator.first_name} to collaborate on {diagram.name} tap `Invitations` on your dashboard to accept or reject this invitation",
                )

            return SuccessResponse(
                message=f"An invite has been sent to {email}",
            )
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))


class DeleteTableView(generics.DestroyAPIView):
    queryset = DatabaseTable.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class DeleteDiagramView(generics.DestroyAPIView):
    queryset = Diagram.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class GetDatatypeList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        datatype = kwargs.get("type")

        type_list = mappings.get(datatype, [])
        return SuccessResponse(message=f"Datatypes for {datatype}", data=type_list)


class UpdateRelationShipView(generics.UpdateAPIView):
    queryset = Relationship.objects.all()
    lookup_field = "id"
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticated]


class SyncDatabaseColumn(generics.UpdateAPIView):
    serializer_class = DatabaseColumnSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatabaseColumn.objects.all()
    lookup_field = "id"


class SyncDatabaseTable(generics.UpdateAPIView):
    serializer_class = DatabaseTableSyncSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatabaseTable.objects.all()
    lookup_field = "id"


class UpdateTablePosition(generics.GenericAPIView):
    serializer_class = DatabasePositionsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        table_id = kwargs.get("id")
        x_position = request.data.get("x_position")
        y_position = request.data.get("y_position")

        try:
            table = DatabaseTable.objects.get(id=table_id)
            table.x_position = x_position
            table.y_position = y_position
            table.save()
        except DatabaseTable.DoesNotExist:
            return ErrorResponse(message="Table not found")
        return SuccessResponse(message="Table position updated successfully")


class ColumnDeleteView(generics.DestroyAPIView):
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    queryset = DatabaseColumn.objects.all()


class RelationshipDeleteView(generics.DestroyAPIView):
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    queryset = Relationship.objects.all()


class RelationshipCreateView(generics.CreateAPIView):
    serializer_class = RelationshipCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            from_column = serializer.validated_data.get("from_column")
            response = serializer.save(diagram=from_column.db_table.diagram)
            return SuccessResponse(
                message="Relationship created successfully",
                data=RelationshipSerializer(response).data,
            )
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
    lookup_field = "id"

    def get_queryset(self):
        return Diagram.objects.all()

    # def get_queryset(self):
    #     return Diagram.objects.filter(creator=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class InvitedDiagramsListView(generics.ListAPIView):
    serializer_class = DiagramMemberSerializer
    permission_classes =[IsAuthenticated]
    
    def get_queryset(self):
        return DiagramMember.objects.filter(user=self.request.user)

class UserDiagramsListView(generics.ListAPIView):
    serializer_class = DiagramSerializer
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
