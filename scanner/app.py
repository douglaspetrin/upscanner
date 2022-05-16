import sys
import time

import requests  # type: ignore
import json
import os
from playwright.sync_api import sync_playwright, Page
from fake_useragent import UserAgent

from scanner.models import Profile, Address

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = BASE[: BASE.find("upscanner") + len("upscanner")] + "/"


class Scanner:
    def __init__(self) -> None:
        self.params = self.get_params()

    def login(self, use_last_state: bool = True, store_new_state: bool = True) -> None:
        with sync_playwright() as p:

            browser = p.firefox.launch(
                headless=self.params["headless"], slow_mo=self.params["slow_mo"]
            )

            storage_state = self.get_path(self.params["state_file"]) if use_last_state else None
            context = browser.new_context(storage_state=storage_state)

            page = context.new_page()
            page.goto(url=self.params["login_url"])

            if not storage_state:
                self._login_steps(page=page)

                # making sure we got global token
                page.wait_for_timeout(self.params["wait_for_timeout"])
                page.goto(url=self.params["home_url"])

            if store_new_state:
                storage = context.storage_state(path=self.get_path(self.params["state_file"]))
                print(f"storage:{storage}")

            browser.close()

    def _login_steps(self, page: Page) -> None:

        print("filling username...")
        page.fill(selector="input#login_username", value=self.params["login"])
        page.click(selector="button#login_password_continue")

        print("filling password...")
        page.fill(selector="input#login_password", value=self.params["password"])
        page.click(selector="button#login_control_continue")

        try:
            print("locating answer...")
            locator = page.locator(selector="input#login_answer")
            if locator:
                print("filling answer...")
                locator.fill(value=self.params["secret_answer"])
                page.keyboard.press(key="Enter")
        except Exception as answer_exception:
            print("login_answer.answer_exception:", answer_exception)
            pass

    @staticmethod
    def _open_file(filename: str) -> dict:
        with open(file=filename, mode="r") as file:
            return json.loads(file.read())

    def get_state(self) -> dict:
        return self._open_file(filename=self.get_path(self.params["state_file"]))

    def get_params(self) -> dict:
        return self._open_file(filename=self.get_path("params.json"))

    @staticmethod
    def get_path(filename: str) -> str:
        return BASE_DIR + filename

    def get_cookies(self) -> dict:
        state = self.get_state()
        cookies = {}
        for item in state["cookies"]:
            cookies[item["name"]] = item["value"]
        return cookies

    def get_headers(self, referer_url: str) -> dict:

        cookies = self.get_cookies()

        headers = self.params["headers"]
        headers["Referer"] = referer_url

        global_token = cookies.get("oauth2_global_js_token")

        if global_token is None:
            for key, value in cookies.items():
                headers[key] = value
        else:
            headers["Authorization"] = f"Bearer {global_token}"

        if self.params["use_fake_user_agent"]:
            headers["User-Agent"] = self._get_random_user_agent()

        return headers

    @staticmethod
    def _get_random_user_agent() -> str:
        user_agent = UserAgent()
        return user_agent.random

    def get_contact_info(self) -> dict:
        response = requests.get(
            url=self.params["endpoints"]["contactInfo"],
            cookies=self.get_cookies(),
            headers=self.get_headers(referer_url=self.params["referer_url"]["contactInfo"]),
        )
        return response.json()["freelancer"]

    def get_high_chance(self) -> dict:
        response = requests.get(
            url=self.params["endpoints"]["high-chance"],
            cookies=self.get_cookies(),
            headers=self.get_headers(referer_url=self.params["referer_url"]["high-chance"]),
        )
        return response.json()

    @staticmethod
    def save_into_file(data: dict, filename: str) -> None:
        with open(file=filename, mode="w") as file:
            file.write(json.dumps(data))

    def store_best_matches(self) -> None:
        high_chance = self.get_high_chance()
        self.save_into_file(data=high_chance["results"], filename="high-chance.json")

    def create_profile(self) -> Profile:
        data = self.get_contact_info()

        profile = Profile()
        profile.id = data.get("rid")
        profile.account = data.get("userRid")
        profile.employer = data.get("employer")
        profile.first_name = data.get("firstName")
        profile.last_name = data.get("lastName")
        profile.full_name = profile.first_name + profile.last_name
        profile.email = data["email"].get("address")
        profile.phone_number = data["address"].get("phone")
        profile.birth_date = data.get("birthDate")
        profile.picture_url = data["portrait"].get("originalPortrait")
        profile.address = Address(
            line1=data["address"].get("street"),
            line2=data["address"].get("additionalInfo"),
            city=data["address"].get("city"),
            state=data["address"].get("state"),
            postal_code=data["address"].get("zip"),
            country=data["address"].get("country"),
        )

        return profile


if __name__ == "__main__":
    scanner = Scanner()
    args = sys.argv[1:]

    for _ in range(scanner.params["tries"]):
        try:
            # start scanning
            scanner.login(use_last_state="last-state" in args)

            # store data in file
            scanner.store_best_matches()

            # creates Profile object
            user_profile = scanner.create_profile()
            print(user_profile)
            print(user_profile.json())
            break

        except Exception as e:
            print(e)
            time.sleep(scanner.params["try_sleep"])
