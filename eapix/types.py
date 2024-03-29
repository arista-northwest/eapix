# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from eapix.environment import EAPI_DEFAULT_FORMAT

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

Timeout = Union[None, float, Tuple[float, float, float, float]]
