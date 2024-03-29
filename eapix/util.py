# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import os
import uuid

from dataclasses import asdict
from typing import Optional, Union
#from _typeshed import DataclassInstance
from eapix.types import Command, CommandList, EapiOptions

def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def indent(spaces: str, text: str) -> str:
    indented = []
    for line in text.splitlines():
        indented.append(spaces + line)

    return "\n".join(indented)

def prepare_commands(commands: list[str]|CommandList) -> list[dict[str, object]]:
    prepared = []

    for cmd in commands:
        if isinstance(cmd, Command):
            cmd = asdict_pruned(cmd)
        elif isinstance(cmd, str):
            cmd = {"cmd": cmd}
        else:
            raise ValueError(f"invalid type for command: {cmd}")

        prepared.append(cmd)

    return prepared

def prepare_request(
    commands: CommandList,
    options: EapiOptions = EapiOptions(),
    request_id: Optional[str] = None) -> dict[str, object]:

    if not request_id:
        request_id = str(uuid.uuid4())

    req: dict[str, object] = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "id": request_id
    }

    params: dict[str, object] = {
        "cmds": prepare_commands(commands),
        "version": options.version,
        "format": options.encoding,
    }

    if options.streaming:
        params["streaming"] = options.streaming
        # eAPI hack, old versions expected it here
        req["streaming"] = options.streaming
    
    if options.timestamps == True:
        params["timestamps"] = options.timestamps

    if options.auto_complete == True:
        params["autoComplete"] = options.auto_complete

    if options.expand_aliases == True:
        params["expand_aliases"] = options.expand_aliases

    if options.include_error_detail == True:
        params["include_error_detail"] = options.include_error_detail

    req["params"] = params
        
    return req


def zpad(keys: list[object], values: list[object], default: object = None) -> list[tuple[object, object]]:
    """zips two lists and pads the second to match the first in length"""

    keys_len = len(keys)
    values_len = len(values)

    if (keys_len < values_len):
        raise ValueError("keys must be as long or longer than values")

    values += [default] * (keys_len - values_len)

    return list(zip(keys, values))

def pruned_dict(data: list[tuple[str, object]]) -> dict[str, object]:
    pruned = {}
    for key, val in data:
        if val is not None:
            pruned[key] = val

    return pruned

def asdict_pruned(data: object) -> dict[str, object]:
    """Just like `asdict` but removes fields with `None` values"""

    return asdict(data, dict_factory=pruned_dict)
    