import time
import json
import math
import getpass
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------
USERNAME = input("Enter username: ")
PASSWORD = getpass.getpass("Enter password: ")

URL = "https://just-dice.com"
STATE_FILE = "bot_state.json"

# -------------------------------
def save_state(data):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return None

# -------------------------------
class RunBot:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")

        service = Service("/home/snowy/geckodriver")

        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)

        self.driver.get(URL)

        print("✅ Page loading...")
        time.sleep(10)

        self.handle_popup()

    # -------------------------------
    def handle_popup(self):
        print("🔧 Handling popup...")

        try:
            close_btns = self.driver.find_elements(By.CSS_SELECTOR, ".fancybox-close")
            for btn in close_btns:
                self.driver.execute_script("arguments[0].click();", btn)
        except:
            pass

        # FORCE remove overlay
        self.driver.execute_script("""
            let overlay = document.querySelector('.fancybox-overlay');
            if (overlay) overlay.remove();
            document.body.classList.remove('fancybox-lock');
        """)

        time.sleep(2)
        self.open_login()

    # -------------------------------
    def open_login(self):
        print("🔓 Opening login...")

        self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        links = self.driver.find_elements(By.TAG_NAME, "a")

        for l in links:
            if l.text.strip() == "Account":
                self.driver.execute_script("arguments[0].click();", l)
                break

        self.wait_login_panel()

    # -------------------------------
    def wait_login_panel(self):
        print("⏳ Waiting for login panel...")
        self.wait.until(EC.presence_of_element_located((By.ID, "myuser")))
        time.sleep(2)
        self.do_login()

    # -------------------------------
    def do_login(self):
        print("🔐 Logging in...")

        self.driver.find_element(By.ID, "myuser").send_keys(USERNAME)
        self.driver.find_element(By.ID, "mypass").send_keys(PASSWORD)

        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(By.ID, "myok")
        )

        print("⏳ Waiting after login...")
        time.sleep(10)

        self.wait_balance()

    # -------------------------------
    def wait_balance(self):
        print("⏳ Waiting for balance...")

        while True:
            bal = self.get_value("#pct_balance")
            if bal is not None:
                print(f"✅ Balance: {bal}")
                self.state = load_state()

                # reset timer after recovery/login
                self.last_change = time.time()

                self.init_betting(float(bal))
                break
            time.sleep(0.00001)

    # -------------------------------
    def init_betting(self, whiskers):
        if self.state and "last_balance" in self.state:
            print(f"🔄 Last diff: {whiskers - self.state['last_balance']:.8f}")

        self.whiskers = whiskers
        self.tabby = round(whiskers / 144000, 8)

        if self.tabby == 0:
            time.sleep(2)
            self.wait_balance()
            return

        self.purr = 49.5
        self.tens = self.tabby * 10
        self.sevens = self.tabby * 6.9
        self.eights = self.tabby * 7.9
        self.mighty = ((math.floor(whiskers / self.tens)) * self.tens)

        self.last_balance = whiskers
        self.last_change = time.time()

        if self.state:
            self.cat = self.state["cat"]
            self.felix = self.state["felix"]
            self.orgy = self.state["orgy"]
            self.shadow = self.state["shadow"]
            self.smokey = self.state["smokey"]
            self.fart = self.state["fart"]
        else:
            self.cat = self.tabby
            self.fart = 1
            self.shadow = whiskers
            self.smokey = whiskers
            self.felix = self.mighty
            self.orgy = self.mighty

        print(f"🐾 Balance: {whiskers:.8f} | Bet: {self.cat:.8f}")

        self.run_click("#b_min")
        self.loop()

    # -------------------------------
    def loop(self):
        while True:
            try:
                bal = self.get_value("#pct_balance")
                if bal is None:
                    continue

                if bal != self.last_balance:
                    self.last_balance = bal
                    self.last_change = time.time()

                # 🔥 FULL RECOVERY TRIGGER
                if time.time() - self.last_change > 120:
                    print("⚠️ Stuck detected → full recovery")
                    self.full_recovery()
                    return

                if abs(self.shadow - bal) < 1e-8 or abs(self.smokey - bal) < 1e-8:
                    current = bal
                    self.mighty = ((math.floor(current / self.tens)) * self.tens)

                    if (current >= (self.orgy + (self.tens * self.fart))):
                        self.cat = self.tabby
                        self.fart = 1
                        self.felix = float(self.mighty)
                        self.orgy = float(self.mighty)

                    if ((current> (self.mighty + self.sevens)) and  (current<(self.mighty + self.eights)) and (current>self.felix)):
                        self.cat *= 2
                        self.felix = float(current)
                        
                    if ((current> (self.mighty + self.sevens)) and  (current<(self.mighty + self.eights)) and (current<self.felix)):
                        self.cat *= 2
                        self.fart = 0
                        self.felix = float(current)
                        
                    print(f"📈 Bal: {bal:.8f} | Profit: {(bal - self.whiskers):.8f} | Bet: {self.cat:.8f}")

                    self.set_value("#pct_chance", self.purr)
                    self.set_value("#pct_bet", f"{self.cat:.8f}")

                    self.shadow = round(current + self.cat, 8)
                    self.smokey = round(current - self.cat, 8)

                    save_state({
                        "cat": self.cat,
                        "felix": self.felix,
                        "orgy": self.orgy,
                        "shadow": self.shadow,
                        "smokey": self.smokey,
                        "fart": self.fart,
                        "last_balance": self.last_balance
                    })

                    self.run_click("#a_lo")

                time.sleep(0.0002)

            except Exception as e:
                print("⚠️ Loop error:", e)
                time.sleep(2)

    # -------------------------------
    def clear_session(self):
        print("🧹 Clearing cookies + storage...")

        try:
            self.driver.delete_all_cookies()
        except:
            pass

        try:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except:
            pass

    # -------------------------------
    def full_recovery(self):
        print("♻️ FULL RECOVERY STARTED")

        try:
            self.clear_session()
        except:
            pass

        try:
            self.driver.get(URL)
        except:
            print("⚠️ Reload failed → restarting driver")
            self.reload_page()
            return

        print("⏳ Waiting for page load...")
        time.sleep(10)

        self.handle_popup()

        print("⏳ Waiting 20s after login...")
        time.sleep(20)

        self.wait_balance()

    # -------------------------------
    def reload_page(self):
        self.driver.quit()
        self.__init__()

    # -------------------------------
    def get_value(self, selector):
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            return float(el.get_attribute("value"))
        except:
            return None

    def set_value(self, selector, val):
        self.driver.execute_script(
            f'document.querySelector("{selector}").value="{val}";'
        )

    def run_click(self, selector):
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script("arguments[0].click();", el)
        except:
            pass

# -------------------------------
if __name__ == "__main__":
    RunBot()
