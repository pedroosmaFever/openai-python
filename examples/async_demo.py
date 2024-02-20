#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()


async def main() -> None:
    prompt = "Resumen crimen y castigo"

    stream = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens= 4096 - len(prompt.split())-100,
        stream=True,
    )
    async for completion in stream:
        print(completion.choices[0].text, end="")
    print()


asyncio.run(main())
