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

2) On the CBS website, teams need to be manually assigned to conferences. This changes every year, based on last year's final standings.

3) Some code will need to be modified to handle any changes to team names, which teams are in which divisions, 
number of teams, which periods are "special", and so on.
  - Inside `teams.py`, change team names as necessary (if any teams have had their names changed since last year)
  - Inside `teams.py`, change the `interdivisional_periods` to reflect this year's schedule
  - Inside `generate_schedule.py`, update the `wales` and `campbell` arrays to match this year's conference makeups.

4) The `generate_schedule.py` script should be run. This will generate the period-to-period "matchups" (in other words, which 
teams are playing which other teams). The resultant schedule will be saved in a file named `matchups.json`, and full details
will be printed out.  Check the output -- if anything is wrong, then modify the code and re-run the script until the
schedule is as desired.  A Python virtual environment can/should be used to run this command:
    `python generate_schedule.py`

5) The `set_matchups.py` script can then be run. This script will upload the schedule to the CBS site automatically.
By default, this will run in `dry-run` mode, which will make changes on the screen, but will not actually save them.
When you're ready to run this for real, pass the `--no-dry-run` argument to the script.
The script will pop up a Firefox-based web browser, and you should see the following happen:
   - It will log in
   - It will then pause for about a minute. If the login did not work (e.g. due to a captcha problem), you can manually log in during this 1 minute pause
   - It will walk through all of the weekly matchup, gradually choosing which teams play which other teams.

6) Manually check each team's schedule, just to make sure there were no problems with the automatic process


## Setup

This code needs to run on a computer with Python 3.10 or higher.

The computer also has to have the Firefox webbrowser installed, along with the `geckodriver` utility (which allows Firefox to be controlled programmatically).
On an Ubuntu Linux system, this can be installed with `sudo apt-get install firefox-geckodriver`

It's highly recommended to do all work inside a Python "virtual environment". This will insulate the system's Python installation from our requirements.

Our Python virtual environment needs to have some libraries installed.  The libraries are specified in the 
`requirements.txt` file.  Python's `pip` utility can be told to read this file and install the needed libraries with `pip -r requirements.txt`

