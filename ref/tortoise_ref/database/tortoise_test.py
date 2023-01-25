#!/usr/bin/env python

"""Test of the Tortoise ORM."""
import asyncio
import traceback

from datetime import datetime

from tortoise.expressions import Q

from tortoise_init_test import init_db, close_db, LOG
from tortoise_model_test import Users

datetime_format = '%Y-%m-%d %H:%M:%S'


async def run():
    """Run some test code."""
    username = 'notarealuser'
    user_id = 9999999
    now = datetime.now().strftime(datetime_format)

    # Find the user by first match to username and user_id.
    found_user = await Users.first().filter(
        Q(username=username) & Q(user_id=user_id)
    )

    if found_user:
        LOG.info('Exiting task 1.')
        return

    # Try to create a new user.
    try:
        new_user = await Users.create(
            username=username,
            user_id=user_id,
            first_join_time=now,
            last_join_time=now,
        )
    except Exception:
        traceback.print_exc()

    # Print the new user.
    LOG.info(new_user)
    LOG.info('Exiting task 1.')


async def run2():
    """Compound query example."""
    # Query all data in a table with compound filtering.
    LOG.info(
        await Users.all()
        .filter(
            Q(Q(username__startswith='n') | Q(username__startswith='a'))
            & Q(is_banned=False)
        )
        .values('id', 'username')
    )
    LOG.info('Exiting task 2.')


async def run_tasks():
    await init_db()

    tasks = [asyncio.create_task(run()), asyncio.create_task(run2())]
    await asyncio.gather(*tasks)

    await close_db()


if __name__ == '__main__':
    asyncio.run(run_tasks())
