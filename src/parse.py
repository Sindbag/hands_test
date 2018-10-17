from __future__ import absolute_import

import sys
import asyncio

from fetcher import PhoneFetcher


def read_data(file):
    with open(file) as f:
        return (l.strip() for l in f.readlines())


async def main():
    if len(sys.argv) < 2:
        raise Exception('File not provided!\nUsage example: ./parse.py path/to/urls/list\n')
    data = read_data(sys.argv[-1])
    async with PhoneFetcher() as fetcher:
        print(await fetcher.parse(data))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
