# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from typing import List, Optional, Tuple, Union
from dataclasses import asdict, dataclass, field

@dataclass
class BaseType:
    pass

@dataclass
class Error(BaseType):
    code: int
    message: str

@dataclass
class Command(BaseType):
    cmd: str
    input: str = ""

@dataclass
class Params(BaseType):
    cmds: List[Union[str, Command]]
    version: int = 1
    format: str = 'text'
    timestamps: Optional[bool] = None
    autoComplete: Optional[bool] = None
    expandAliases: Optional[bool] = None
    includeErrorDetail: Optional[bool] = None
    streaming: Optional[bool] = None

@dataclass
class Request(BaseType):
    params: Params
    id: str = ""
    jsonrpc: str = "2.0"
    method: str = "runCmds"
    streaming: bool = False # eAPI hack

Auth = Tuple[str, Optional[str]]

Certificate = Optional[Union[str, Tuple[str, str], Tuple[str, str, str]]]

Timeout = Union[None, float, Tuple[float, float, float, float]]

# RequestsOptions = TypedDict('RequestsOptions', {
#     'auth': Auth,
#     'timeout': Timeout,
#     'cert': Certificate,
#     'verify': bool
# }, total=False)
