import asyncio

from lib.db import init_database


async def main() -> None:
    await init_database()
    print("Seeded PostgreSQL demo accounts and opportunities")


if __name__ == "__main__":
    asyncio.run(main())