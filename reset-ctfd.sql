-- Reset offsec ctfd. Will delete all non-admin teams.
-- ** They will delete all the teams that are not admin **

delete from cached_generated_files;
delete secrets from secrets join teams on teams.id = secrets.teamid where teams.admin != 1;
delete tracking from tracking join teams on tracking.team = teams.id where teams.admin != 1;
delete solves from solves;
delete wrong_keys from wrong_keys join teams on wrong_keys.teamid = teams.id where teams.admin != 1
delete from teams where admin != 1;
delete from `keys`;
delete from `tags`;
delete from `files` where chalid IS NOT NULL;
delete from `challenges`;
