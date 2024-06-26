# -*- coding: utf-8 -*-
# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import json
import re

from collections.abc import Mapping
from pprint import pformat
from typing import List, Union, Optional

from eapix.environment import EAPI_DEFAULT_TRANSPORT
from eapix.types import Command, Error
from eapix.util import zpad, indent

class JsonResult(Mapping):
    def __init__(self, result: dict):
        self._data = result

    def __getitem__(self, name):
        return self._data[name]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return str(self._data)

    @property
    def pretty(self):
        return pformat(self._data)


class TextResult:
    def __init__(self, result: str):
        self._data = result.strip()

    def __str__(self):
        return self._data

    @property
    def pretty(self):
        return self._data


class ResponseElem:
    def __init__(self, command: Command,
                 result: Union[TextResult, JsonResult]):
        self.command = command
        self.result = result

    def to_dict(self):
        if isinstance(self.result, JsonResult):
            result = dict(self.result)
        else:
            result = str(self.result)

        return {
            "command": self.command,
            "result": result
        }

    def __str__(self):
        return str(self.result)


class Response:

    def __init__(self, target, elements: List[ResponseElem],
                 error: Optional[Error] = None):
        self._target = target
        self.elements = elements
        self.error = error

    # def __contains__(self, name):
    #     return name in self.__str__()

    # def __getitem__(self, item):
    #     return self.elements[item]

    # def __iter__(self):
    #     return iter(self.elements)

    # def __len__(self):
    #     return len(self.elements)

    @property
    def code(self):
        return self.error.code

    @property
    def message(self):
        return self.error.message

    @property
    def target(self):
        return self._target

    @property
    def json(self):
        return json.dumps(self.to_dict())

    @property
    def pretty(self):
        return str(self)

    def to_dict(self) -> dict:
        out = {}
        out["target"] = self._target.to_url()
        out["status"] = [self.code, self.message]

        out["responses"] = []
        for elem in self.elements:
            out["responses"].append(elem.to_dict())

        return out

    def __str__(self):
        text = "target: %s\n" % self.target
        text += "status: [%d, %s]\n\n" % (self.code, self.message or "OK")

        text += "responses:\n"

        for elem in self.elements:
            text += "- command: %s\n" % elem.command["cmd"]
            text += "  result: |\n"
            text += indent("    ", elem.result.pretty)
            text += "\n"
        return text

    @classmethod
    def from_rpc_response(cls, target, request, response):
        """Convert JSON response to a `Response` object"""
        
        encoding = request["params"]["format"]
        commands = request["params"]["cmds"]

        error = Error(code=0, message="")

        errored = response.get("error")
        results = []

        if errored:
            # dump the errored output
            results = errored.get("data", [])
            code = errored["code"]
            message = errored["message"]
            error = Error(code, message)
        else:
            results = response["result"]

        elements = []
        for cmd, res in zpad(commands, results, {}):
            if encoding == "text":
                res = TextResult(res.get("output", ""))
            else:
                res = JsonResult(res)
            elem = ResponseElem(cmd, res)
            elements.append(elem)

        return cls(target, elements, error)

class JsonRpcMessage:
    pass
