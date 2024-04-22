# Spring '22 Documentation

## Uploading Challenges
...

## Updating Challenges on CTFd
...

## Grading

### Initial Setup

1. [x] Copy the most recent grade script and updates dates & times for the semester
2. [x] Create a clean csv gradebook for the script to populate
    - Name it something unique to the semester (e.g. spr22_grades_clean.csv)
    - Single column with header of "Student"
    - Include student netIDs from Brightspace classlist, one per line (note: it will really help to mirror the classlist order when entering grades)
3. [x] Create a tracker (Excel, etc.) to track cheaters
    - Student to who shared their flag
    - Student who submitted the shared flag
    - Challange
    - Flag shared

### Running Weekly Grades

1. Copy your clean gradebook csv into a new csv called `grades.csv`
    - The grade script looks for this specific filename
    - The grade book needs to be empty (e.g. just the list of netIDs)
2. Run the grading script
    - 3 script takes 3 parameters: ctfd url, the local challenge path on your machine, and the gradebook
        - `--ctfd_url https://class.osiris.cyber.nyu.edu` 
        - `--chals_path ../../chals`
        - `--gradebook grades.csv`
    - An audit of if the student had solved each challenge per week before or after the deadline will be output to stdout (it may be helpful to direct this into an audit text file, `> week5_audit.txt`)
    - Calculated scores for each week up to the current will be written to the csv, comma separated per week
3. Rename `grades.csv` to reflect week name (e.g. `grades_week3.csv`)

### Check for Cheating

1. Check cheat alerts for any flag shares for the previous week's challenges
2. Add to cheat tracker along and note challenge point totals

### Enter Grades in Brightspace

1. Navigate to the Grades tab
2. Enter grades from grades csv
3. Adjust grades for cheatering
    - Both flag sharers and submitters should be docked the points of the challenge
    - Take the student's calculated grade total from the script and subtract the challenge points (e.g. if had 300 total and cheated on a 100 point challenge, student would get 200 for the week) 