"""Trivia plugin."""

from html import unescape

from random import shuffle

import server_utils

from init import CACHE
from plugins._base_plugins import BaseCommandPlugin


class TriviaCommand(BaseCommandPlugin):
    """Trivia plugin."""

    COMMAND = 'trivia'

    async def run(self) -> None:
        """Trivia questions provided by The Open Trivia Database."""
        if not self.command_args:
            await self.generate_question()
            return

        if self.command_args[0].lower() != 'answer':
            return -1

        await self.show_answer()

    async def generate_question(self) -> None:
        """Generate a question and cache the answer."""
        if await CACHE.exists('trivia'):
            await self.send_message(
                'Show the answer with "!trivia answer" before getting a new '
                'question.'
            )
            return -1

        url = 'https://opentdb.com/api.php'
        headers = {}
        params = {'amount': 1, 'type': 'multiple'}

        _, response = await server_utils.get_request(url, headers, params)
        results = response.get('results', [])
        if not results:
            return -1

        results = results[0]
        category = unescape(results.get('category'))
        difficulty = unescape(results.get('difficulty'))
        question = unescape(results.get('question'))
        correct_answer = unescape(results.get('correct_answer'))
        incorrect_answers = [
            unescape(i) for i in results.get('incorrect_answers')
        ]

        await CACHE.add('trivia', {'correct_answer': correct_answer})

        answers = incorrect_answers
        answers.append(correct_answer)
        shuffle(answers)
        answers_str = ', '.join(answers)

        msg = (
            f'Here\'s a {difficulty} question about {category}: {question} '
            f'{answers_str}'
        )

        await self.send_message(msg)

    async def show_answer(self) -> None:
        """Retrieve the answer from the cache and print it."""
        trivia_cache = await CACHE.get('trivia')
        if not trivia_cache:
            await self.send_message('No trivia running.')
            return -1

        correct_answer = trivia_cache.data.get('correct_answer')

        await self.send_message(f'The correct answer is: {correct_answer}.')

        await CACHE.delete('trivia')
