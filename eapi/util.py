# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import os
import uuid
import dataclasses
from typing import Optional, Union, List
from eapi.types import Command, Params, Request

from eapi.environments import EAPI_DEFAULT_ENCODING

def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def indent(spaces, text: str):
    indented = []
    for line in text.splitlines():
        indented.append(spaces + line)

    return "\n".join(indented)


def prepare_request(commands: List[Union[str, Command]], 
        encoding: Optional[str] = None, streaming: bool = False) -> Request:
    #commands = prepare_cmd(commands)
    request_id = str(uuid.uuid4())

    if not encoding:
        encoding = EAPI_DEFAULT_ENCODING

    _commands = []
    for c in commands:
        if isinstance(c, str):
            c = Command(cmd=c)
        _commands.append(c)
    
    params = Params(
        version = 1,
        format = encoding,
        cmds = _commands
    )

    req: Request = Request(
        jsonrpc = "2.0",
        method = "runCmds",
        params = params,
        streaming = streaming,
        id = request_id
    )
    return req


def zpad(keys, values, default=None):
    """zips two lits and pads the second to match the first in length"""

    keys_len = len(keys)
    values_len = len(values)

    if (keys_len < values_len):
        raise ValueError("keys must be as long or longer than values")

    values += [default] * (keys_len - values_len)

    return zip(keys, values)

def pruned_dict(data):
    pruned = {}
    for key, val in data:
        if val is not None:
            pruned[key] = val

    return pruned

def asdict(data, prune=True):
    """Normal `asdict` but removes fields with None values"""

    factory = pruned_dict if prune else dict

    return dataclasses.asdict(data, dict_factory=factory)
    