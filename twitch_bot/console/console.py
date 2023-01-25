"""Web console for interacting with the bot."""

import asyncio
import os

import remi.gui as gui
from remi import App, Server

import zmq_utils

from discord import discord_sender
from log import LOG


class ConsoleLauncher(object):
    """Console launcher class."""

    def __init__(self):
        """Init."""
        super(ConsoleLauncher, self).__init__()

    async def init(self, bot: object) -> object:
        """Async init.

        Args:
            bot (TwitchBot): Twitch bot instance.

        Returns:
            self (ConsoleLauncher): Class instance.
        """
        self.console = Server(
            Console,
            address=str(bot.twitch_config.get('console_address', '0.0.0.0')),
            multiple_instance=False,
            start=False,
            port=int(bot.twitch_config.get('console_port', 8081)),
            start_browser=bot.twitch_config.get('open_console', True),
            userdata=(bot,),
        )

        self.console.start()

        return self


class Console(App):
    """Console."""

    def __init__(self, *args):
        """Init."""
        res_path = os.path.join(os.path.dirname(__file__), 'res')
        super(Console, self).__init__(
            *args, static_file_path={'res': res_path}
        )

    def main(self, bot) -> gui.Container:
        """Main page definition.

        Args:
            bot (TwitchBot): Twitch bot instance.

        Returns:
            main_container (gui.Container): Central container widget.
        """
        self.bot = bot

        # Container for the entire web page.
        main_container = gui.Container(
            width=1000,
            margin='0px auto',
            style={'display': 'grid', 'overflow': 'hidden'},
        )

        # Add a title.
        title = gui.Label('TwitchBot Command Console', margin='5px')
        title.style['font-size'] = '30px'
        main_container.append(title)

        # Add the buttons at the top.
        buttons_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )
        main_container.append(buttons_container)

        # Start bot button.
        self.start_bot_button = gui.Button('Start Bot', margin='5px')
        self.start_bot_button.attributes['name'] = 'start_bot'
        self.start_bot_button.style['padding'] = '10px 20px'
        self.start_bot_button.onclick.do(self.start_bot)
        buttons_container.append(self.start_bot_button)

        # Stop bot button.
        self.stop_bot_button = gui.Button('Stop Bot', margin='5px')
        self.stop_bot_button.attributes['name'] = 'stop_bot'
        self.stop_bot_button.style['padding'] = '10px 20px'
        self.stop_bot_button.onclick.do(self.stop_bot)
        buttons_container.append(self.stop_bot_button)

        # Reload config button.
        self.reload_config_button = gui.Button('Reload Configs', margin='5px')
        self.reload_config_button.attributes['name'] = 'reload_configs'
        self.reload_config_button.style['padding'] = '10px 20px'
        self.reload_config_button.onclick.do(self.reload_configs)
        buttons_container.append(self.reload_config_button)

        # Reload plugins button.
        self.reload_plugins_button = gui.Button('Reload Plugins', margin='5px')
        self.reload_plugins_button.attributes['name'] = 'reload_plugins'
        self.reload_plugins_button.style['padding'] = '10px 20px'
        self.reload_plugins_button.onclick.do(self.reload_plugins)
        buttons_container.append(self.reload_plugins_button)

        # Reload commands button.
        self.reload_commands_button = gui.Button(
            'Reload Commands', margin='5px'
        )
        self.reload_commands_button.attributes['name'] = 'reload_commands'
        self.reload_commands_button.style['padding'] = '10px 20px'
        self.reload_commands_button.onclick.do(self.reload_commands)
        buttons_container.append(self.reload_commands_button)

        # Connect / Reconnect OBS button.
        self.reconnect_obs_button = gui.Button(
            'Connect / Reconnect OBS', margin='5px'
        )
        self.reconnect_obs_button.attributes['name'] = 'reconnect_obs'
        self.reconnect_obs_button.style['padding'] = '10px 20px'
        self.reconnect_obs_button.onclick.do(self.reconnect_obs)
        buttons_container.append(self.reconnect_obs_button)

        # Disconnect OBS button.
        self.disconnect_obs_button = gui.Button('Disonnect OBS', margin='5px')
        self.disconnect_obs_button.attributes['name'] = 'disconnect_obs'
        self.disconnect_obs_button.style['padding'] = '10px 20px'
        self.disconnect_obs_button.onclick.do(self.disconnect_obs)
        buttons_container.append(self.disconnect_obs_button)

        # Create the containers for the other components.
        chat_container = self.create_chat_container()
        main_container.append(chat_container)

        plugin_container = self.create_plugin_container()
        main_container.append(plugin_container)

        command_container = self.create_command_container()
        main_container.append(command_container)

        tcp_container = self.create_tcp_container()
        main_container.append(tcp_container)

        zmq_container = self.create_zmq_container()
        main_container.append(zmq_container)

        discord_container = self.create_discord_container()
        main_container.append(discord_container)

        # event_container = self.create_event_container()
        # main_container.append(event_container)

        return main_container

    def create_chat_container(self) -> gui.Container:
        """Create a container for the chat related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the chat
                related widgets.
        """
        chat_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        chat_label = gui.Label(
            'Chat Message: ', margin='5px', width='150px', height='40px'
        )
        chat_label.style['text-align'] = 'right'
        chat_label.style['padding-top'] = '20px'
        chat_container.append(chat_label)

        self.chat_message = gui.TextInput(width=200, height=40, margin='5px')
        self.chat_message.attributes['placeholder'] = 'message'
        self.chat_message.style['line-height'] = '40px'
        self.chat_message.style['padding-left'] = '5px'
        chat_container.append(self.chat_message)

        self.send_chat_button = gui.Button('Send', margin='5px')
        self.send_chat_button.attributes['name'] = 'send_chat'
        self.send_chat_button.style['padding'] = '10px 20px'
        self.send_chat_button.onclick.do(self.send_chat_message)
        chat_container.append(self.send_chat_button)

        return chat_container

    def create_plugin_container(self) -> gui.Container:
        """Create a container for the plugin related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the plugin
                related widgets.
        """
        plugin_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        plugin_label = gui.Label(
            'Plugins: ', margin='5px', width='150px', height='40px'
        )
        plugin_label.style['text-align'] = 'right'
        plugin_label.style['padding-top'] = '20px'
        plugin_container.append(plugin_label)

        categories = sorted(self.bot.plugins.keys())
        self.plugin_category_dropdown = gui.DropDown.new_from_list(
            items=[], width=200, height=40, margin='5px'
        )
        for category in categories:
            self.plugin_category_dropdown.add_child(
                category, gui.DropDownItem(category)
            )
        self.plugin_category_dropdown.onchange.do(
            self.plugin_category_dropdown_changed
        )
        self.plugin_category_dropdown.select_by_value(categories[0])
        plugin_container.append(self.plugin_category_dropdown)

        plugins = sorted(self.bot.plugins[categories[0]].keys())
        self.plugin_dropdown = gui.DropDown.new_from_list(
            items=[], width=200, height=40, margin='5px'
        )
        for plugin in plugins:
            self.plugin_dropdown.add_child(plugin, gui.DropDownItem(plugin))
        self.plugin_dropdown.onchange.do(self.plugin_dropdown_changed)
        self.plugin_dropdown.select_by_value(plugins[0])
        plugin_container.append(self.plugin_dropdown)

        self.plugin_command_args = gui.TextInput(
            width=200, height=40, margin='5px'
        )
        self.plugin_command_args.attributes['placeholder'] = 'arg1,arg2,arg3'
        self.plugin_command_args.style['line-height'] = '40px'
        self.plugin_command_args.style['padding-left'] = '5px'
        plugin_container.append(self.plugin_command_args)

        self.run_plugin_button = gui.Button('Run', margin='5px')
        self.run_plugin_button.attributes['name'] = 'run_plugin'
        self.run_plugin_button.style['padding'] = '10px 20px'
        self.run_plugin_button.onclick.do(self.run_plugin)
        plugin_container.append(self.run_plugin_button)

        return plugin_container

    def create_command_container(self) -> gui.Container:
        """Create a container for the command related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the command
                related widgets.
        """
        command_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        command_label = gui.Label(
            'Command: ', margin='5px', width='150px', height='40px'
        )
        command_label.style['text-align'] = 'right'
        command_label.style['padding-top'] = '20px'
        command_container.append(command_label)

        self.command_dropdown = gui.DropDown.new_from_list(
            self.bot.simple_commands.commands,
            width=200,
            height=40,
            margin='5px',
        )
        self.command_dropdown.onchange.do(self.command_dropdown_changed)
        self.plugin_dropdown.select_by_value(
            list(self.bot.simple_commands.commands.keys())[0]
        )
        command_container.append(self.command_dropdown)

        self.command_args = gui.TextInput(width=200, height=40, margin='5px')
        self.command_args.attributes['placeholder'] = 'arg1,arg2,arg3'
        self.command_args.style['line-height'] = '40px'
        self.command_args.style['padding-left'] = '5px'
        command_container.append(self.command_args)

        self.run_command_button = gui.Button('Run', margin='5px')
        self.run_command_button.attributes['name'] = 'run_command'
        self.run_command_button.style['padding'] = '10px 20px'
        self.run_command_button.onclick.do(self.run_command)
        command_container.append(self.run_command_button)

        return command_container

    def create_tcp_container(self) -> gui.Container:
        """Create a container for the TCP related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the TCP
                related widgets.
        """
        tcp_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        tcp_label = gui.Label(
            'TCP Message: ', margin='5px', width='150px', height='40px'
        )
        tcp_label.style['text-align'] = 'right'
        tcp_label.style['padding-top'] = '20px'
        tcp_container.append(tcp_label)

        self.tcp_message = gui.TextInput(width=200, height=40, margin='5px')
        self.tcp_message.attributes['placeholder'] = 'message'
        self.tcp_message.style['line-height'] = '40px'
        self.tcp_message.style['padding-left'] = '5px'
        tcp_container.append(self.tcp_message)

        self.run_tcp_button = gui.Button('Send', margin='5px')
        self.run_tcp_button.attributes['name'] = 'send_tcp'
        self.run_tcp_button.style['padding'] = '10px 20px'
        self.run_tcp_button.onclick.do(self.send_tcp_message)
        tcp_container.append(self.run_tcp_button)

        return tcp_container

    def create_zmq_container(self) -> gui.Container:
        """Create a container for the ZMQ related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the ZMQ
                related widgets.
        """
        zmq_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        zmq_label = gui.Label(
            'ZMQ Message: ', margin='5px', width='150px', height='40px'
        )
        zmq_label.style['text-align'] = 'right'
        zmq_label.style['padding-top'] = '20px'
        zmq_container.append(zmq_label)

        self.zmq_recipient = gui.TextInput(width=200, height=40, margin='5px')
        self.zmq_recipient.attributes['placeholder'] = 'subscriber'
        self.zmq_recipient.style['line-height'] = '40px'
        self.zmq_recipient.style['padding-left'] = '5px'
        zmq_container.append(self.zmq_recipient)

        self.zmq_message = gui.TextInput(width=200, height=40, margin='5px')
        self.zmq_message.attributes['placeholder'] = 'message'
        self.zmq_message.style['line-height'] = '40px'
        self.zmq_message.style['padding-left'] = '5px'
        zmq_container.append(self.zmq_message)

        self.run_zmq_button = gui.Button('Send', margin='5px')
        self.run_zmq_button.attributes['name'] = 'send_zmq'
        self.run_zmq_button.style['padding'] = '10px 20px'
        self.run_zmq_button.onclick.do(self.send_zmq_message)
        zmq_container.append(self.run_zmq_button)

        return zmq_container

    def create_discord_container(self) -> gui.Container:
        """Create a container for the Discord related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the Discord
                related widgets.
        """
        discord_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        discord_label = gui.Label(
            'Discord Message: ', margin='5px', width='150px', height='40px'
        )
        discord_label.style['text-align'] = 'right'
        discord_label.style['padding-top'] = '20px'
        discord_container.append(discord_label)

        self.discord_message = gui.TextInput(
            width=200, height=40, margin='5px'
        )
        self.discord_message.attributes['placeholder'] = 'message'
        self.discord_message.style['line-height'] = '40px'
        self.discord_message.style['padding-left'] = '5px'
        discord_container.append(self.discord_message)

        self.send_discord_button = gui.Button('Send', margin='5px')
        self.send_discord_button.attributes['name'] = 'send_discord'
        self.send_discord_button.style['padding'] = '10px 20px'
        self.send_discord_button.onclick.do(self.send_discord_message)
        discord_container.append(self.send_discord_button)

        return discord_container

    def create_event_container(self) -> gui.Container:
        """Create a container for the event related widgets.

        Returns:
            chat_container (gui.Container): Container widget with the event
                related widgets.
        """
        event_container = gui.Container(
            width='100%',
            layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
            margin='0px',
            style={
                'display': 'flex',
                'overflow': 'auto',
                'align-items': 'center',
            },
        )

        event_label = gui.Label(
            'Send Event: ', margin='5px', width='150px', height='40px'
        )
        event_label.style['text-align'] = 'right'
        event_label.style['padding-top'] = '20px'
        event_container.append(event_label)

        self.event_dropdown = gui.DropDown.new_from_list(
            [], width=200, height=40, margin='5px'
        )
        self.event_dropdown.onchange.do(self.event_dropdown_changed)
        self.event_dropdown.select_by_value('DropDownItem 0')
        event_container.append(self.event_dropdown)

        self.send_event_button = gui.Button('Send', margin='5px')
        self.send_event_button.attributes['name'] = 'send_event'
        self.send_event_button.style['padding'] = '10px 20px'
        self.send_event_button.onclick.do(self.send_event)
        event_container.append(self.send_event_button)

        return event_container

    def start_bot(self, widget: gui.Widget) -> None:
        """Start up the bot.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        pass

    def stop_bot(self, widget: gui.Widget) -> None:
        """Stop the bot.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        pass

    def reload_configs(self, widget: gui.Widget) -> None:
        """Reload the bot config.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(self.bot.reload_config())

    def reload_plugins(self, widget: gui.Widget) -> None:
        """Reload the plugins.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(self.bot._initialize_plugins(do_reload=True))

    def reload_commands(self, widget: gui.Widget) -> None:
        """Reload the simple commands.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(self.bot.reload_simple_commands())

    def reconnect_obs(self, widget: gui.Widget) -> None:
        """Connect or reconnect OBS.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(self.bot.obs.reconnect())

    def disconnect_obs(self, widget: gui.Widget) -> None:
        """Disconnect OBS.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(self.bot.obs.disconnect())

    def send_chat_message(self, widget: gui.Widget) -> None:
        """Send a message to chat.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        text = self.chat_message.text
        if text:
            asyncio.run(self.bot.send_message(text))

    def run_plugin(self, widget: gui.Widget) -> None:
        """Run a plugin.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        plugin_category = self.plugin_category_dropdown.get_value()
        plugin_name = self.plugin_dropdown.get_value()
        if not plugin_name:
            key = sorted(self.plugin_dropdown.children.keys())[0]
            plugin_name = self.plugin_dropdown.children[key].value
        LOG.debug(f'Looking for plugin: {plugin_category} {plugin_name}')
        plugin = self.bot.plugins[plugin_category][plugin_name]

        asyncio.run(
            self.bot._run_plugin(
                plugin,
                None,
                {'name': 'descvert_bot', 'id': self.bot.bot_user_id},
                plugin_name,
                [
                    p.strip()
                    for p in self.plugin_command_args.get_text().split(',')
                ],
            )
        )

    def run_command(self, widget: gui.Widget) -> None:
        """Run a simple command.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        asyncio.run(
            self._run_simple_command(
                None,
                {'name': 'descvert_bot', 'id': self.bot.bot_user_id},
                self.command_dropdown.get_item(),
                [a.strip() for a in self.command_args.get_text().split(',')],
            )
        )

    def send_tcp_message(self, widget: gui.Widget) -> None:
        """Send a TCP message.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        if self.tcp_message:
            asyncio.run(
                self.bot.tcp_server.publish_message(
                    self.tcp_message.get_text()
                )
            )

    def send_zmq_message(self, widget: gui.Widget) -> None:
        """Send a ZMQ message.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        if self.zmq_recipient and self.zmq_message:
            asyncio.run(
                zmq_utils.publish_message(
                    self.zmq_recipient.get_text, self.zmq_message.get_text()
                )
            )

    def send_discord_message(self, widget: gui.Widget) -> None:
        """Send a Discord message.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        message = self.discord_message.get_text()
        if message:
            asyncio.run(discord_sender.send_discord_message(message))

    def send_event(self, widget: gui.Widget) -> None:
        """Send an event.

        Args:
            widget (gui.Widget): Widget that made the function call.
        """
        pass

    def plugin_category_dropdown_changed(
        self, widget: gui.Widget, value: str
    ) -> None:
        """Add plugins belonging to the new category to the plugin_dropdown.

        Args:
            widget (gui.Widget): Widget that made the function call.
            value (str): New value of the dropdown.
        """
        plugins = sorted(self.bot.plugins[value].keys())

        self.plugin_dropdown.empty()
        for plugin in plugins:
            self.plugin_dropdown.add_child(plugin, gui.DropDownItem(plugin))

        self.plugin_dropdown.select_by_value(plugins[0])

    def plugin_dropdown_changed(self, widget: gui.Widget, value: str) -> None:
        """Clear the plugin_command_args field when the plugin changes.

        Args:
            widget (gui.Widget): Widget that made the function call.
            value (str): New value of the dropdown.
        """
        self.plugin_command_args.set_text('')

    def command_dropdown_changed(self, widget: gui.Widget, value: str) -> None:
        """Clear the plugin_command_args field when the command changes.

        Args:
            widget (gui.Widget): Widget that made the function call.
            value (str): New value of the dropdown.
        """
        self.command_args.set_text('')

    def event_dropdown_changed(self, widget: gui.Widget, value: str) -> None:
        """Not implemented.

        Args:
            widget (gui.Widget): Widget that made the function call.
            value (str): New value of the dropdown.
        """
        pass

    def on_close(self):
        """On close event."""
        super(Console, self).on_close()

    def on_window_close(self):
        """On window close event."""
        self.close()
