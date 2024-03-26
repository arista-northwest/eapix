
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import pytest

from eapix.util import indent, zpad

from pprint import pprint

@pytest.mark.parametrize("text", [
    "a\nb\nc\nd\nf"
])
def test_indent(text):
    indent(" " * 10, text)


def test_prepare_request(request_):
    assert request_.get("jsonrpc") == "2.0"
    assert request_.get("method") == "runCmds"
    assert isinstance(request_.get("id"), str)
    assert request_["params"]["version"] == 1
    assert request_["params"]["format"] in ("json", "text")


def test_zpad():
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    z = ['z', 'y', 'x', 'w']

    r = list(zpad(a[:], z[:], None))
    assert len(r) == len(a)

    with pytest.raises(ValueError):
        zpad(z[:], a[:], None)


