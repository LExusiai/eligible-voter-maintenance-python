# -*- coding: utf-8 -*-
from pywikibot import Page, Site
import os
import pymysql

def get_voter_list_from_database(timestamp: str, b_timestamp: str) -> list[str]:
    voter_list: list[str] = []

    conn = pymysql.connect(
        host=os.environ['WIKIMEDIADBHOST'],
        user=os.environ['TOOL_REPLICA_USER'],
        password=os.environ['TOOL_REPLICA_PASSWORD'],
        database=os.environ['WIKIMEDIADBNAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

    query = '''
	SELECT u.user_name as username
	FROM user u
	INNER JOIN actor a ON u.user_id = a.actor_user
	INNER JOIN(
	SELECT r.rev_actor, COUNT(*) as recent_edits
	FROM revision_userindex r
	INNER JOIN page p ON r.rev_page = p.page_id
	WHERE r.rev_timestamp >= %(start_time)s
		AND r.rev_timestamp <= %(time)s
		AND p.page_namespace NOT IN (2, 3)
	GROUP BY r.rev_actor
	HAVING recent_edits >= 10
	) recent ON a.actor_id = recent.rev_actor
	WHERE
		(u.user_registration IS NULL OR u.user_registration <= %(start_time)s)
		AND u.user_is_temp = 0
		AND u.user_editcount >= 500
		AND u.user_id NOT IN (
			SELECT ug.ug_user
			FROM user_groups ug
			WHERE ug.ug_group = 'bot'
		)
		AND u.user_name NOT LIKE 'Renamed user %'
	ORDER BY u.user_name;
'''

    with conn:
        with conn.cursor() as cursor:
            paras: dict = {
                "start_time": timestamp,
                "time": b_timestamp
            }
            db_result = cursor.execute(query, paras)
            db_result = cursor.fetchall()

            for i in db_result:
                voter_list.append(i["username"])

            return voter_list

def get_voter_list_from_wikipedia() -> list[str]:
    site = Site('wikipedia:zh')
    main_list_page = Page(site, os.environ['MAINLISTPAGENAME'])
    voter_list_from_wikipedia: list[str] = main_list_page.text.splitlines()
    return voter_list_from_wikipedia[2:-1]

def get_new_election() -> list[tuple[int, str, str]]:
    conn = pymysql.connect(
        host=os.environ['BOTDBHOST'],
        user=os.environ['TOOL_TOOLSDB_USER'],
        password=os.environ['TOOL_TOOLSDB_PASSWORD'],
        database=os.environ['BOTDBNAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

    query = "SELECT election_id, timestamp, b_timestamp FROM secure_poll WHERE status = 'uncheck'; "
    with conn:
        with conn.cursor() as cursor:
            db_result: int = cursor.execute(query)
            result = cursor.fetchall()
            return [
                (i["election_id"], i["timestamp"], i["b_timestamp"])
                for i in result
            ]

def mark_election(election_id: int, status: str) -> int:
    conn = pymysql.connect(
        host=os.environ['BOTDBHOST'],
        user=os.environ['TOOL_TOOLSDB_USER'],
        password=os.environ['TOOL_TOOLSDB_PASSWORD'],
        database=os.environ['BOTDBNAME'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

    query = "UPDATE secure_poll SET status = %(status)s WHERE election_id = %(election_id)s;"
    with conn:
        with conn.cursor() as cursor:
            result = cursor.execute(query, {
                "election_id": election_id,
                "status": status,
            })

            return result