# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import asyncio

import pytest

import eapix
import eapix.api
from eapix.messages import Response

# from tests.conftest import EAPI_TARGET

# pytestmark = pytest.mark.skipif(not EAPI_TARGET, reason="target not set")

def test_execute(server, commands, auth):
    target = str(server.url)
    eapix.execute(target, commands=commands, auth=auth)

def test_enable(server, commands, auth):
    target = str(server.url)
    eapix.execute(target, commands=commands, auth=auth, enable=True, secret="s3cr3t")

def test_execute_text(server, commands, auth):
    target = str(server.url)
    eapix.execute(target, commands, auth=auth)

def test_execute_jsonerr(server, auth):
    target = str(server.url)
    response = eapix.execute(
        target, 
        ["show hostname", "show bogus"],
       encoding="json", auth=auth)

    assert response.code > 0

def test_execute_err(server, auth):
    target = str(server.url)
    response = eapix.execute(target,
        commands=[
            "show hostname",
            "show bogus",
            "show running-config"
        ],
        auth=auth
    )
    assert response.code > 0

def test_configure(server, auth):
    target = str(server.url)
    eapix.configure(target, [
        "ip access-list standard DELETE_ME",
        "permit any"
    ], auth=auth)

    eapix.execute(target, ["show ip access-list DELETE_ME"], auth=auth)

    eapix.configure(target, [
        "no ip access-list DELETE_ME"
    ], auth=auth)


def test_watch(server, auth):
    target = str(server.url)
    def _cb(r, matched: bool):
        assert isinstance(r, eapix.messages.Response)
    
    eapix.watch(target, "show clock", callback=_cb, auth=auth, deadline=10)
    

@pytest.mark.asyncio
async def test_aexecute(server, commands, auth):
    channel = asyncio.Queue()
    target = str(server.url)
    await eapix.aexecute(channel, target, commands, auth=auth)

@pytest.mark.asyncio
async def test_awatch(server, auth):
    channel = asyncio.Queue()

    target = str(server.url)
    tasks = []

    for cmd in ["show clock"]:
        tasks.append(
            eapix.awatch(channel, target, cmd, auth=auth, deadline=2)
        )
    
    tasks.append(async_consumer(channel))
    
    await asyncio.gather(*tasks)

async def async_consumer(channel):
    while True:
        rsp = await channel.get()
        # break on stop signal
        if rsp is None:
            break
        
        assert isinstance(rsp[0], eapix.messages.Response)

    

