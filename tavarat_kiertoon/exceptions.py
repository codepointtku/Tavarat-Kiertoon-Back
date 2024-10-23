import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(exception: APIException, context: dict) -> Response:
    response = exception_handler(exception, context)

    if isinstance(exception, ValidationError):
        request_data = {"request_data": context["request"].data}
        """ path = context["request"].path
        status_code = response.status_code
        request = context["request"]
        logger.warning(
            f"Bad Request: {path} status_code: {status_code} http_request: {request} data:{request_data}",
            extra={
                "status_code": response.status_code,
                "http_request": context["request"],
                "json_fields": request_data,
            },
        ) """
        logger.warning(
            "Bad Request: %s",
            context["request"].path,
            extra={
                "status_code": response.status_code,
                "method": context["request"].method,
                "response_data": response.data,
            },
        )

    # setattr(response, "_has_been_logged", True)
    return response
