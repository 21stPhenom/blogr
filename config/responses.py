from rest_framework.response import Response
from rest_framework.serializers import ReturnDict, ReturnList
from rest_framework.status import is_success, is_client_error, is_server_error


def api_response(
    status_code: int,
    message: str = "an error occured",
    data: ReturnDict | ReturnList | dict = {},
):
    if is_success(status_code):
        status = "success"
    elif is_client_error(status_code):
        status = "client error"
    elif is_server_error(status_code):
        status = "server error"

    return Response(
        {"status": status, "message": message, "data": data}, status=status_code
    )
