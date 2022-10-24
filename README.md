# Simple Asynchronous Web Scraper

This project uses [`Poetry`](https://python-poetry.org/) package manager.

## Overview

Script will asynchronously fetch list of provided urls

`urls = ["https://news.ycombinator.com/news?p=", "https://grahamcluley.com/page/"]`

You can provide page range as follows:

`asyncio.run(scrape(start_page=1, end_page=4))`

Asyncio's Semaphore is used to throttle coroutine concurrency:

`asyncio.Semaphore(5)`

Fetched data is saved as `.txt` files. Then script runs parsers for each website. Parsers located in `parsers.py`.

Parsed data is saved as `.csv` files.

## Run project

Install dependencies with

`poetry install`

Then you can run

`poetry run python3 main.py`