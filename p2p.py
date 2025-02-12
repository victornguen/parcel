import asyncio
import tempfile
from pathlib import Path

from iroh import BlobTicket, AddrInfoOptions, SetTagOption, \
    WrapOption, AddProgressType, DownloadProgressType, BlobExportFormat, BlobExportMode
from iroh import Iroh, NodeOptions


class ParcelNode:
    def __init__(
            self,
            persistent: bool = False,
    ):

        self.node_opts = NodeOptions(
            enable_docs=True
        )
        self.persistent = persistent
        self.node: Iroh | None = None

    async def start(self):
        try:
            if self.persistent:
                dir = tempfile.TemporaryDirectory()
                print(f"Using persistent storage at {dir.name}")
                self.node = await Iroh.persistent_with_options(dir.name, self.node_opts)
            else:
                print("Using in-memory storage")
                self.node = await Iroh.memory_with_options(self.node_opts)
        except Exception as e:
            print(e)
            raise e

    async def _author(self):
        return await self.node.authors().default()

    async def share_blob(self, path, in_place=True):
        class AddCallback:
            collection_hash = None
            format = None
            blob_hashes = []

            async def progress(self, progress_event):
                print(progress_event.type())
                match progress_event.type():
                    case AddProgressType.ALL_DONE:
                        all_done_event = progress_event.as_all_done()
                        self.collection_hash = all_done_event.hash
                        self.format = all_done_event.format
                    case AddProgressType.ABORT:
                        abort_event = progress_event.as_abort()
                        print(abort_event.error)
                        raise Exception(abort_event.error)
                    case AddProgressType.DONE:
                        done_event = progress_event.as_done()
                        print(done_event.hash)
                        self.blob_hashes.append(done_event.hash)

        tag = SetTagOption.auto()
        filename = Path(path).name
        wrap = WrapOption.wrap(filename)
        cb = AddCallback()
        await self.node.blobs().add_from_path(path, in_place, tag, wrap, cb)
        # author = await self._author()
        print("Blob format: ", cb.format)
        ticket = await self.node.blobs().share(cb.collection_hash, cb.format, AddrInfoOptions.RELAY_AND_ADDRESSES)
        # key = iroh.path_to_key(path, None, None)
        # with open(path, 'rb') as f:
        #     await blob.set_bytes(author, key, f.read())

        blobs = await self.node.blobs().list()
        print(f"blobs: {", ".join(str(h) for h in blobs)}")


        print(f"🚀 Sharing data - keep this running until transfer completes!")
        print(f"🔑 Share this ticket:\n{ticket}")
        await asyncio.sleep(100000)

    async def share_blob_in_mem(self, path):
        filename = Path(path).name
        content = Path(path).read_bytes()
        bo = await self.node.blobs().add_bytes_named(content, filename)
        print("Blob format: ", bo.format)

        ticket = await self.node.blobs().share(bo.hash, bo.format, AddrInfoOptions.RELAY_AND_ADDRESSES)

        print(f"🚀 Sharing data - keep this running until transfer completes!")
        print(f"🔑 Share this ticket:\n{ticket}")
        await asyncio.Future()

    async def receive_blob(self, ticket_str, output_dir):
        class DownloadCallback:
            async def progress(self, progress_event):
                match progress_event.type():
                    case DownloadProgressType.ALL_DONE:
                        written = progress_event.as_all_done().bytes_written
                        print(f"done downloading, written {written} bytes")
                    case DownloadProgressType.ABORT:
                        abort_event = progress_event.as_abort()
                        print(abort_event.error)
                        raise Exception(abort_event.error)
        cb = DownloadCallback()
        ticket = BlobTicket(ticket_str)
        print("Ticket hash: ", ticket.hash())
        await self.node.blobs().download(ticket.hash(), opts=ticket.as_download_options(), cb=cb)
        # author = await self._author()
        blob_collections = await self.node.blobs().list_collections()
        blobs = await self.node.blobs().list()
        print(f"blob_collections: {', '.join((str(c) for c in blob_collections))}")
        print(f"blobs: {', '.join(str(b) for b in blobs)}")
        await self.node.blobs().export(ticket.hash(), output_dir,  BlobExportFormat.COLLECTION,  BlobExportMode.COPY)
        # key = iroh.path_to_key(output_dir, None, None)
        # with open(output_dir, 'wb') as f:
        #     f.write(await blob.get_bytes(author, key))
        # print(f"\n✅ Download complete! Saved to: {output_dir}")

    async def receive_blob_in_mem(self, ticket_str, output_dir):
        class DownloadCallback:
            async def progress(self, progress_event):
                match progress_event.type():
                    case DownloadProgressType.ALL_DONE:
                        written = progress_event.as_all_done().bytes_written
                        print(f"done downloading, written {written} bytes")
                    case DownloadProgressType.ABORT:
                        abort_event = progress_event.as_abort()
                        print(abort_event.error)
                        raise Exception(abort_event.error)
        cb = DownloadCallback()
        ticket = BlobTicket(ticket_str)
        print("Ticket hash: ", ticket.hash())
        await self.node.blobs().download(ticket.hash(), opts=ticket.as_download_options(), cb=cb)
        # author = await self._author()
        blob_collections = await self.node.blobs().list_collections()
        blobs = await self.node.blobs().list()
        print(f"blob_collections: {', '.join((str(c) for c in blob_collections))}")
        print(f"blobs: {', '.join(str(b) for b in blobs)}")
        content = await self.node.blobs().read_to_bytes(ticket.hash())
        with open(output_dir, '+wb') as f:
            f.write(content)
        print(f"\n✅ Download complete! Saved to: {Path(output_dir).absolute()}")