"""
Simple asynchronous web scraper
"""

import os
from typing import Callable
from urllib.parse import urlparse

import asyncio
import aiofiles
import aiofiles.os
import aiohttp

import pandas as pd

from parsers import ycombinator_parser, grahamcluley_parser


HTML_DIR = "raw_data/"
PARSED_DATA = "parsed_data/"

urls = ["https://news.ycombinator.com/news?p=", "https://grahamcluley.com/page/"]


def create_dir(dir_name: str) -> str:
    """Create new directory if doesn't exist"""
    if os.path.isdir(dir_name):
        print(f"Directory {dir_name} already exists")
    else:
        os.mkdir(dir_name)

    return dir_name


async def fetch(url: str, session: aiohttp.ClientSession) -> bytes:
    """Asynchronously fetch provided url"""
    async with session.get(url) as response:
        return await response.read()


async def fetch_and_save(
    sem: asyncio.Semaphore,
    url: str,
    page: int,
    dir_name: str,
    session: aiohttp.ClientSession,
) -> None:
    """Calls `fetch` function and saves result to txt file"""
    async with sem:
        result = await fetch(url, session)

    async with aiofiles.open(dir_name + "/" + str(page) + ".txt", mode="wb") as file:
        await file.write(result)


async def scrape(start_page: int = 1, end_page: int = 1) -> None:
    """Creates asyncio tasks to fetch provided urls"""
    if start_page < 1 or end_page < 1:
        raise ValueError("Page numbers must be >= 1")

    tasks = []

    # Semaphore
    sem = asyncio.Semaphore(5)

    headers = {
        "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:

            # Creates directory based on domain name from url
            dir_name = create_dir(HTML_DIR + urlparse(url).netloc)

            for page in range(start_page, end_page + 1):
                full_url = url + str(page)
                tasks.append(
                    asyncio.create_task(
                        fetch_and_save(sem, full_url, page, dir_name, session)
                    )
                )

        await asyncio.gather(*tasks)


def parse_and_save(
    dir_path: str, out_file_path: str, parser: Callable[[bytes], pd.DataFrame]
) -> None:
    """Calls provided `parser` function and saves results to csv file"""

    for fpath in sorted(os.listdir(dir_path), key=(lambda x: int(x.split(".")[0]))):
        with open(dir_path + fpath, mode="rb") as file:
            data_frame = parser(file.read())

            # Append without headers if csv file already exists
            if not os.path.isfile(out_file_path):
                data_frame.to_csv(out_file_path, index=False)
            else:
                data_frame.to_csv(out_file_path, mode="a", index=False, header=False)


if __name__ == "__main__":

    # Create necessary directories
    create_dir(HTML_DIR)
    create_dir(PARSED_DATA)

    # Run main scrape function
    asyncio.run(scrape(end_page=4))

    ycomb_path = HTML_DIR + "news.ycombinator.com/"
    ycomb_out_path = PARSED_DATA + "ycombinator.csv"

    # Parse news.ycombinator.com data
    parse_and_save(ycomb_path, ycomb_out_path, ycombinator_parser)

    gc_path = HTML_DIR + "grahamcluley.com/"
    gc_out_path = PARSED_DATA + "grahamcluley.csv"

    # Parse grahamcluley.com data
    parse_and_save(gc_path, gc_out_path, grahamcluley_parser)
