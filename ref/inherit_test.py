#!/usr/bin/env python

import asyncio


class Base(object):
    def __init__(self):
        """Init."""
        super(Base, self).__init__()

    async def init(self, a: str, b: str, c: str) -> object:
        self.a = a
        self.b = b
        self.c = c

        return self

    async def _run(self):
        await self.run()

    async def run(self):
        pass


class Parent(Base):

    VAR = 'var'


class Child(Parent):
    async def run(self):
        print(self.a, self.VAR)


async def main():
    a = 'test'
    b = ''
    c = ''

    child = await Child().init(a, b, c)
    await child._run()


if __name__ == '__main__':
    asyncio.run(main())
