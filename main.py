# -*- coding: utf-8 -*-

from pywikibot import Site, Page
import datetime as dt
import asyncio
import os
import database

# 主列表的election id是0，安全投票的id自第一个由机器人维护的安全投票起
# 是1，一般选举的election id是投票页面的页面id，不过这个有jimmy xu老师的脚本
# 就不写了。
def update_list(election_id: int, timestamp: str, b_timestamp: str) -> bool:
    page_preload = ""

    if election_id == 0:
        site = Site('wikipedia:zh')
        site.login()
        main_list_page = Page(site, os.environ['MAINLISTPAGENAME'])
        voter_list_from_database: list[str] = database.get_voter_list_from_database(timestamp, b_timestamp)

        voter_list_text = "\n".join(voter_list_from_database)
        main_list_page.text = page_preload + voter_list_text
        main_list_page.save(summary="机器人自动更新清单")

        if database.get_voter_list_from_wikipedia() == voter_list_from_database:
            return True
        else:
            return False
    else:
        list_prefix: str = os.environ['LISTPREFIX']
        site = Site('wikipedia:zh')
        site.login()
        list_page = Page(site, list_prefix + str(election_id))
        list_page.text = page_preload + "\n".join(database.get_voter_list_from_database(timestamp, b_timestamp))
        list_page.save(summary="机器人自动创建新列表")
        return True

async def check_main_list_update() -> None:
    while True:
        time_period = dt.timedelta(days=180)
        start_time = dt.date.today() - time_period

        b_timestamp: str = dt.date.today().strftime('%Y%m%d%H%M%S')
        timestamp: str = start_time.strftime('%Y%m%d%H%M%S')

        latest_main_list: list[str] = await asyncio.to_thread(database.get_voter_list_from_database, timestamp, b_timestamp)
        if latest_main_list != await asyncio.to_thread(database.get_voter_list_from_wikipedia):
            update: bool = await asyncio.to_thread(update_list, 0, timestamp, b_timestamp)
            if update:
                print("200")
            else:
                print("warning: updating main list")
                await asyncio.sleep(43200)
        else:
            await asyncio.sleep(43200)

async def check_sub_list_update() -> None:
    while True:
        new_election_list: list[tuple[int, str, str]] = await asyncio.to_thread(database.get_new_election)
        if new_election_list:
            for election in new_election_list:
                b_timestamp: str = dt.date.today().strftime('%Y%m%d%H%M%S')
                update: bool = await asyncio.to_thread(update_list, election[0], election[1], b_timestamp)
                if update:
                    print("OK")
                else:
                    print("Error")
        else:
            await asyncio.sleep(10)

async def main():
    await asyncio.gather(
        check_main_list_update(),
        check_sub_list_update()
    )

if __name__ == "__main__":
    asyncio.run(main())