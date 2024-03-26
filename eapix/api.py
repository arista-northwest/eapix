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
from eapix.sessions import Session, AsyncSession

NEVER_RE = r'(?!x)x'

def version():
    """get installed version
    
    :return: str"""
    return __version__

def execute(target: str,
            commands: CommandList,
            options: EapiOptions = EapiOptions(),
            auth: Optional[Auth] = None,
            cert: Optional[Certificate] = None,
            verify: Optional[bool] = None,
            **kwargs) -> Response:
    """Send an eAPI request

    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param format: json or text (default: json)
    :param type: str
    :param **kwargs: pass through ``httpx`` options

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    with Session(auth=auth, cert=cert, verify=verify) as sess:
        return sess.call(target, commands, options, **kwargs)


def enable(target: str,
           commands: CommandList,
           secret: str = "",
           options: EapiOptions = EapiOptions(),
           **kwargs) -> Response:
    """Prepend 'enable' command
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param **kwargs: Optional arguments that ``_send`` takes.

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, Command(cmd="enable", input=secret))
    return execute(target, commands, options, **kwargs)


def configure(target: str,
              commands: CommandList,
              options: EapiOptions = EapiOptions(),
              **kwargs) -> Response:
    """Wrap commands in a 'configure'/'end' block

    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param **kwargs: Optional arguments that ``execute`` takes.

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, Command("configure"))
    commands.append(Command("end"))
    return execute(target, commands, options, **kwargs)


def watch(target: str,
          command: Union[str, Command],
          options: EapiOptions = EapiOptions(),
          callback: Callable = None,
          interval: Optional[int] = None,
          deadline: Optional[float] = None,
          exclude: bool = False,
          condition: Optional[str] = None,
          **kwargs) -> Optional[Iterator[Response]]:
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

    if not interval:
        interval = 2

    if not deadline:
        deadline = math.inf

    if not condition:
        condition = NEVER_RE

    start = time.time()
    check = start

    while (check - deadline) < start:
        response = execute(target, [command], options, **kwargs)
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
                   options: EapiOptions = EapiOptions(),
                   auth: Optional[Auth] = None,
                   cert: Optional[Certificate] = None,
                   verify: Optional[bool] = None,
                   **kwargs) -> None:
    """Send command(s) to an eAPI target (async version)

    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param **kwargs: pass through ``httpx`` options

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """
    
    async with AsyncSession(auth=auth, cert=cert, verify=verify) as sess:
        response = await sess.call(target, commands, options, **kwargs)

        await channel.put(response)

async def aenable(channel: asyncio.Queue,
                  target: str, commands: CommandList,
                  secret: str = "",
                  options: EapiOptions = EapiOptions(),
                  **kwargs):
    """Prepend 'enable' command (async version)
    
    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param **kwargs: Optional arguments that ``_send`` takes.

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, Command(cmd="enable", input=secret))
    await aexecute(channel, target, commands, options, **kwargs)


async def aconfigure(channel: asyncio.Queue,
                     target: str,
                     commands: CommandList,
                     options: EapiOptions = EapiOptions(),
                     **kwargs):
    """Wrap commands in a 'configure'/'end' block (async version)

    :param channel: results channel
    :param type: asyncio.Queue
    :param target: eAPI target
    :param type: Target
    :param commmands: List of commands to send to target
    :param type: list
    :param options: eapi options
    :param type: EapiOptions
    :param **kwargs: Optional arguments that ``execute`` takes.

    :return: :class:`Response <Response>` object
    :rtype: eapi.messages.Response
    """

    commands.insert(0, "configure")
    commands.append("end")
    await aexecute(channel, target, commands, options, **kwargs)


async def awatch(channel: asyncio.Queue,
                 target: str,
                 command: Union[str, Command],
                 options: EapiOptions = EapiOptions(),
                 interval: int = 1,
                 deadline: float = math.inf,
                 exclude: bool = False,
                 condition: str = NEVER_RE,
                 **kwargs):

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
        await aexecute(rsp_chan, target, [command], options, **kwargs)
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
