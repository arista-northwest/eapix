# -*- coding: utf-8 -*-
# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import asyncio
import sys

from eapix.exceptions import EapiError
import click

import eapix.version
import eapix.exceptions
import eapix.environments
import eapix.types

from eapix import util


@click.group()
@click.option("--targets", "-t", multiple=True, help="specifies targets")
@click.option("--format", "-e", default="text")
@click.option("--auto-complete", is_flag=True)
@click.option("--expand_aliases", is_flag=True)
@click.option("--include-error-detail", is_flag=True)
@click.option("--streaming", "-s", is_flag=True, help="enable streaming mode")
@click.option("--username", "-u", default="admin", help="Username (default: admin")
@click.option("--password", "-p", default="", help="Username (default: <blank>")
@click.option("--cert", help="Client certificate file")
@click.option("--key", help="Private key file name")
@click.option("--verify", is_flag=True, help="verify SSL cert")
@click.version_option(eapix.version.__version__)
@click.pass_context
def main(ctx,
         targets,
         format,
         auto_complete,
         expand_aliases,
         include_error_detail,
         streaming,
         username,
         password,
         cert,
         key,
         verify):
    pair = None
    auth = None

    if cert:
        pair = (cert, key)

    if not key:
        auth = (username, password)

    eapi_options = eapix.types.EapiOptions(
        format=format,
        streaming=streaming,
        auto_complete=auto_complete,
        expand_aliases=expand_aliases,
        include_error_detail=include_error_detail
    )
    ctx.obj = {
        'targets': targets,
        'options': eapi_options,
        'auth': auth,
        'cert': pair,
        'verify': verify,
    }

@main.command()
@click.argument("commands", nargs=-1, required=True)
@click.pass_context
def execute(ctx, commands):
    targets = ctx.obj["targets"]
    options = ctx.obj["options"]
    auth = ctx.obj["auth"]
    cert = ctx.obj["cert"]
    verify = ctx.obj["verify"]

    async def _consumer(channel):
        while True:
            rsp = await channel.get()

            if rsp is None:
                break

            if options.format == "json":
                print(rsp.json)
            else:
                print(rsp.pretty)
  
    async def _run(channel):
        tasks = []

        asyncio.create_task(_consumer(channel))

        for target in targets:
            producer = asyncio.create_task(
                eapix.aexecute(
                    channel,
                    target,
                    commands,
                    options,
                    auth=auth,
                    cert=cert,
                    verify=verify
                )
            )
            tasks.append(producer)

        await asyncio.gather(*tasks)
        # shutdown the channel
        await channel.put(None)

    channel = asyncio.Queue()
    asyncio.run(_run(channel))

@main.command()
@click.argument("command", nargs=1, required=True)
@click.option("--interval", "-i", type=int, default=None, help="Time between sends")
@click.option("--deadline", "-d", type=float, default=None, help="Limit how long to watch")
@click.option("--exclude", is_flag=True, help="Match if condition is FALSE")
@click.option("--condition", "-c", default=None, help="Pattern to search for, watch ends when matched")
@click.pass_context
def watch(ctx, command, interval, deadline, exclude, condition):

    target = ctx.obj["target"]
    options = ctx.obj["options"]
    auth = ctx.obj["auth"]
    cert = ctx.obj["cert"]
    verify = ctx.obj["verify"]

    def _cb(response, matched):
        if options.format == "json":
            print(response.json)
        else:
            util.clear_screen()
            print(f"Watching '{response[0].command}' in {response.target}")
            print()
            print(response[0])

    try:
        eapix.watch(target,
                    command,
                    options,
                    callback=_cb,
                    interval=interval,
                    deadline=deadline,
                    exclude=exclude,
                    condition=condition,
                    auth=auth,
                    cert=cert,
                    verify=verify)
    except eapix.EapiError as err:
        sys.exit(str(err))
