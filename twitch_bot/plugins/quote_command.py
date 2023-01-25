"""Quote plugins."""

import random
import re

from tortoise import fields

import api

from plugins._base_model import AbstractPluginModel
from plugins._base_plugins import BaseCommandPlugin

QUOTE_RE = re.compile(r'(?P<id>\d+)?\s?\"(?P<quote>.+)\"\s+\@?(?P<quotee>\w+)')


class QuoteModel(AbstractPluginModel):
    quote_id = fields.IntField()
    quote = fields.CharField(max_length=255)
    quotee = fields.CharField(max_length=255)
    game = fields.CharField(max_length=255)

    class Meta:
        table = 'quotes'


class QuoteCommand(BaseCommandPlugin):
    """Quote plugin.

    Used to fetch a quote either intentionally or randomly.
    """

    COMMAND = 'quote'

    async def run(self) -> None:
        """Quote."""
        if self.command_args:
            index = self.command_args[0]
        else:
            index = random.randint(0, self.db.count_rows('quotes'))

        db_data = await self.db.read('quotes', queries={'id': index})
        if not db_data:
            return -1

        db_data_dict = dict(db_data)
        quote_id = db_data_dict['id']
        quote = db_data_dict['quote']
        quotee = db_data_dict['quotee']
        game = db_data_dict['game']
        await self.send_message(f'#{quote_id}: {quote} - {quotee} ({game})')


class AddQuoteCommand(BaseCommandPlugin):
    """Add quote plugin.

    Used to add interesting quotes from chat.
    """

    COMMAND = 'addquote'
    TABLE = 'quotes'
    FIELDS = {
        'quote_id': 'INT',
        'quote': 'STRING',
        'quotee': 'STRING',
        'game': 'STRING',
    }

    async def run(self) -> dict:
        """Add a quote."""
        if not self.command_args:
            await self.send_message(
                'Please use the form !addquote "This is the quote" @user'
            )
            return -1

        if self.last_row:
            last_row_dict = dict(self.last_row)
            quote_id = last_row_dict['id'] + 1
        else:
            quote_id = 1

        matches = re.match(QUOTE_RE, ' '.join(self.command_args))
        match_dict = matches.groupdict() if matches else {}
        quote = match_dict.get('quote', '')
        quotee = match_dict.get('quotee', '')

        if not quote or not quotee:
            await self.send_message(
                'Please use the form !addquote "This is the quote" @user'
            )
            return -1

        channel_data = await api.get_channel_data(
            self.bot.auth, self.bot.owner
        )
        game = channel_data['game_name']

        await self.send_message(
            'Successfully added quote '
            f'#{quote_id}: {quote} - {quotee} ({game})'
        )
        return {
            'quote_id': quote_id,
            'quote': quote,
            'quotee': quotee,
            'game': game,
        }


class EditQuoteCommand(BaseCommandPlugin):
    """Edit quote plugin.

    Used to fetch a quote and edit it.
    """

    ALLOWED = ['mod']
    COMMAND = 'editquote'

    async def run(self) -> None:
        """Edit a quote."""
        if not self.command_args:
            await self.send_message(
                'Please use the form !editquote 1 "This is the quote" @user'
            )
            return -1

        matches = re.match(QUOTE_RE, ' '.join(self.command_args))
        match_dict = matches.groupdict() if matches else {}
        quote_id = match_dict.get('quote', None)
        quote = match_dict.get('quote', '')
        quotee = match_dict.get('quotee', '')

        try:
            quote_id = int(quote_id)
        except ValueError:
            await self.send_message(f'Invalid quote ID: {quote_id}')
            return -1

        if not quote or not quotee:
            await self.send_message(
                'Please use the form !editquote 1 "This is the quote" @user'
            )
            return -1

        db_data = await self.db.read('quotes', queries={'id': quote_id})
        if not db_data:
            await self.send_message(f'No quote found at ID: {quote_id}')
            return -1

        await self.db.update(
            'quotes', {'quote': quote, 'quotee': quotee}, {'id': quote_id}
        )

        await self.send_message(
            f'Successfully edited quote #{quote_id}: {quote}'
        )


class RemoveQuoteCommand(BaseCommandPlugin):
    """Remove quote plugin.

    Used to fetch a quote and delete it.
    """

    ALLOWED = ['mod']
    COMMAND = 'removequote'

    async def run(self) -> None:
        """Remove a quote."""
        if self.command_args:
            quote_id = self.command_args[0]
        else:
            await self.send_message('No quote id given.')
            return -1

        db_data = await self.db.read('quotes', queries={'id': quote_id})
        if not db_data:
            await self.send_message(f'No quote found at quote_id: {quote_id}')
            return -1

        await self.db.delete('quotes', {'id': quote_id})

        await self.send_message(f'Successfully removed quote #{quote_id}.')
