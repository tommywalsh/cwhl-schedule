# This program generates a schedule for a fantasy sports league with the following constraints:
# - Two divisions, each with five teams
# - Each team plays three games against each of the other teams in its division.
# - Each team plays one game against each team in the other division
# - Each team plays one game every "week". Thus, there are 17 weeks.
# - There are two "weird" weeks that last longer than 7 days. These should have only non-divisional games
# - So, there need to be a total of 25 non-division games and 60 in-division games.
#
# The general strategy is:
# - We'll have two "weird" weeks, each with 5 non-divisional games
# - There will be 15 "normal" weeks, each with 4 divisional games, and 1 non-divisional game
#   - The normal weeks are broken up into three groups of five weeks.
#   - Each group's games are generated by the modified round-robin algorithm described below
#
# Modified round-robin algorithm for each division:
# - Imagine five team captains (named A B C D and E) sitting at a round table, in that order.
# - Each week we assign games like so:
#   - One team is chosen to play a non-division team.  The first week, this is team A.
#   - The first in-division game has the teams immediately to the left and right of the chosen team (1st week: B and E)
#   - The remaining two teams also play an in-division game (first week: C and D)
# - Each following week, the chosen team changes.
#   - So the second week has (C vs A) and (D vs E), then (B vs D) and (A vs E), and so on.
# - Once we complete one trip through this for five weeks, we repeat.
#   - The second time through this works the same way, but the home/away teams are swapped.
#   - The third time through is the same as the first.
#
# Each teams schedule looks like this:
#   - 3 games against each division opponent
#      - 6 home games and 6 away games
#      - 2 home, 1 away against two of the division opponents
#      - 1 home, 2 away against the other two division opponents
#   - 1 game each against non-division opponents (5 total)
#      - One division's teams will have 3 home games and 2 away games
#      - The other division will have 2 home and 3 away


# League-specific data
wales = ["Steamers", "Army", "Breakfast Kings", "Loonies", "Magoons"]
campbell = ["Pleased", "Zaus", "Poachers", "Pants", "Cold Necks"]


# Convenience class representing one single game
class Game:
    def __init__(self, home, away, title=None):
        self.home = home
        self.away = away
        self.title = title


# Convenience class representing information about a single team's schedule
# Useful for sanity checking that each team's schedule is as expected.
class TeamReport:
    def __init__(self):
        self.home = 0
        self.total = 0
        self.in_division = 0
        self.opponents = set()

    def augment_with_game(self, is_home, is_in_division, opponent):
        if is_home:
            self.home += 1
        if is_in_division:
            self.in_division += 1
        self.total += 1
        self.opponents.add(opponent)


# Convenience class representing information about all team's schedules
# Useful for sanity checking that each team's schedule is as expected.
class Report:
    def __init__(self, division1):
        self.by_team = {}
        self.wales = division1

    def _is_same_division_game(self, game):
        return (game.home in self.wales) == (game.away in self.wales)

    def _add_game_info_for_team(self, team, is_home, is_same_division, other_team):
        if team not in self.by_team:
            self.by_team[team] = TeamReport()
        self.by_team[team].augment_with_game(is_home, is_same_division, other_team)

    def add_game(self, new_game):
        is_same = self._is_same_division_game(new_game)
        self._add_game_info_for_team(new_game.home, True, is_same, new_game.away)
        self._add_game_info_for_team(new_game.away, False, is_same, new_game.home)


# Convenience function to help with toggling which team is home and which is away
def get_game_with_home_away_parity(team1, team2, parity):
    home = team1 if parity else team2
    away = team2 if parity else team1
    return Game(home, away)


# Implements one round of the round-robin algorithm described above
# Toggling the "parity" argument will change which team is home vs. away
def get_round_robin_pairs(all_teams, sitout_team_index, parity):
    num_teams = len(all_teams)
    assert(num_teams % 2 == 1)
    num_pairs = int((num_teams - 1) / 2)
    games = []
    for pair_index in range(0, num_pairs):
        team1_index = (sitout_team_index + pair_index + 1) % num_teams
        team2_index = (sitout_team_index - pair_index - 1) % num_teams
        game = get_game_with_home_away_parity(all_teams[team1_index], all_teams[team2_index], parity)
        games.append(game)
    return games


