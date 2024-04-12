# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import pytest
from pprint import pprint
from eapix.response import Response, ResponseElem, TextResult, JsonResult

def test_text_result(text_response):
    r = TextResult(text_response[-1]["result"][1]["output"])
    str(r)
    r.pretty

def test_json_result(json_response):
    
    r = JsonResult(json_response[-1]["result"][1])
    str(r)
    r.pretty
    len(r)
    for k,v in r.items():
        pass

def test_response_elem(json_response, text_response):
    _, request, response = json_response

    c = request["params"]["cmds"][-1]
    r = response["result"][1]
    t = text_response[-1]["result"][1]["output"]
    e = ResponseElem(c, JsonResult(r))
    str(e)
    e.to_dict()

    e = ResponseElem(c, TextResult(t))
    str(e)
    e.to_dict()

def test_text_response(text_response):
    resp = Response.from_rpc_response(*text_response)
    assert resp.code == 0
    assert "FQDN" in resp.pretty
    assert "target" in resp.pretty
    
    resp.to_dict()
    for elem in resp.elements:
        assert isinstance(elem, ResponseElem)

def test_json_response(json_response):
    resp = Response.from_rpc_response(*json_response)
    assert resp.code == 0
    assert "fqdn" in resp.pretty
    resp.to_dict()
    for elem in resp.elements:
        assert isinstance(elem, ResponseElem)

def test_errored_response(errored_response):
    resp = Response.from_rpc_response(*errored_response)
    assert resp.code == 1002
    assert "invalid" in resp.pretty

    resp.to_dict()
    for elem in iter(resp.elements):
        assert isinstance(elem, ResponseElem)

def test_errored_text_response(errored_text_response):
    resp = Response.from_rpc_response(*errored_text_response)
    assert resp.code == 1002
    assert "invalid" in resp.pretty
    
    resp.to_dict()
    for elem in resp.elements:
        assert isinstance(elem, ResponseElem)

