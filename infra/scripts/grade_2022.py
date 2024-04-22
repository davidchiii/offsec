#!/usr/bin/env python3
import argparse
from collections import defaultdict
import csv
import datetime
import dateutil.parser
import json
import glob
import os
from sys import exit

from ctfdbot import CtfdBot

WEEK_DEADLINES = {
    # EST is UTC-05:00, UTC-04:00 w/ daylight savings time
    1: "2022-09-17 4:00:00-05:00",
    2: "2022-02-07 19:00:00-05:00",
    3: "2022-09-27 18:00:00-05:00",
    4: "2022-10-04 18:00:00-05:00", # President's day on 02-21, no classes schewduled
    5: "2022-10-11 18:00:00-05:00", # Switched to 8pm ET starting the 28th
    6: "2022-10-18 18:00:00-05:00",
    7: "2022-10-21 20:00:00-04:00", # Midterm. Note: Daylight savings time starts 03-13
    8: "2022-10-28 20:00:00-04:00",
    9: "2022-10-04 20:00:00-04:00",
    10: "2022-10-11 20:00:00-04:00",
    11: "2022-10-18 20:00:00-04:00",
    12: "2022-10-25 20:00:00-04:00",
    13: "2022-10-02 20:00:00-04:00",
    14: "2022-10-09 20:00:00-04:00",
    15: "2022-10-16 20:00:00-04:00",
}
# Optional map of week -> name that shows up in NYU Classes
WEEK_NAMES = {
    14: "Master Challenge [100]",
    15: "Write Up [1]"
}

def parse_args():

    parser = argparse.ArgumentParser(
        description='Grade all assignments that have passed the solve deadline',
    )

    parser.add_argument(
        '--ctfd_url',
        type=str,
        default='http://localhost:4000',
        help='URL for CTFd',
    )

    parser.add_argument(
        '--chals_path',
        type=str,
        help='Path to the local challenges directory',
    )

    parser.add_argument(
        '--gradebook_path',
        type=str,
        help='Path to an up-to-date blank gradebook CSV. Expects a single column with student netIds',
    )

    return parser.parse_args()

def get_chals_by_week(chals_dir):
    chals = defaultdict(list)
    for chal_dir in sorted(glob.glob(os.path.join(chals_dir, 'week_*/*/'))):
        wk_num = int(chal_dir.split('/')[-3].split('_')[1])
        with open(os.path.join(chal_dir, 'challenge.json')) as chaljson:
            chal_metadata = json.load(chaljson)
            if chal_metadata['name'] == 'Are You Alive?':
                continue
            chals[wk_num].append(chal_metadata['name'])

    return chals

def main():
    args = parse_args()

    bot = CtfdBot(args.ctfd_url, '238b01236ebd1b7c0d48a3be2d7090f582f7575a')

    chals = list(bot.get_challenges())
    chals = {x['name']: x for x in chals}
    teams = list(bot.get_teams())
    teams = {x['name']: x for x in teams}
    for t in teams.values():
        t['solves'] = {x['id']: x for x in t['solves']}

    chals_by_week = get_chals_by_week(args.chals_path)

    with open(args.gradebook_path, 'r') as gradebook:
        reader = csv.reader(gradebook)
        headers = next(reader)
        students = [row for row in reader]

    for week, due_time in WEEK_DEADLINES.items():
        due_time = dateutil.parser.parse(due_time)

        # If this is a "valid" week to grade
        # NOTE: no, you can't just use utcnow because that returns a tz-naive datetime
        # because of course it does...
        if due_time < datetime.datetime.now(datetime.timezone.utc):
            # Add the column header
            #headers.append(WEEK_NAMES.get(week, f"Week {week} [100]"))
            chals_for_week = chals_by_week[week]

            # And calculate the pass/fail grade for each student
            for student_row in students:
                student_id = student_row[0]  # NetID
                points_for_week = 0

                if student_id not in teams:
                    continue

                # For each challenge in this week
                for chal_name in chals_for_week:
                    chalid = chals[chal_name]['id']

                    chal_due_time = due_time

                    """
                    Insert due-time overrides here that are more specific than the entire week
                    """

                    # If the student solved it...
                    if chalid in teams[student_id]['solves']:
                        student_solve_time = teams[student_id]['solves'][chalid]['date']
                        # ... before the due time
                        if dateutil.parser.parse(student_solve_time) <= chal_due_time:
                            #print(f"{student_id} solved {chal_name} before due date")
                            points_for_week += chals[chal_name]['value']
                        else:
                            #print(f"{student_id} solved {chal_name} AFTER due date ({student_solve_time})")
                            print("student solved after ddl")
                    else:
                        #print(f"{student_id} hasn't solved {chal_name}")
                        print("student hasn't solved chal")

                """
                Grade modifications due to cheating should go here
                """

                needed_points = 300

                """
                Adjustments to points needed based on week (e.g. midterm) should go here
                """

                #print(f"{student_id} has {points_for_week} points at end of week {week}\n")
                if week == 7:
                    if points_for_week >= needed_points:
                        student_row.append(str((points_for_week / 1000) * 100))
                    else:
                        student_row.append('0')
                    continue
                if week == 15:
                    if points_for_week >= 1:
                        student_row.append('1')
                    else:
                        student_row.append('0')
                    continue

                # Spr22 update: students get partial credit up to week's point threshold
                if points_for_week >= needed_points:
                    student_row.append(needed_points)
                else:
                    student_row.append(points_for_week)


    with open('grades.csv', 'w') as grades:
        writer = csv.writer(grades)
        writer.writerow(headers)
        for student in students:
            writer.writerow(student)

    return 0


if __name__ == '__main__':
    exit(main())
