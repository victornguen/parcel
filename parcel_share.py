import asyncio
import functools as ft
import os

import click
import iroh

import p2p


def async_cmd(func):
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group()
async def cli():
    """Peer-to-peer file and directory transfer tool"""
    iroh.iroh_ffi.uniffi_set_event_loop(asyncio.get_running_loop())
    pass


@cli.command()
@async_cmd
@click.argument('path', type=click.Path(exists=True))
async def share(path):
    """Send a file or directory"""
    click.echo(f'Sharing: {path}')
    await send_file_or_directory(path)


@cli.command()
@async_cmd
@click.argument('ticket')
@click.argument('path', type=click.Path(exists=False))
async def receive(ticket, path):
    """Receive a file or directory"""
    await receive_file_or_directory(ticket, path)


async def send_file_or_directory(path):
    if os.path.isdir(path):
        node = p2p.ParcelNode(persistent=False)
        await node.start()
        await node.share_blob(path, in_place=True)
        pass
    else:
        node = p2p.ParcelNode(persistent=False)
        await node.start()
        # await node.share_blob(path, in_place=True)
        await node.share_blob_in_mem(path)
        pass


async def receive_file_or_directory(ticket, output_dir='.'):
    node = p2p.ParcelNode(persistent=False)
    await node.start()
    await node.receive_blob(ticket, output_dir)
    pass


if __name__ == '__main__':
    asyncio.run(
        cli()
    )
