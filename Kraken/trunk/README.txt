Intro
=================================

Kraken is a (currently very simple) mailing list manager. The basic principle is
that we are going to leverage an already existing IMAP/SMTP server. No need to
mess with Exim as in Mailman, e.g. We are just another IMAP client.

The beauty of using IMAP for mailing list/discussion mgmt is the modularity and
the flexibility. I can login w/ Thunderbird or a TTW client and manage the
archives and sift through the trash. I can use any old IMAP host on the Net, or
I can run my own Cyrus server and serve the list as nntp too (no need for
gmane!). Will it scale? Why not?



Install
=================================

Prerequisites:

    1. An IMAP account with these three mailboxes: INBOX, Archive, Limbo

    2. An SMTP account

    3. Python (only tested with 2.3.4)

    4. The runner script is *nix style (no .bat file yet)

    5. cron if you want to run it cronishly


Here's how to install Kraken:

    1. Checkout or export the Kraken package from:

        https://svn.zetadev.com/repos/public/Kraken

    2. Every directory is a mailing list; cp example/ to make your own (note
       that the example directory itself will be ignored, so it is safe to keep
       around for reference).

    3. Customize the conf files in your new list directory (instructions are
       in-line).

    4. cp release_the_kraken.py.example release_the_kraken.py

    5. Set the Kraken lair in release_the_kraken.py to the absolute path of your
       package

    6. Use release_the_kraken.py to, well, release the Kraken. ;-)

    7. When your setup is working, add release_the_kraken.py to your crontab.




List Types
=================================

Kraken currently implements two types of lists:

    - private discussion -- all addresses in send_to.addrs may post, plus
      those addresses explicitly named in accept_from.addrs

    - announcement list -- only addresses specifically named in the
      accept_from.addrs may post to the list




Roadmap
=================================

See Zeta's release management process for details. The plan here is to keep this
product w/in Zeta until at least 0.6. We will only have one production instance.

0.2 -- My initial use case was a 5-10 person members-only list, and this is just
about the simplest solution for my requirements.

0.4 -- new use case: announcement list (do not accept from send_to)

0.6 -- see TODO.txt



History
=================================

0.4 - switched from Trash to Limbo

    - abstracted conf from Kraken.py so we can use one Kraken to run multiple lists

    - added list type to kraken.conf

    - implemented announcement list

0.2 - did initial implementation



Author
=================================

Chad Whitacre
chad at zetaweb . com
whit537 on irc.freenode.net



License
=================================

Borrowed from Poul-Henning Kamp[1] 'cause it looks like fun:

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE":
# <chad@zetaweb.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. --Chad Whitacre
# ----------------------------------------------------------------------------


[1] http://people.freebsd.org/~phk/
