#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict

from app.lib.response_code import CustomResponse, CustomResponseCode
from app.core.conf import settings

_ExcludeData = set[int | str] | dict[int | str, Any]

__all__ = ['ResponseModel', 'response_base']


class StatusModel(BaseModel):
    res: CustomResponseCode | CustomResponse = None,
    error_detail: str = ""

class ResponseModel(BaseModel):
    """
    E.g. ::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})

        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})

        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """  # noqa: E501

    model_config = ConfigDict(json_encoders={datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)})

    data: Any | None = None
    status: StatusModel


class ResponseBase:
    """
    Unified return method

    .. tip::

        The return methods in this class will be pre-parsed by the custom encoder, and then processed and returned again by the encoder inside fastapi. There may be a performance penalty, depending on personal preference;；
        This return model does not generate openapi schema documentation

    E.g. ::

        @router.get('/test')
        def test():
            return await response_base.success(data={'test': 'test'})
    """  # noqa: E501

    @staticmethod
    async def __response(
        *,
        res: CustomResponseCode | CustomResponse = None,
        data: Any | None = None,
        error_detail: str | None = None,
        exclude: _ExcludeData | None = None,
        **kwargs,
    ) -> dict:
        """

        :param code: 
        :param msg: 
        :param data: 
        :param exclude: 
        :param kwargs: jsonable_encoder 
        :return:
        """
        if data is not None:
            # TODO: custom_encoder: https://github.com/tiangolo/fastapi/discussions/10252
            custom_encoder = {datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)}
            kwargs.update({'custom_encoder': custom_encoder})
            data = jsonable_encoder(data, exclude=exclude, **kwargs)
        return {
            'status': { 
                'code' : res.code, 
                'message': res.msg, 
                'error_detail': error_detail
            },
            'data': data
        }

    async def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
        error_detail: str | None = None,
        exclude: _ExcludeData | None = None,
        **kwargs,
    ) -> dict:
        return await self.__response(res=res, data=data, exclude=exclude, error_detail=error_detail, **kwargs)

    async def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
        error_detail: str | None = None,
        exclude: _ExcludeData | None = None,
        **kwargs,
    ) -> dict:
        return await self.__response(res=res, data=data, exclude=exclude, error_detail=error_detail, **kwargs)


response_base = ResponseBase()
