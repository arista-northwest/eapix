# -*- coding: utf-8 -*-
# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import re

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
from eapix.environment import EAPI_DEFAULT_FORMAT, EAPI_DEFAULT_TRANSPORT

Auth = Tuple[str, str]

Certificate = Union[str, Tuple[str, str], Tuple[str, str, str]]

@dataclass
class Command:
    cmd: str
    input: Optional[str] = None

CommandList = List[Union[str, tuple[str, str], Command]]

@dataclass
class EapiOptions:
    version: int = 1
    encoding: str = EAPI_DEFAULT_FORMAT
    timestamps: Optional[bool] = None
    auto_complete: Optional[bool] = None
    expand_aliases: Optional[bool] = None
    include_error_detail: Optional[bool] = None
    streaming: Optional[bool] = None

@dataclass
class Error:
    code: int
    message: str

@dataclass
class Target:
    transport: str
    hostname: str
    port: Optional[int]

    def __post_init__(self):
        if self.port is not None and (self.port < 1 or self.port > 65535):
            raise ValueError(f"invalid port '{self.port}'. must be > 1 and < 65535")
        
        if self.transport not in ("http", "https"):
            raise ValueError(f"invalid transport '{self.transport}'. must be http or https")

    def __str__(self):
        return self.to_url()

    def to_url(self):
        url = f"{self.transport}://{self.hostname}"
        
        if self.port:
            url += f":{self.port}"

        return url

    @property
    def fqdn(self):
        fqdn = self.hostname
        if "." not in fqdn:
            fqdn += ".local"
        return fqdn
    
    @classmethod
    def from_url(cls, target: Union[str, "Target"]) -> "Target":
        _target_re = re.compile(r"^(?:(?P<transport>\w+)\:\/\/)?"
                        r"(?P<hostname>[\w+\-\.]+)(?:\:"
                        r"(?P<port>\d{,5}))?/*?$")
        
        if isinstance(target, Target):
            return target

        match = _target_re.search(target)
        if not match:
            raise ValueError("Invalid target: %s" % target)

        transport = match.group("transport") or EAPI_DEFAULT_TRANSPORT
        hostname = match.group("hostname")

        
        port = match.group("port")
        if port is not None:
            port = int(port)

        return cls(transport, hostname, port)

Timeout = Union[None, float, Tuple[float, float, float, float]]
