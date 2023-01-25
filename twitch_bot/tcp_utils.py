"""Messaging via TCP.

Used to communicate with external programs through a pseudo
Publisher -> Subscriber relationship. TCP StreamReader is ignored.
"""

import asyncio

from configs import config_utils
from log import LOG


class TCPServer(object):
    """TCP server object."""

    async def init(self):
        """Async init.

        Returns:
            self (TCPServer): Class instance.
        """
        self.disconnected = True
        self.bad_disconnect = False
        self.config = await config_utils.load_config_file('bot_config')
        return self

    async def run(self) -> object:
        """Run the TCP server."""
        self.message_to_send = ''
        self.server = await asyncio.start_server(
            self.handle, self.config['tcp_host'], self.config['tcp_port']
        )
        while self.disconnected or self.bad_disconnect:
            await self.serve()

        LOG.info('TCP server stopped.')

    async def serve(self) -> None:
        """Serve the TCP server."""
        addr = ', '.join(
            str(sock.getsockname()) for sock in self.server.sockets
        )
        async with self.server:
            LOG.info(f'Serving on: {addr}')
            await self.server.serve_forever()

    async def handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle incoming and outgoing TCP messages.

        Args:
            reader (StreamReader): Incoming TCP data.
            writer (StreamWriter): Outgoing TCP data.
        """
        LOG.info('Connection to TCP client established.')
        self.disconnected = False
        self.bad_disconnect = False

        retry_counter = 0
        while True:
            # data = await reader.read(100)
            # addr = writer.get_extra_info('peername')

            # if data:
            #     msg = data.decode()
            #     LOG.debug(f'Message received via TCP from {addr}: {msg}')

            while not self.message_to_send:
                await asyncio.sleep(0.1)

            writer.write(self.message_to_send.encode())

            try:
                LOG.debug(f'TCP StreamWriter writing: {self.message_to_send}')
                await writer.drain()

            except (
                ConnectionResetError,
                BrokenPipeError,
                ConnectionAbortedError,
            ) as e:
                if retry_counter <= 4:
                    retry_counter += 1
                    LOG.warning(
                        'TCP message failed to send, retrying. '
                        f'(Attempt {retry_counter}'
                    )
                    await asyncio.sleep(retry_counter)
                    self.bad_disconnect = True
                    return

                else:
                    LOG.error(
                        'TCP server encountered an error: {}\n{}'.format(
                            e, getattr(e, 'message', repr(e))
                        )
                    )
                    retry_counter = 0

            self.message_to_send = None

    async def publish_message(self, message) -> None:
        """Publish a message via TCP.

        Args:
            message (str): Message to publish.
        """
        LOG.info(f'Sending over TCP: {message}')
        self.message_to_send = message
