from rest_framework.response import Response

class SuccessResponse(Response):
    def __init__(self, data=None, message=None, status=200, **kwargs):
        resp = {"status": "success", "data":data, "message":message, "success":True}
        # resp.update(data)
        super().__init__(data=resp, status=status, **kwargs)


class ErrorResponse(Response):
    def __init__(self, data=None, message=None, status=400, **kwargs):
        resp = {"status": "failure", "data":data, "message":message, "success":False}
        # resp.update(data)
        super().__init__(data=resp, status=status, **kwargs)