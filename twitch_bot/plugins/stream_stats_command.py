"""Stream Stats plugin."""

from datetime import datetime

from tortoise import fields

import utils

from plugins._base_model import AbstractPluginModel
from plugins._base_plugins import BaseCommandPlugin, BaseIntervalPlugin


class QuoteModel(AbstractPluginModel):
    date = fields.CharField(max_length=255, null=False)
    time = fields.CharField(max_length=255, null=False)
    viewer_count = fields.IntField(null=False)

    class Meta:
        table = 'viewer_count'


class ViewerCountCommand(BaseIntervalPlugin):
    """Viewer count plugin."""

    COMMAND = 'viewer_count'
    ALLOWED = ['bot']
    INTERVAL = 10
    TABLE = 'viewer_count'
    FIELDS = {
        'date': 'TEXT NOT NULL',
        'time': 'TEXT NOT NULL',
        'viewer_count': 'INTEGER NOT NULL',
    }

    async def run(self) -> dict:
        """Count the number of viewers and save it to a database."""
        now = datetime.now()
        date = str(now.date())
        time = f'{now.hour}:{now.minute}'
        viewer_count = await utils.get_viewer_count(self.bot)

        return {'date': date, 'time': time, 'viewer_count': viewer_count}


class GraphStatsCommand(BaseCommandPlugin):
    """Graph Stats plugin."""

    COMMAND = 'graph_stats'
    ALLOWED = ['bot']

    async def run(self) -> None:
        """Graph the viewer count over time and save the graph as an image."""
        await utils.graph_stream_stats(self.bot)
        await utils.generate_stats_markdown(self.bot)
