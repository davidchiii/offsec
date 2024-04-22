from zipfile import ZipFile
import pandas as pd
import json
from datetime import datetime
from dateutil.parser import parse


def unzip(filename):
    with ZipFile(filename, "r") as zObject:
        zObject.extractall()
    zObject.close()


def process_files():
    # get all the users
    users = json.load(open("db/users.json"))
    users = pd.DataFrame(users["results"])
    all_users = users["name"].unique()

    # get all submissions
    submissions = json.load(open("db/submissions.json"))
    submissions = pd.DataFrame(submissions["results"])

    df = pd.merge(users, submissions, left_on="id", right_on="user_id")
    df = df.drop(
        columns=[
            "oauth_id",
            "password",
            "secret",
            "website",
            "affiliation",
            "country",
            "team_id_y",
            "bracket",
            "hidden",
            "verified",
            "created",
            "language",
        ]
    )
    return df, all_users


def main():
    # unzip export
    unzip("offsec-grades-02-01-2024.zip")
    df, all_users = process_files()

    due_dates = 




main()
