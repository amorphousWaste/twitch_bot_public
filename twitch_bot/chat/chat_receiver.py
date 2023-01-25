"""Chat receiver."""

import traceback

from websockets.exceptions import ConnectionClosedError

from chat import chat_events
from events import DummyEvent
from init import EVENT_QUEUE
from log import LOG


class ChatReceiver(object):
    """Chatreceiver."""

    def __init__(self, connection) -> None:
        """Init."""
        super(ChatReceiver, self).__init__()

        self.connection = connection

    async def get_data(self) -> str:
        """Get the data from the server.

        Returns:
            data (str): Received data from the server.
        """
        try:
            raw_data = (
                (await self.connection.socket.recv()).strip('\r\n').strip()
            )

        except KeyboardInterrupt:
            LOG.info('Exiting.')
            self.running = False
            raw_data = ''

        except ConnectionResetError:
            LOG.warning('Connection reset: reconnecting.')
            await self.connection._connect()
            return

        except BrokenPipeError:
            LOG.warning('Pipe broken: reconnecting.')
            await self.connection._connect()
            return

        except ConnectionClosedError:
            LOG.warning('Connection closed prematurely: reconnecting.')
            await self.connection._connect()
            return

        except Exception as e:
            LOG.error(
                'Attempt to get data failed failed: {}'.format(
                    getattr(e, 'message', repr(e)),
                )
            )
            traceback.print_exc()
            raw_data = ''

        return raw_data

    async def run(self) -> None:
        """Main functionality of the bot.

        This is run automatically when the thread is started.
        """
        LOG.debug('Running chat receiver loop.')
        self.running = True

        while self.running:
            # Get and decode the data sent from the server.
            raw_data = await self.get_data()

            if not raw_data:
                continue

            # The raw_data may contain multiple server messages,
            # so separate them.
            for data in filter(None, raw_data.split('\r\n')):
                # Respond to the keep-alive message so the session is not
                # terminated.
                if 'PING' in data:
                    LOG.debug('PING <> PONG')
                    await self.connection.send_server_message(
                        'PONG :tmi.twitch.tv\n'
                    )
                    continue

                event_type = await chat_events.get_event_type(data)

                # Mapping of chat message type to Event class.
                event_mapping = {
                    '353': chat_events.ExistingUsersEvent,
                    '366': chat_events.NamesEndEvent,
                    'ACK': chat_events.AckEvent,
                    'CAP': chat_events.CapEvent,
                    'JOIN': chat_events.JoinEvent,
                    'NOTICE': chat_events.NoticeEvent,
                    'PART': chat_events.PartEvent,
                    'PRIVMSG': chat_events.PubmsgEvent,
                    'ROOMSTATE': chat_events.RoomstateEvent,
                    'USERNOTICE': chat_events.UsernoticeEvent,
                    'USERSTATE': chat_events.UserstateEvent,
                    'WHISPER': chat_events.WhisperEvent,
                }

                event = await event_mapping.get(event_type, DummyEvent)().init(
                    data
                )
                LOG.debug('Adding event to queue')
                await EVENT_QUEUE.put(event)

        LOG.debug('ChatMessagereceiver no longer running.')
