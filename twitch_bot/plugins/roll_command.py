"""Roll plugin."""

import random
import re

from plugins._base_plugins import BaseCommandPlugin


class RollCommand(BaseCommandPlugin):
    """Roll plugin.

    Roll any number of any kind of dice and return the result(s).
    """

    COMMAND = 'roll'

    async def run(self) -> None:
        """Roll some dice."""
        if not self.command_args:
            await self.send_message(
                'Please provide 1 or more dice to roll in dice notation: XdY'
            )
            return -1

        # Check for a modifier
        if '+' in self.command_args:
            index = self.command_args.index('+')
            mod = int(self.command_args[index + 1])
            # Remove the modifier from the list
            self.command_args = self.command_args[0:index]
        else:
            mod = 0

        results = await self.roll(self.command_args)
        if not results:
            await self.send_message('Sorry, I didn\'t understand your rolls.')
            return -1

        if mod != 0:
            results['total'] += mod
            results['individual_rolls'].append(str(mod))

        message = 'You rolled: {} for a total of {}.'.format(
            '+'.join(results['individual_rolls']), results['total']
        )

        if results['crit_success'] == 1:
            message += ' You even got a critical success!'
        elif results['crit_success'] > 1:
            message += ' Wow! You got {} critical successes!'.format(
                results['crit_success']
            )

        if results['crit_failure'] == 1:
            message += ' Unfortunately, you got a critical failure.'
        elif results['crit_failure'] > 1:
            message += ' Big oof though, you got {} critical failures.'.format(
                results['crit_failure']
            )

        await self.send_message(message)

    async def roll(self, command_args):
        """Roll the dice.

        Args:
            command_args (list): Argument(s) for the command.

        Returns:
            (dict): Dictionary of roll results.
        """
        pattern = re.compile(r'(\d+)d(\d+|%)')
        individual_rolls = []
        total = 0
        crit_success = 0
        crit_failure = 0

        for command_arg in command_args:
            match = re.search(pattern, command_arg)
            if not match:
                return None

            count, die_type = match.groups()

            for inc in range(int(count)):
                # Used for percentage dice (00 to 90 in increments of 10)
                if die_type == '%':
                    roll = random.randint(0, 9) * 10
                else:
                    roll = random.randint(1, int(die_type))

                individual_rolls.append(str(roll))
                total += roll

                if die_type == 20:
                    if roll == 20:
                        crit_success += 1

                    elif roll == 1:
                        crit_failure += 1

        return {
            'individual_rolls': individual_rolls,
            'total': total,
            'crit_success': crit_success,
            'crit_failure': crit_failure,
        }
