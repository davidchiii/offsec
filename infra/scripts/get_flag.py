#!/usr/bin/env python3

"""
This scripts will prompt you for a netid then ask you to pick a challenge.
It will give you the hash that will be added to the flag for that specific user and challenge.

* You will need to be on the osiris vpn for this to be able to connect to the database cluster *
"""

from hashlib import sha256
import pymysql.cursors

conn = pymysql.connect(
    host='db.int.isis.poly.edu',
    user='ctfclass',
    password='lZV0CU49sOWBQ7DvD37hiddIs6iGoVK',
    db='ctfclass',
    charset='utf8mb4',
    #cursorclass=pymysql.cursors.DictCursor
)

try:
    netid = input('enter netid: ')
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT name FROM challenges;'
        )
        challenge_names = list(map(
            lambda x: x[0],
            cursor.fetchall()
        ))
    for index, value in enumerate(challenge_names):
        print(index+1, ':', value)
    challenge = challenge_names[int(input('select challenge: '))-1]
    with conn.cursor() as cursor:
        cursor.execute(
            'select data from secrets join teams on teams.id = secrets.teamid where teams.name = %s;',
            (netid,)
        )
        secret=cursor.fetchone()[0]
        cursor.execute(
            'select flag from `keys` join challenges on challenges.id = `keys`.chal where challenges.name = %s;',
            (challenge,)
        )
        flag=cursor.fetchone()[0]
    hash=sha256((secret+challenge).encode()).hexdigest()[:12]
    print(flag.replace('<HASH>', hash))
finally:
    conn.close()
