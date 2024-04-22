Generated Challenge Plugin
--------------------------

This plugin does 2 main things:

1. It provides a mechanism for generating challenges and flags per-user. Look at the docstrings in `generate.py` for details.
2. It detects cheaters who use other teams' generated flags.

To setup the plugin, copy the files in `templates/admin` into your admin theme under `ctfd/CTFd/themes/admin/static/js/templates/challenges/`, then do the same for `templates/user` into `ctfd/CTFd/themes/<theme>/static/js/templates/challenges/`. Yes, it's overcomplicated.

To setup reporting to a Slack channel, create a webhook at [https://api.slack.com/incoming-webhooks](https://api.slack.com/incoming-webhooks), and setup the `SLACK_WEBHOOK_URL` in your config table (something like `INSERT INFO config (key, value) VALUES ('SLACK_WEBHOOK_URL', '<webhook_url>');`. Again, it's a bit overcomplicated, sorry.

Now, you can just upload your files, and the one called `gen` will be executed and the files printed to stdout will be served to the user.

Have fun!
