import asyncio
import json

from sys import version

import httpx
import pytest

from eapix.util import prepare_request

import eapix
import eapix.exceptions
import eapix.client
from eapix.response import Response
from eapix.client import Client, AsyncClient
from eapix.types import Target

def test_login(session, server, auth):
    target = str(server.url)
    session.login(target, auth=auth)
    assert session.logged_in(target)


def test_login_err(server):
    target = Target.from_url(str(server.url))
    with Client() as sess:
        with pytest.raises(eapix.exceptions.EapiAuthenticationFailure):
            sess.login(target, ("b4d", "p4ss"))

        with pytest.raises(eapix.exceptions.EapiAuthenticationFailure):
            sess._call(Target.from_url(target).to_url() + "/login", data={})


def test_call(session, server, auth):
    target = str(server.url)
    session.call(target, ["show hostname"])


def test_http_error(session, server):
    target = str(server.url)
    t = Target.from_url(target)
    with pytest.raises(eapix.exceptions.EapiPathNotFoundError):
        session._call(t.to_url() + "/badpath", {})


def test_jsonrpc_error(session, server):
    target = str(server.url)
    tgt = Target.from_url(target)
    req = prepare_request(["show hostname"])
    req["method"] = "bogus"
    resp = session._call(tgt.to_url() + "/command-api", req)

    rresp = Response.from_rpc_response(tgt, req, resp.json())

    assert rresp.code < 0

def test_context(server, auth):
    target = str(server.url)
    with Client() as sess:
        sess.login(target, auth=auth)
        sess.call(target, ["show hostname"])


def test_ssl_verify(starget, cert):
    sess = Client(cert=cert)
    with pytest.raises(eapix.exceptions.EapiError):
        sess.call(starget, ["show hostname"])

def test_logout(server, auth):
    target = str(server.url)
    with Client() as sess:
        sess.login(target, auth=auth)
        sess.logout(target)


def test_logout_noexist(session):
    session.logout("bogus")


def test_unauth(session, server):
    target = str(server.url)
    with pytest.raises(eapix.exceptions.EapiAuthenticationFailure):
        session.login(target, auth=("l33t", "h3x0r"))


# def test_call_noauth(session, server, auth):
#     target = str(server.url)
#     sess = Client()
#     with pytest.raises(eapi.exceptions.EapiAuthenticationFailure):
#         sess.call(target, ["show hostname"], auth=auth)


@pytest.mark.asyncio
async def test_async(server, auth):
    target = Target.from_url(str(server.url))
    targets = [target] * 4
    commands = [
        "show version",
        "show hostname",
        "show clock",
    ] * 3

    async with AsyncClient(auth=auth) as sess:
        tasks = []
        for t in targets:
            for c in commands:
                tasks.append(sess.call(t, [c]))

        responses = await asyncio.gather(*tasks)

        assert len(responses) == 36
