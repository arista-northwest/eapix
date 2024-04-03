# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import json
import warnings

from typing import Dict, Optional, Union, Type

import httpx

import eapix.environment
from eapix.types import EapiOptions

from eapix.util import prepare_request

from eapix.exceptions import (
    EapiAuthenticationFailure,
    EapiError,
    EapiPathNotFoundError)

from eapix.types import (
    Auth,
    Certificate,
    CommandList,
    Target
)

from eapix.response import Response

class BaseClient:

    def __init__(self,
                 klass: Type[Union[httpx.Client, httpx.AsyncClient]],
                 auth: Optional[Auth] = None,
                 cert: Optional[Certificate] = None,
                 verify: Optional[bool] = None,
                 **kwargs):

        if verify is None:
            verify = eapix.environment.SSL_VERIFY

        # use a httpx client to manage state
        self._client = klass(
            auth=auth,
            cert=cert,
            headers={"Content-Type": "application/json"},
            verify=verify,
            **kwargs
        )

        # store parameters for future requests
        self._eapi_sessions: Dict[str, dict] = {}

    def _handle_call_response(self, response):

        if response.status_code == 401:
            raise EapiAuthenticationFailure(response.reason_phrase)

        if response.status_code == 404:
            raise EapiPathNotFoundError(response.reason_phrase)

        response.raise_for_status()

    def _handle_login_response(self, target, auth, resp):
        if resp.status_code == 404:
            # Older versions do not have the login endpoint.
            # fall back to basic auth if /login is not found
            pass
        elif resp.status_code != 200:
            raise EapiError(f"{resp.status_code} {resp.reason_phrase}")

        if "Session" not in resp.cookies:
            warnings.warn(("Got a good response, but no 'Session' found in "
                           "cookies. Using fallback auth."))
        elif resp.cookies["Session"] == "None":
            # this is weird... investigate further
            warnings.warn("Got cookie Session='None' in response?! "
                          "Using fallback auth.")

        options = {}
        if not self.logged_in(target):
            # store auth if login fails (without throwing an exception)
            options["auth"] = auth

        self._eapi_sessions[target.fqdn] = options

    def logged_in(self, target: str) -> bool:
        """determines if session cookie is set"""
        target_ = Target.from_url(target)

        cookie = self._client.cookies.get("Session", domain=target_.fqdn)

        return True if cookie else False


class Client(BaseClient):
    def __init__(self,
                 auth: Optional[Auth] = None,
                 cert: Optional[Certificate] = None,
                 verify: Optional[bool] = None,
                 **kwargs):

        super().__init__(
            klass=httpx.Client, # why does this irritate pyright
            auth=auth,
            cert=cert,
            verify=verify,
            **kwargs
        )

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _call(self, url, data: dict, **options) -> httpx.Response:
        """calls the request to EAPI"""

        response = None

        if "timeout" not in options:
            options["timeout"] = eapix.environment.EAPI_DEFAULT_TIMEOUT

        try:
            response = self._client.post(url, content=json.dumps(data), **options)
        except httpx.HTTPError as exc:
            raise EapiError(str(exc))

        self._handle_call_response(response)

        return response

    def close(self):
        """shutdown the underlying httpx session"""
        self._client.close()

    def logout(self, target: Union[str, Target]) -> None:
        """Log out of an eAPI session

        :param target: eAPI target (host, port)
        :param type: Target

        """

        _target: Target = Target.from_url(target)

        if _target.fqdn in self._eapi_sessions:
            del self._eapi_sessions[_target.fqdn]

        if self.logged_in(target):
            self._call(f"{_target}/logout", data={})

    def login(self, target: str, auth: Optional[Auth] = None) -> None:
        """Login to an eAPI session

        :param target: eAPI target (host, port)
        :param type: Target
        :param auth: username, password tuple
        :param type: Auth
        """
        _target: Target = Target.from_url(target)

        if self.logged_in(target):
            return

        username, password = auth or self._client.auth
        payload = {"username": username, "password": password}

        resp = self._call(f"{_target}/login", data=payload)

        self._handle_login_response(_target, auth, resp)

    def call(self, target: str, commands: CommandList,
             options: EapiOptions = EapiOptions(), **kwargs):
        """call commands to an eAPI target

        :param target: eAPI target (host, port)
        :param type: str
        :param commands: List of `Command` objects
        :param type: list
        :param options: eapi options
        :param type: EapiOptions
        :param **kwargs: other pass through `httpx` options
        :param type: dict

        """

        _target: Target = Target.from_url(target)

        # get session defaults (set at login)
        httpx_args = self._eapi_sessions.get(_target.fqdn) or {}
        httpx_args.update(kwargs)

        request = prepare_request(commands, options)

        response = self._call(f"{_target}/command-api",
                              data=request, **httpx_args)

        return Response.from_rpc_response(_target, request, response.json())


class AsyncClient(BaseClient):
    def __init__(self,
                 auth: Optional[Auth] = None,
                 cert: Optional[Certificate] = None,
                 verify: Optional[bool] = None,
                 **kwargs):

        super().__init__(
            klass=httpx.AsyncClient,
            auth=auth,
            cert=cert,
            verify=verify,
            **kwargs
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def _call(self, url, data: dict, **options) -> httpx.Response:
        """Post to eAPI endpoint"""

        response = None

        if "timeout" not in options:
            options["timeout"] = eapix.environment.EAPI_DEFAULT_TIMEOUT

        try:
            response = await self._client.post(url, content=json.dumps(data),
                                                **options)
        except httpx.HTTPError as exc:
            raise EapiError(str(exc))

        self._handle_call_response(response)

        return response

    async def close(self) -> None:
        await self._client.aclose()

    async def login(self, target: str, auth: Optional[Auth] = None) -> None:
        """Login to an eAPI session

        :param target: eAPI target (host, port)
        :param type: str
        :param auth: username, password tuple
        :param type: Auth
        """
        target_: Target = Target.from_url(target)

        if self.logged_in(target):
            return

        username, password = auth or self._client.auth
        payload = {"username": username, "password": password}

        resp = await self._call(target_.url + "/login", data=payload)

        self._handle_login_response(target_, auth, resp)

    async def logout(self, target: str) -> None:
        """Log out of an eAPI session

        :param target: eAPI target (host, port)
        :param type: str

        """

        target_: Target = Target.from_url(target)

        if target_.fqdn in self._eapi_sessions:
            del self._eapi_sessions[target_.fqdn]

        if self.logged_in(target):
            await self._call(target_.url + "/logout", data={})

    async def call(self, target: str, commands: CommandList,
                   options: EapiOptions = EapiOptions(), **kwargs):
        """call commands to an eAPI target

        :param target: eAPI target (host, port)
        :param type: Target
        :param commands: List of `Command` objects
        :param type: list
        :param options: eapi options
        :param type: EapiOptions
        :param **kwargs: other pass through `httpx` options
        :param type: dict

        """

        _target: Target = Target.from_url(target)
        
        # get session defaults (set at login)
        httpx_args = self._eapi_sessions.get(_target.fqdn) or {}
        httpx_args.update(kwargs)

        request = prepare_request(commands, options)

        response = await self._call(f"{_target}/command-api",
                                    data=request, **httpx_args)

        return Response.from_rpc_response(_target, request, response.json())
