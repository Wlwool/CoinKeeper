import asyncio
from bot.bot import TelegramBot


async def main():
    app = TelegramBot()
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
