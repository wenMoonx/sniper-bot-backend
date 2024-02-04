import dataclasses

from enum import Enum


class CustomCodeBase(Enum):
    """Custom status code base class"""

    @property
    def code(self):
        """
        Get status code
        """
        return self.value[0]

    @property
    def msg(self):
        """
        Get status code information
        """
        return self.value[1]


class CustomResponseCode(CustomCodeBase):
    """Custom response status code"""

    HTTP_200 = (200, 'Request successful')
    HTTP_201 = (201, 'New request successful')
    HTTP_202 = (202, 'The request has been accepted, but the processing has not been completed')
    HTTP_204 = (204, 'The request was successful, but no content was returned')
    HTTP_400 = (400, 'Request error')
    HTTP_401 = (401, 'Unauthorized')
    HTTP_403 = (403, 'Access Forbidden')
    HTTP_404 = (404, 'The requested resource does not exist')
    HTTP_410 = (410, 'The requested resource has been permanently deleted')
    HTTP_422 = (422, 'Illegal request parameters')
    HTTP_425 = (425, 'The request cannot be performed because the server cannot meet the request')
    HTTP_429 = (429, 'Too many requests, server limit')
    HTTP_500 = (500, 'Server internal error')
    HTTP_502 = (502, 'Gateway error')
    HTTP_503 = (503, 'The server is temporarily unable to process the request')
    HTTP_504 = (504, 'Gateway timeout')


class CustomErrorCode(CustomCodeBase):
    """New request successful"""

    CAPTCHA_ERROR = (40001, 'Verification code error')


@dataclasses.dataclass
class CustomResponse:
    """
    Provide open response status codes instead of enumerations, which may be useful if you want to customize the response information
    """

    code: int
    msg: str
