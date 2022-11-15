
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from dataclasses import dataclass
from typing import Tuple, Optional
import pytest

import eapi.sessions
import eapi.environments
from eapi.util import indent, prepare_request, zpad, asdict


@pytest.mark.parametrize("text", [
    "a\nb\nc\nd\nf"
])
def test_indent(text):
    indent(" " * 10, text)


# @pytest.mark.parametrize("cmd", [
#     "show some stuff",
#     {"cmd": "show secret stuff", "input": "s3c3rt"},
#     ["show some stuff", {"cmd": "show secret stuff", "input": "s3c3rt"}]
# ])
# def test_prepare_cmd(cmd):
#     commands = prepare_cmd(cmd)
#     for cmd in commands:
#         assert "cmd" in cmd
#         assert "input" in cmd
#         assert len(cmd["cmd"]) > 0


def test_prepare_request(request_):

    assert request_.jsonrpc == "2.0"
    assert request_.method == "runCmds"
    assert isinstance(request_.id, str)
    assert request_.params.version == 1
    assert request_.params.format in ("json", "text")
    for command in request_.params.cmds:
        # assert "cmd" in command
        # assert "input" in command
        assert len(command.cmd) > 0

    p = prepare_request(["show stuff"])
    assert p.params.format == eapi.environments.EAPI_DEFAULT_ENCODING


def test_zpad():
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    z = ['z', 'y', 'x', 'w']

    r = list(zpad(a[:], z[:], None))
    assert len(r) == len(a)

    with pytest.raises(ValueError):
        zpad(z[:], a[:], None)

# @dataclass
# class TestData:
#     a: str
#     b: str
#     c: Optional[str] = None

# def test_asdict():
#     d = TestData("a", "b", "c")
#     print(asdict(d))

#     d = TestData("a", "b", None)

#     print(asdict(d))

