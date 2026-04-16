import time
import json
import math
import sys
import getpass
import socket
import random
from datetime import datetime
from decimal import Decimal, getcontext

# Set precision for 8 decimal places (Satoshi standard)
getcontext().prec = 20

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
        serializable = {k: str(v) if isinstance(v, Decimal) else v for k, v in data.items()}
        with open(STATE_FILE, "w") as f:
            json.dump(serializable, f)
    except Exception as e:
        print(f"⚠️ Save error: {e}")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            decimal_keys = ["cat", "felix", "orgy", "shadow", "smokey", "tracked_balance", "initial_balance"]
            for k in decimal_keys:
                if k in data:
                    data[k] = Decimal(data[k])
            return data
    except:
        return None

# -------------------------------
class RunBot:
    def __init__(self):
        self.recovery_attempts = 0
        options = Options()
        options.add_argument("--headless")
        options.binary_location = "/home/snowy/waterfox/waterfox"
        service = Service("/home/snowy/geckodriver")

        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        self.session_start_bal = None 
        self.last_activity_time = time.time() 
        self.safe_start()

    def safe_start(self):
        try:
            self.driver.get(URL)
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Page loading...")
            time.sleep(8)
            self.handle_popup()
        except:
            self.full_recovery()

    def handle_popup(self):
        try:
            self.driver.execute_script("""
                let overlay = document.querySelector('.fancybox-overlay');
                if (overlay) overlay.remove();
                document.body.classList.remove('fancybox-lock');
            """)
        except: pass
        time.sleep(2)
        self.open_login()

    def open_login(self):
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            for l in self.driver.find_elements(By.TAG_NAME, "a"):
                if "Account" in l.text:
                    self.driver.execute_script("arguments[0].click();", l)
                    break
            self.wait.until(EC.presence_of_element_located((By.ID, "myuser")))
            self.do_login()
        except:
            self.full_recovery()

    def do_login(self):
        self.driver.find_element(By.ID, "myuser").send_keys(USERNAME)
        self.driver.find_element(By.ID, "mypass").send_keys(PASSWORD)
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "myok"))
        print("⏳ Logging in...")
        time.sleep(8)
        self.wait_balance()

    def wait_balance(self):
        while True:
            bal = self.get_value("#pct_balance")
            if bal is not None:
                self.state = load_state()
                self.init_betting(Decimal(str(bal)))
                return
            time.sleep(0.5)

    def init_betting(self, real_bal):
        self.tabby = (real_bal / Decimal("144000")).quantize(Decimal("1.00000000"))
        self.purr = 49.5
        self.tens = self.tabby * 10
        self.sevens = self.tabby * Decimal("6.9")
        self.eights = self.tabby * Decimal("7.9")
        self.session_start_bal = real_bal
        self.tracked_balance = self.state["tracked_balance"]
        
        if (real_bal == self.tracked_balance) and self.state:
            print("📂 [RECOVERY] Resuming state...")
            self.cat = self.state["cat"]
            self.felix = self.state["felix"]
            self.orgy = self.state["orgy"]
            self.shadow = self.state["shadow"]
            self.smokey = self.state["smokey"]
            self.fart = self.state["fart"]
            self.tracked_balance = self.state["tracked_balance"]
            self.initial_balance = self.state.get("initial_balance", real_bal)
            self.last_balance = real_bal
        else:
            print("🆕 Fresh start initialized.")
            self.cat = self.tabby
            self.fart = 1
            self.tracked_balance = real_bal
            self.initial_balance = real_bal
            self.last_balance = real_bal
            mighty = ((math.floor(real_bal / self.tens)) * self.tens)
            self.felix = mighty
            self.orgy = mighty
            self.shadow = real_bal
            self.smokey = real_bal

        self.last_activity_time = time.time()
        self.run_click("#b_min")
        self.loop()

    def loop(self):
        while True:
            try:
                # --- WATCHDOG ---
                if time.time() - self.last_activity_time > 55:
                    print(f"⚠️ [WATCHDOG] Inactive for 55s! Reloading...")
                    self.full_recovery()
                    return

                raw = self.get_value("#pct_balance")
                if raw is None:
                    time.sleep(0.2)
                    continue
                
                current_real = Decimal(str(raw))

                # --- LOGGING UPDATED WITH REAL BALANCE ---
                if ((float(current_real - self.last_balance)>=float(0-self.cat)) and (current_real != self.last_balance)):
                    delta = current_real - self.last_balance
                    self.tracked_balance += delta
                    self.last_balance = current_real
                    self.last_activity_time = time.time() 
                    
                    # Calculations
                    session_p = current_real - self.session_start_bal
                    life_p = self.tracked_balance - self.initial_balance
                    t_stamp = datetime.now().strftime('%H:%M:%S')
                    
                    # Clean Log Line
                    print(f"🕒 [{t_stamp}] | Bal: {current_real:.8f} | Delta: {delta:+.8f} | Sess: {session_p:+.8f} | Life: {life_p:+.8f}")

                    save_state({
                        "cat": self.cat, "felix": self.felix, "orgy": self.orgy,
                        "shadow": self.shadow, "smokey": self.smokey, "fart": self.fart,
                        "tracked_balance": self.tracked_balance,
                        "initial_balance": self.initial_balance
                    })

                if ((float(current_real - self.last_balance)<float(0-self.cat)) and current_real != self.last_balance):
                    print("fuck off hacker")
                    sys.exit()
    

                # --- STRATEGY ---
                if abs(self.shadow - current_real) < Decimal("1e-8") or abs(self.smokey - current_real) < Decimal("1e-8"):
                    mighty = ((math.floor(self.tracked_balance / self.tens)) * self.tens)

                    if self.tracked_balance >= (self.orgy + (self.tens * self.fart)):
                        self.cat = self.tabby
                        self.fart = 1
                        self.felix = mighty
                        self.orgy = mighty

                    if (self.tracked_balance>(mighty + self.sevens)) and (self.tracked_balance < (mighty + self.eights)) and self.tracked_balance < self.felix:
                        self.cat *= 2
                        self.fart = 0
                        self.felix = self.tracked_balance

                    if (self.tracked_balance>(mighty + self.sevens)) and (self.tracked_balance < (mighty + self.eights)) and self.tracked_balance > self.felix:
                        self.cat *= 2
                        self.felix = self.tracked_balance

                    self.set_value("#pct_chance", self.purr)
                    self.set_value("#pct_bet", f"{self.cat:.8f}")

                    self.shadow = (current_real + self.cat).quantize(Decimal("1.00000000"))
                    self.smokey = (current_real - self.cat).quantize(Decimal("1.00000000"))

                    self.run_click("#a_lo")

                time.sleep(0.1)

            except Exception as e:
                print(f"⚠️ Loop Error: {e}")
                time.sleep(1)

    def full_recovery(self):
        print("♻️ Reloading...")
        try: self.driver.quit()
        except: pass
        time.sleep(5)
        self.__init__()

    def get_value(self, selector):
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            return float(el.get_attribute("value"))
        except: return None

    def set_value(self, selector, val):
        self.driver.execute_script(f'document.querySelector("{selector}").value="{val}";')

    def run_click(self, selector):
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script("arguments[0].click();", el)
        except: pass

if __name__ == "__main__":
    bot = None
    try:
        bot = RunBot()
    except SystemExit:
        # This catches sys.exit() calls
        print("👋 Bot shutting down via script command.")
    except KeyboardInterrupt:
        print("\n🛑 Manual stop (Ctrl+C).")
    finally:
        if bot and hasattr(bot, 'driver'):
            print("🧹 Closing browser and saving final state...")
            # Save the last known numbers
            save_state({
                "cat": bot.cat, "felix": bot.felix, "orgy": bot.orgy,
                "shadow": bot.shadow, "smokey": bot.smokey, "fart": bot.fart,
                "tracked_balance": bot.tracked_balance,
                "initial_balance": bot.initial_balance
            })
            bot.driver.quit()
