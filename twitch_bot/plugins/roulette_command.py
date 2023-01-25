"""Roulette plugin."""

import random

from typing import Optional

from plugins._base_plugins import BaseCommandPlugin


class Space(object):
    """Roulette Space."""

    def __init__(self) -> None:
        """Init."""
        super(Space, self).__init__()

    async def init(
        self, number: int, color: str, row: int, column: int
    ) -> object:
        """Async init.

        Args:
            number (int): Number of the space.
            color (str): Color of the space.
            row (int): Row of the space.
            column (int): Column of the space.

        Returns:
            (object): Space object.
        """
        self.number = number
        self.color = color
        self.row = row
        self.column = column

        await self.calculate_neighbors()

        return self

    async def calculate_neighbors(self) -> None:
        """Calculate the neighbors to this space."""
        self.top = self.number - 3 if self.row > 1 else None

        self.topright = (
            self.number - 2 if self.column < 3 and self.row > 1 else None
        )

        self.right = self.number + 1 if self.column < 3 else None

        self.bottomright = (
            self.number + 4 if self.column < 3 and self.row < 12 else None
        )

        self.bottom = self.number + 3 if self.row < 12 else None

        self.bottomleft = (
            self.number + 2 if self.column > 1 and self.row < 12 else None
        )

        self.left = self.number - 1 if self.column > 1 else None

        self.topleft = (
            self.number - 4 if self.column > 1 and self.row > 1 else None
        )

    @property
    async def is_consecutive(self, num) -> bool:
        """Check if this space is consecutive with the given number.

        Args:
            num (int): Number to test.

        Returns:
            (bool): True if consecutive, False otherwise.
        """
        if num == self.space + 1 or num == self.space - 1:
            return True

        return False

    @property
    async def is_even(self) -> bool:
        """Check if this space is even.

        Returns:
            (bool): True if even, otherwise False.
        """
        return True if self.number % 2 else False


class Board(object):
    """Roulette Board."""

    def __init__(self) -> None:
        """Init."""
        super(Board, self).__init__()

    async def init(self) -> None:
        """Async init.

        Returns:
            (object): self.
        """
        self.black_spaces = [
            2,
            4,
            6,
            8,
            10,
            11,
            13,
            15,
            17,
            20,
            22,
            24,
            26,
            28,
            29,
            31,
            33,
            35,
        ]

        self.spaces = {}
        self.spaces[0] = await Space().init(0, 'green', 0, 0)

        row = 1
        column = 1
        for i in range(1, 37):
            color = 'black' if i in self.black_spaces else 'red'
            self.spaces[i] = await Space().init(i, color, row, column)

            if row % 3 == 0:
                row += 1

            if column == 3:
                column = 1
            else:
                column += 1

        return self


class Bet(object):
    """Bet object."""

    def __init__(self):
        """Init."""
        super(Bet, self).__init__()

    async def validate(self, number: Optional[int] = 0) -> bool:
        """Validate the number given.

        Args:
            number (int, optional): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        return True


class Straight(Bet):
    """Straight bet object."""

    def __init__(self):
        """Init."""
        super(Straight, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'straight'
        self.payout = 35

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        if number not in range(0, 36):
            await self.send_message('Your bet must be between 0-36.')
            return False

        return True

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if number == space.number else False


class Low(Bet):
    """Low bet object."""

    def __init__(self):
        """Init."""
        super(Low, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'low'
        self.payout = 1

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.number in range(1, 19) else False


class High(Bet):
    """High bet object."""

    def __init__(self):
        """Init."""
        super(High, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'high'
        self.payout = 1

        return self

    async def validate(self, number: Optional[int] = 0) -> bool:
        """Validate the number given.

        Args:
            number (int, optional): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        return True

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.number in range(19, 37) else False


