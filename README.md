RSSCurator
==========

Script for Curating an RSS Feed

See [this](http://greymeister.net/blog/2013/09/15/getting-rid-of-duplicates-in-the-hacker-news-feed/) blog post for more information.

### boto configuration:

Right now the script is kind of stupid and assumes you want to use S3 for persisting your feed.  This could
change later to allow some other options, but for now expect an error if you do not have your S3 credentials
configured, as specified here: [BotoConfig](http://code.google.com/p/boto/wiki/BotoConfig)

### Usage:

	$ ./run-curate.sh
	usage: ./curate.py feed_name_or_url

There is an example crontab line included if you would like to run the script periodically.  To avoid abuse of your
source URL, you should pick some number between 01 and 59 for the minutes to avoid slamming them.


### Todo

* Prune entries that are older than a month.
* Allow different persistence options.
* Allow list/multiple feeds from command line.