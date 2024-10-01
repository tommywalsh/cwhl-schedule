# This program uploads a season's worth of matchups to the CWHL site
#
# It reads a file called `matchups.json`, which is created by the `generate_schedule.py` program.
#
# It then opens an instrumented web browser, and uses it to log into the CWHL site. Then it walks through all of the
# various clicking and selecting that needs to be done in order to enter the matchups for the whole season.
#
# This program requires there to be a file called `CWHL_CREDENTIALS.json` that contains the username and password
# for accessing commissioner mode for the league.
import argparse
import json
import urllib.parse
import time
from selenium import webdriver

CRED_FILENAME = "CWHL_CREDENTIALS.json"
MATCHUPS_FILENAME = "matchups.json"
CBS_LOGIN_URL = "https://www.cbssports.com/login"
CWHL_BASE_URL = "https://baio.hockey.cbssports.com/"


def read_json_file(filename):
    with open(filename) as json_file:
        return json.loads(json_file.read())


def read_site_credentials():
    try:
        return read_json_file(CRED_FILENAME)
    except:
        raise ValueError("No valid credentials file found!\nPlease create a text file named {} ".format(CRED_FILENAME) +
                         "whose contents look like this:\n" +
                         '{\n  "userid": "your-user-name-here",\n  "password": "your-password-here"\n}\n')


def read_matchups():
    return read_json_file(MATCHUPS_FILENAME)


def find_dropdown(driver, desired_id):
    dropdowns = driver.find_elements_by_tag_name("select")
    assert len(dropdowns) == 1
    dropdown = dropdowns[0]
    assert dropdown.get_attribute("id") == desired_id
    return dropdown


def find_option_in_dropdown(dropdown, option_text):
    items = dropdown.find_elements_by_tag_name("option")
    for item in items:
        if item.text == option_text:
            return item
    assert False


def choose_team_for_game(driver, team_name, game_number, is_home):
    # Find the correct dropdown, then find the correct team in that dropdown, then click on the team
    dropdown_id = "dropdown:{}:{}".format(game_number,  "home" if is_home else "away")
    dropdown = driver.find_element_by_id(dropdown_id)
    option = find_option_in_dropdown(dropdown, team_name)
    option.click()


def choose_teams_for_game(driver, home_team, away_team, game_number):
    choose_team_for_game(driver, home_team, game_number, is_home=True)
    choose_team_for_game(driver, away_team, game_number, is_home=False)


def choose_teams_for_games(driver, matchups):
    game_number = 1
    for matchup in matchups:
        choose_teams_for_game(driver, home_team=matchup["home"], away_team=matchup["away"], game_number=game_number)
        game_number += 1


def url_with_params(base_url, param_spec):
    param_strings = []
    for key in param_spec:
        param_string = "{}={}".format(urllib.parse.quote(key), urllib.parse.quote(param_spec[key]))
        param_strings.append(param_string)
    full_param_string = "&".join(param_strings)
    full_url = "{}?{}".format(base_url, full_param_string)
    return full_url


def bot_login(driver, credentials):
    params = {
        "product_abbrev": "mgmt",
        "xurl": CWHL_BASE_URL,
        "master_product": "40581"
    }
    login_url = url_with_params(CBS_LOGIN_URL, params)
    driver.get(login_url)

    name_field = driver.find_element_by_name("email")
    name_field.send_keys(credentials["userid"])

    pw_field = driver.find_element_by_name("password")
    pw_field.send_keys(credentials["password"])

    all_buttons = driver.find_elements_by_tag_name("button")
    continue_buttons = [x for x in all_buttons if x.text == "Continue"]
    assert len(continue_buttons) == 1
    continue_button = continue_buttons[0]
    continue_button.click()

    time.sleep(60)  # Hack to wait for login to complete


def choose_period(driver, week_number):
    dropdown = driver.find_element_by_id("period")
    all_options = dropdown.find_elements_by_tag_name("option")

    # Assumption: the options are always returned in top-to-bottom order
    index = week_number - 1
    all_options[index].click()


def set_matchups(driver, all_matchups, is_dryrun=True):

    week_number = 1
    for week_matchups in all_matchups:
        driver.get("https://baio.hockey.cbssports.com/setup/commish-tools/schedule-edit")

        choose_period(driver, week_number)
        choose_teams_for_games(driver, week_matchups)

        if not is_dryrun:
            ok_button = driver.find_element_by_name("_submit")
            ok_button.click()
            time.sleep(5)  # Hack to wait for submission to complete
        week_number += 1


def set_all_matchups(is_dryrun):
    credentials = read_site_credentials()
    all_matchups = read_matchups()
    driver = webdriver.Firefox()
    bot_login(driver, credentials)
    set_matchups(driver, all_matchups, is_dryrun)


options = {
    "dryrun": True
}


def no_dry_run():
    options["dryrun"] = False


if __name__ == "__main__":
    spiel = """
    Upload schedule to CWHL site.
    
    Note that by default this merely simulates an update.
    To do a real update, you must pass the --no-dry-run option.
    """
    parser = argparse.ArgumentParser(description=spiel)
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction, help="Perform simulation only",
                        default=True)
    args = parser.parse_args()
    set_all_matchups(args.dry_run)