class Even(Bet):
    """Even bet object."""

    def __init__(self):
        """Init."""
        super(Even, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'even'
        self.payout = 1

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.is_even else False


class Odd(Bet):
    """Odd bet object."""

    def __init__(self):
        """Init."""
        super(Odd, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'odd'
        self.payout = 1

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if not space.is_even else False


class Red(Bet):
    """Red bet object."""

    def __init__(self):
        """Init."""
        super(Red, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'red'
        self.payout = 1

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.color == 'red' else False


class Black(Bet):
    """Black bet object."""

    def __init__(self):
        """Init."""
        super(Black, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'black'
        self.payout = 1

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.color == 'black' else False


class Topline(Bet):
    """Topline bet object."""

    def __init__(self):
        """Init."""
        super(Topline, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'topline'
        self.payout = 6

        return self

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if space.number in range(0, 4) else False


class Street(Bet):
    """Street bet object."""

    def __init__(self):
        """Init."""
        super(Street, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'street'
        self.payout = 11

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        if number not in range(1, 13):
            await self.send_message('Your bet must be between 1-12.')
            return False

        return True

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if number == space.row else False


class Column(Bet):
    """Column bet object."""

    def __init__(self):
        """Init."""
        super(Column, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'column'
        self.payout = 2

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        if number not in range(1, 4):
            await self.send_message('Your bet must be between 1-3.')
            return False

        return True

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if number == space.column else False


class Dozen(Bet):
    """Dozen bet object."""

    def __init__(self):
        """Init."""
        super(Dozen, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'dozen'
        self.payout = 2

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        if number not in range(1, 4):
            await self.send_message('Your bet must be between 1-3.')
            return False

        return True

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        return True if number == int(space.number / 12) + 1 else False


class Split(Bet):
    """Split bet object."""

    def __init__(self):
        """Init."""
        super(Split, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'split'
        self.payout = 17

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        raise NotImplementedError()

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        raise NotImplementedError()


class Doublestreet(Bet):
    """Doublestreet bet object."""

    def __init__(self):
        """Init."""
        super(Doublestreet, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'doublestreet'
        self.payout = 5

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        raise NotImplementedError()

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        raise NotImplementedError()


class Corner(Bet):
    """Corner bet object."""

    def __init__(self):
        """Init."""
        super(Corner, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            (object): self.
        """
        self.type = 'corner'
        self.payout = 8

        return self

    async def validate(self, number: int) -> bool:
        """Validate the number given.

        Args:
            number (int): Number given by the player.

        Returns:
            (bool): True if the number is valid, otherwise False.
        """
        raise NotImplementedError()

    async def calculate_win(
        self, space: Space, number: Optional[int] = 0
    ) -> bool:
        """Calculate the win condition.

        Args:
            space (Space): Space landed on.
            number (int, optional): Number guessed by the player.

        Returns:
            (bool): True if the player wins, otherwise False.
        """
        raise NotImplementedError()


class RouletteCommand(BaseCommandPlugin):
    """Roulette plugin."""

    COMMAND = 'roulette'

    async def run(self) -> None:  # noqa
        """Roulette."""
        self.user = self.user
        if not self.command_args:
            await self.send_message(
                'You need to pick a bet (number, colour, etc.).'
            )
            return -1

        self.number = None

        self.board = await Board().init()

        self.bet_type = self.command_args[0]
        if not len(self.command_args) > 1:
            await self.send_message('Please ensure you have a bet amount.')
            return -1

        try:
            self.bet_ammount = int(self.command_args[-1])
        except ValueError:
            await self.send_message(
                'Please enter the bet first, then the bet amount.'
            )
            return -1

        self.bet_types = {
            'straight': Straight,
            'low': Low,
            'high': High,
            'even': Even,
            'odd': Odd,
            'red': Red,
            'black': Black,
            'topline': Topline,
            'street': Street,
            'column': Column,
            'dozen': Dozen,
            # 'split': Split,
            # 'doublestreet': Doublestreet,
            # 'corner': Corner,
        }

        try:
            self.number = int(self.bet_type)
            self.bet_type = 'straight'
        except ValueError:
            if self.bet_type.lower() not in self.bet_types:
                await self.send_message(
                    'Your bet must either be between 0-36 or one of the '
                    'following: '.format(', '.join(self.bet_types.keys()))
                )

        self.bet_type = self.bet_type.lower()

        if self.bet_type not in self.bet_types:
            await self.send_message(
                f'"{self.bet_type}" is not a valid bet type. '
                'Please see the instructions below.'
            )
            return -1

        if self.bet_type in ['street', 'column', 'dozen']:
            if len(self.command_args) < 3:
                await self.send_message(
                    '"Street" or "column" bets need a number and bet amount. '
                    'Eg. !roulette street 2 1000'
                )
                return -1

            try:
                self.number = int(self.command_args[1])
            except ValueError:
                await self.send_message(
                    '"Street", "column" or "dozen" bets need a number and bet '
                    'amount. Eg. !roulette street 2 1000'
                )
                return -1

        # Get the database data for the user.
        db_data = dict(
            await self.db.read('users', queries={'user_id': self.user['id']})
        )
        self.current_points = int(db_data['points'])

        if self.current_points <= 0:
            await self.send_message(
                'Looks like you have no points. Take these 100 and have fun!'
            )
            self.current_points = 100

        if self.bet_ammount > self.current_points:
            await self.send_message(f'You only have {self.current_points}.')
            return -1

        await self.let_it_roll()

    async def let_it_roll(self) -> None:
        """Do the spin and calculate the win."""
        spin = random.randint(0, 36)
        space = self.board.spaces[spin]
        color = self.board.spaces[spin].color
        bet = await self.bet_types.get(self.bet_type)().init()

        if not await bet.validate(self.number):
            return -1

        if await bet.calculate_win(space, self.number):
            winnings = self.bet_ammount * bet.payout
            message = f'You Win {winnings}!'
        else:
            message = 'Sorry, you lose.'

        await self.send_message(f'And the spin is: {spin}({color}): {message}')

        self.current_points += winnings
        await self.db.update(
            'users',
            {'points': self.current_points},
            {'user_id': self.user['id']},
        )
