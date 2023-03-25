This is a set of simple Python programs that handles scheduling for a fantasy sports league.

The code is fairly specific to one particular league and one particular website (CBS Sports).
but hopefully it can be modified/generalized in the future if/when needs change.

I can't imagine anyone else wanting to use this code, but if so, feel free.

## Usage

Once the NHL schedule has been set for the season, there are four tasks that need to be done in order to finalize the
league schedule.

1) The "periods" need to be set up manually using the CBS website. (A "period" is the span of time during which one 
fantasy game happens).  This is typically going to follow rules similar to the following:
  - There are 17 periods during the regular season
  - There are 3 periods during the playoffs
  - Each period runs from Monday to Sunday, inclusive.
  - Each period is one week long, except for special periods at the beginning of the season and during the all-star break, which are two weeks.

2) Some code will need to be modified to handle any changes to team names, which teams are in which divisions, 
number of teams, which periods are "special", and so on.

3) The `generate_schedule.py` script should be run. This will generate the period-to-period "matchups" (in other words, which 
teams are playing which other teams). The resultant schedule will be saved in a file named `matchups.json`, and full details
will be printed out.  Check the output -- if anything is wrong, then modify the code and re-run the script until the
schedule is as desired.

4) The `set_matchups.py` script can then be run. This script will upload the schedule to the CBS site automatically.


## Setup

This code needs to run on a computer with Python 3.10 or higher, and the Chrome web browser.

In addition, the Python environment needs to have some libraries installed.  The libraries are specified in the 
`requirements.txt` file.  Python's `pip` utility can be told to read this file and install the needed libraries.
As always, it's recommended to install dependencies inside a Python "virtual environment", rather than as part of the 
system Python installation.

As of March 2023, there is a compatibility problem with `webbot`, one of the libraries we depend on. The problem is that
the latest version of `webbot` depends on an older version of `selenium`, but it does not declare that the newest version
of `selenium` will not work.  This bug in `webbot` should be fixed soon, but in the meantime, if the `set_matchup.py`
script errors out, you can try doing `pip uninstall selenium && pip install selenium==3.141.0`.
