import logging
import re

from netdev.netdev_base import NetDev


class HPComware(NetDev):
    async def connect(self):
        """
        Prepare the session after the connection has been established.

        Using 3 functions:
            establish_connection() for connecting to device
            set_base_prompt() for finding and setting device prompt
            disable_paging() for non interact output in commands
        """
        await self._establish_connection()
        await self._set_base_prompt()
        await self._disable_paging(command='screen-length disable')

    @property
    def _priv_prompt_term(self):
        return ']'

    @property
    def _unpriv_prompt_term(self):
        return '>'

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Comware devices base_pattern is "[\]|>]prompt(\-\w+)?[\]|>]
        """
        logging.info("In set_base_prompt")
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self.base_prompt = prompt[1:-1]
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"[\[|<]{0}([\-\w]+)?[{1}|{2}]".format(re.escape(self.base_prompt), re.escape(priv_prompt),
                                                                    re.escape(unpriv_prompt))
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self.base_prompt

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'priv_prompt': ']',
            'unpriv_prompt': '>',
            'disable_paging': 'screen-length disable',
            'priv_enter': '',
            'priv_exit': '',
            'config_enter': 'system-view',
            'config_exit': 'return',
            'check_config_mode': ']'
        }
        # @formatter:on
        return command_mapper[command]

    async def _config_mode(self, config_command='system-view', exit_config_mode=True):
        """Enter configuration mode."""
        return await super(HPComware, self)._config_mode(config_command=config_command)

    async def _exit_config_mode(self, exit_config='return', pattern=''):
        """Exit config mode."""
        return await super(HPComware, self)._exit_config_mode(exit_config=exit_config)

    async def _check_config_mode(self, check_string=']', pattern=''):
        """Check whether device is in configuration mode. Return a boolean."""
        return await super(HPComware, self)._check_config_mode(check_string=check_string)
