# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import asyncio
import math
import re
import time

from typing import Callable, Iterator, List, Optional, Union

from eapix.version import __version__
from eapix.types import Auth, Certificate, Command, CommandList, EapiOptions
from eapix.messages import Response
from eapix.session import Session, AsyncSession
from eapix.environment import EAPI_DEFAULT_FORMAT

NEVER_RE: str = r'(?!x)x'
EAPI_WATCH_INTERVAL: int = 2
EAPI_WATCH_DEADLINE: float = math.inf

def version():
    """get installed version
    
    :return: str"""
    return __version__

def execute(target: str,
            commands: CommandList,
            auth: Optional[Auth] = None,
            encoding: str = EAPI_DEFAULT_FORMAT,
            enable: bool = False,
            secret: str = "",
            cert: Optional[Certificate] = None,
            verify: bool = False,
            auto_complete: bool = False,
            expand_aliases: bool = False,
            include_error_detail: bool = False,
            timestamps: bool = False,
            streaming: bool = False
        ) -> Response:
    """Send an eAPI request

    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param auth:
    :param type: tuple
    :param encoding: json or text (default: json)
    :param type: str
    :param enable:
    :param type: bool
    :param secret:
    :param type: str
    :param cert:
    :param verify:
    :param auto_complete:
    :param type: bool
    :param expand_aliases:
    :param type: bool
    :param include_error_detail:
    :param type: bool
    :param timestamps:
    :param type: bool
    :param streaming:
    :param type: bool

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    if enable:
        commands.insert(0, Command(cmd="enable", input=secret))

    with Session(auth=auth, cert=cert, verify=verify) as sess:
        return sess.call(target, commands, EapiOptions(
            encoding=encoding,
            timestamps=timestamps,
            auto_complete=auto_complete,
            expand_aliases=expand_aliases,
            include_error_detail=include_error_detail,
            streaming=streaming
        ))

def configure(target: str, commands: CommandList, *args, **kwargs) -> Response:
    """Wrap commands in a 'configure'/'end' block

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, Command("configure"))
    commands.append(Command("end"))
    return execute(target, commands, *args, **kwargs)


def watch(target: str,
          command: Union[str, Command],
          callback: Callable = None,
          interval: Optional[int] = EAPI_WATCH_INTERVAL,
          deadline: Optional[float] = EAPI_WATCH_DEADLINE,
          exclude: bool = False,
          condition: Optional[str] = NEVER_RE,
          *args, **kwargs) -> Optional[Iterator[Response]]:
    """Watch a command until deadline or condition matches

    :param target: eAPI target
    :param type: Target
    :param commmand: A single command to send
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param callback: Callback function for responses
    :param type: Callable
    :param interval: time between repeating command
    :param type: int
    :param deadline: End loop after specified time
    :param type: float
    :param exclude: return if condition patter is NOT matched
    :param type: bool
    :param condition: search for pattern in output, return if matched
    :param type: str

    :param **kwargs: Optional arguments that ``execute`` takes.

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    matched: bool = False

    exclude = bool(exclude)

    start = time.time()
    check = start

    while (check - deadline) < start:
        response = execute(target, [command], *args, **kwargs)
        match = re.search(condition, str(response))

        if exclude and not match:
            matched = True
        elif match:
            matched = True

        callback(response, matched)

        if matched:
            break

        time.sleep(interval)
        check = time.time()


async def aexecute(channel: asyncio.Queue,
                   target: str,
                   commands: CommandList,
                   auth: Optional[Auth] = None,
                   encoding: str = EAPI_DEFAULT_FORMAT,
                   enable: bool = False,
                   secret: str = "",
                   cert: Optional[Certificate] = None,
                   verify: bool = False,
                   auto_complete: bool = False,
                   expand_aliases: bool = False,
                   include_error_detail: bool = False,
                   timestamps: bool = False,
                   streaming: bool = False) -> None:
    """Send command(s) to an eAPI target (async version)

    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param auth:
    :param type: tuple
    :param encoding: json or text (default: json)
    :param type: str
    :param enable:
    :param type: bool
    :param secret:
    :param type: str
    :param cert:
    :param verify:
    :param auto_complete:
    :param type: bool
    :param expand_aliases:
    :param type: bool
    :param include_error_detail:
    :param type: bool
    :param timestamps:
    :param type: bool
    :param streaming:
    :param type: bool

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    if enable:
        commands.insert(0, Command(cmd="enable", input=secret))

    async with AsyncSession(auth=auth, cert=cert, verify=verify) as sess:
        response = await sess.call(target, commands, EapiOptions(
            encoding=encoding,
            timestamps=timestamps,
            auto_complete=auto_complete,
            expand_aliases=expand_aliases,
            include_error_detail=include_error_detail,
            streaming=streaming
        ))

        await channel.put(response)

async def aconfigure(channel: asyncio.Queue, target: str, commands: CommandList,
                     *args, **kwargs):
    """Wrap commands in a 'configure'/'end' block (async version)

    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, "configure")
    commands.append("end")
    await aexecute(channel, target, commands, *args, **kwargs)


async def awatch(channel: asyncio.Queue,
                 target: str,
                 command: Union[str, Command],
                 interval: Optional[int] = EAPI_WATCH_INTERVAL,
                 deadline: Optional[float] = EAPI_WATCH_DEADLINE,
                 exclude: bool = False,
                 condition: Optional[str] = NEVER_RE,
                 *args, **kwargs):

    """Watch a command until deadline or condition matches (async version)

    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmand: command to send
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param interval: time between repeating command
    :param type: int
    :param deadline: end loop after specified time
    :param type: float
    :param exclude: return if condition patter is NOT matched
    :param type: bool
    :param condition: search for pattern in output, return if matched
    :param type: str
    :param **kwargs: optional arguments that ``execute`` takes.
    """

    rsp_chan = asyncio.Queue()
    response: Response

    matched: bool = False

    exclude = bool(exclude)

    start = time.time()
    check = start

    while (check - deadline) < start:
        await aexecute(rsp_chan, target, [command], *args, **kwargs)
        response = await rsp_chan.get()

        match = re.search(condition, str(response))

        if exclude and not match:
            matched = True
        elif match:
            matched = True

        # await callback(response, matched)
        await channel.put((response, matched))

        if matched:  
            break

        time.sleep(interval)
        check = time.time()
    
    await rsp_chan.put(None)
    await channel.put(None)
