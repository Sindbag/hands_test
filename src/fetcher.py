import re
import logging

import aiohttp
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class PhoneFetcher:
    RU_PHONES_REGEX = r'\b(?!-)(?P<prefix>[7|8])?[\s\-]?\(?(?P<city>[0-9]{3})?\)?[\s\-]?' \
                      r'(?P<number>([0-9][\-\f ]?){5}[0-9]{2})(?!-)\b'

    def __init__(self, debug=False):
        self._rec = re.compile(PhoneFetcher.RU_PHONES_REGEX, re.MULTILINE)
        self.debug = debug

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=1500,
                limit_per_host=0,
                force_close=True)
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self._session.close()

    async def _fetch(self, url):
        async with self._session.get(url) as response:
            return await response.text()

    @staticmethod
    def get_text(html):
        _bs = BeautifulSoup(html, features="html.parser")
        # kill all script and style elements
        [script.extract() for script in _bs(["script", "style"])]
        # get text
        return _bs.get_text(separator=' ')

    def get_matches(self, text):
        if self.debug:
            logger.debug(text)
            print(text)
        matches = self._rec.finditer(text)
        res = set()
        for match in matches:
            gd = match.groupdict()
            res.add(
                '8{city}{number}'.format(
                    city=gd.get('city') or 495,
                    number=re.sub('[^0-9]', '', gd['number'])
                ).strip()
            )
        return res

    async def parse(self, sites):
        results = {}
        for url in sites:
            try:
                logger.info('Parsing %s...', url)
                html = await self._fetch(url)
                text = self.get_text(html)
                results[url] = self.get_matches(text)
            except Exception as err:
                logger.error(err)
        return results
