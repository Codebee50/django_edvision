from rest_framework import generics
from common.responses import ErrorResponse
from common.utils import format_first_error

class ValidatingGenericApiView(generics.GenericAPIView):
    def on_validated(self, validated_data):
        pass
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return self.on_validated(serializer.validated_data)
        else:
            return ErrorResponse(message=format_first_error(serializer.errors))