# Uses round-robin algorithm to generate a full slate of games for a "normal" week
# week_num is used to choose which team from division 1 plays non-divisionally
# division_offset is used to choose which team from division 2 plays non-divisionally
# parity toggles the rules for which teams are home and away
def generate_games_for_normal_week(week_num, division1, division2, division_offset, parity):
    teams_per_division = len(division1)
    assert(teams_per_division % 2 == 1)
    assert(len(division1) == len(division2))

    games = []

    # A normal week has one non-divisional game
    team1_nondiv_index = week_num % teams_per_division
    team2_nondiv_index = (team1_nondiv_index + division_offset) % teams_per_division
    nondiv_game = get_game_with_home_away_parity(division1[team1_nondiv_index], division2[team2_nondiv_index], parity)
    games.append(nondiv_game)

    # Each division also has their own in-division games.
    games.extend(get_round_robin_pairs(division1, team1_nondiv_index, parity))
    games.extend(get_round_robin_pairs(division2, team2_nondiv_index, parity))

    return games


# Prints out statistics about team schedules, to make sure we don't have any glaring errors
def do_sanity_check(all_weeks, division1):
    report = Report(division1)

    for week in all_weeks:
        for game in week["games"]:
            report.add_game(game)

    print("Sanity check:")
    for team in report.by_team:
        info = report.by_team[team]
        opps = len(info.opponents)
        print(f"{team}: home: {info.home}, in_div: {info.in_division}, opps: {opps}; total {info.total}")


# Generates a full slate of games for a "weird" week
def generate_games_for_weird_week(week, division1, division2):
    assert (len(division1) == len(division2))
    teams_per_division = len(division1)
    parity = (week % 2) == 1

    games = []

    # Weird weeks feature only non-division games. We just pair the teams up one-by-one,
    # In the first week, we match up the first team in one division with the first in the other, and so on.
    # In the second week, we match the first team in one to the SECOND in the other, and so on.
    for wales_index in range(0, teams_per_division):
        campbell_index = (wales_index + week) % teams_per_division
        team1 = division1[wales_index]
        team2 = division2[campbell_index]
        games.append(get_game_with_home_away_parity(team1, team2, parity))
    return {
        "title": f"Weird Week #{week + 1}",
        "games": games
    }


def generate_all_weeks(divison1, division2):

    # We want two weird weeks (with the divisions being offset by 0 then 1)...
    all_weeks = [
        generate_games_for_weird_week(0, divison1, division2),
        generate_games_for_weird_week(1, divison1, division2)
    ]

    # ...and three sets of five normal weeks, with the divisions offset by 2 then 3 then 4 in each set.
    for set_number in range(0, 3):
        # Flop the parity between sets, so that the second set's home/away is the opposite of the 1st and 3rd.
        parity = set_number % 2 == 1

        # Each set will have five weeks
        for week in range(0, 5):
            all_weeks.append({
                "title": f"Normal Week #{set_number*5 + week + 1}",
                "games": generate_games_for_normal_week(week, divison1, division2, 2 + set_number, parity)
            })

    return all_weeks


def print_full_report(all_weeks, division1, division2):

    # Print out a sanity check at the top so that we know if something is wrong.
    do_sanity_check(all_weeks, division1)

    # Do a week-by-week output of all the games
    print("\n\n")
    for week in all_weeks:
        print(f"{week['title']}")
        for game in week["games"]:
            print(f"  {game.away} at {game.home}")

    # Print out each team's individual schedule
    print("\n\n")
    for team in division1 + division2:
        print(f"##### {team} #####")
        for week in all_weeks:
            for game in week["games"]:
                if game.home == team or game.away == team:
                    print(f"  {week['title']}: {game.away} at {game.home}")


def main(division1, division2):
    all_weeks = generate_all_weeks(division1, division2)
    print_full_report(all_weeks, division1, division2)


if __name__ == "__main__":
    main(wales, campbell)
