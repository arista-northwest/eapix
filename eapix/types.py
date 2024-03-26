# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from eapix.environments import EAPI_DEFAULT_FORMAT

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
class EapiOptions(BaseType):
    version: int = 1
    format: str = EAPI_DEFAULT_FORMAT
    timestamps: Optional[bool] = None
    auto_complete: Optional[bool] = None
    expand_aliases: Optional[bool] = None
    include_error_detail: Optional[bool] = None
    streaming: Optional[bool] = None

CommandList = List[Union[str, Command]]

Auth = Tuple[str, Optional[str]]

Certificate = Optional[Union[str, Tuple[str, str], Tuple[str, str, str]]]

Timeout = Union[None, float, Tuple[float, float, float, float]]
