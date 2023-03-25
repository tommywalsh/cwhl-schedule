import json
import urllib.parse
import webbot

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


def find_dropdown(browser, desired_id):
    dropdowns = browser.find_elements(tag="select", id=desired_id)
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


def choose_team_for_game(browser, team_name, game_number, is_home):
    # Find the correct dropdown, then find the correct team in that dropdown, then click on the team
    dropdown_id = "dropdown:{}:{}".format(game_number,  "home" if is_home else "away")
    dropdown = find_dropdown(browser, dropdown_id)
    option = find_option_in_dropdown(dropdown, team_name)
    option.click()


def choose_teams_for_game(browser, home_team, away_team, game_number):
    choose_team_for_game(browser, home_team, game_number, is_home=True)
    choose_team_for_game(browser, away_team, game_number, is_home=False)


def choose_teams_for_games(browser, matchups):
    game_number = 1
    for matchup in matchups:
        choose_teams_for_game(browser, home_team=matchup["home"], away_team=matchup["away"], game_number=game_number)
        game_number += 1


def url_with_params(base_url, param_spec):
    param_strings = []
    for key in param_spec:
        param_string = "{}={}".format(urllib.parse.quote(key), urllib.parse.quote(param_spec[key]))
        param_strings.append(param_string)
    full_param_string = "&".join(param_strings)
    full_url = "{}?{}".format(base_url, full_param_string)
    return full_url


def bot_login(browser, credentials):
    params = {
        "product_abbrev": "mgmt",
        "xurl": CWHL_BASE_URL,
        "master_product": "39357"
    }
    login_url = url_with_params(CBS_LOGIN_URL, params)
    browser.go_to(login_url)
    browser.type(credentials["userid"], into="Email")
    browser.type(credentials["password"], into="Password")
    browser.click("Log In")


def choose_period(browser, week_number):
    dropdown = find_dropdown(browser, "period")
    all_options = dropdown.find_elements_by_tag_name("option")

    # Assumption: the options are always returned in top-to-bottom order
    index = week_number - 1
    all_options[index].click()


def set_matchups(browser, all_matchups):
    browser.go_to("https://baio.hockey.cbssports.com/setup/commish-tools/schedule-edit")

    week_number = 1
    for week_matchups in all_matchups:
        choose_period(browser, week_number)
        choose_teams_for_games(browser, week_matchups)

        # TODO: Uncomment this to actually make this work.
        # To be done once next season's schedule is ready.
        # browser.click("OK")
        week_number += 1


def set_all_matchups():
    credentials = read_site_credentials()
    all_matchups = read_matchups()
    browser = webbot.Browser()
    bot_login(browser, credentials)
    set_matchups(browser, all_matchups)


set_all_matchups()
