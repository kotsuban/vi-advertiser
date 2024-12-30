import subprocess
import pyautogui
from termcolor import colored
import time
from PIL import ImageDraw
import sqlite3

# Options.
OPEN_DIALOG_X = 185
OPEN_DIALOG_Y = 400

UNKNOWN_USER_X = 1757
UNKNOWN_USER_Y = 854

VISITED_USER_X = 2157
VISITED_USER_Y = 854

AD_CONTENT = "__PLACEHOLDER__"

COMMANDS = {
    "COPY": "COPY",
    "FOCUS": "FOCUS",
    "HOTKEY": "HOTKEY",
    "CLICK": "CLICK",
    "INIT": "INIT",
    "SANITY": "SANITY",
    "IS_AVAILABLE": "IS_AVAILABLE",
    "ERROR": "ERROR",
}

CMD_KEYS = {"COMMAND": "command"}


def log(cmd, text, color):
    print(colored(cmd, color), text)


def copy(text):
    log(COMMANDS["COPY"], text, "red")
    script = f"""
    tell application "System Events"
        set the clipboard to "{text}"
    end tell
    """

    subprocess.run(["osascript", "-e", script], check=True)


def hotkey(cmd, key, interval=0.25):
    log(COMMANDS["HOTKEY"], f"{cmd} + {key}", "yellow")
    pyautogui.hotkey(cmd, key, interval=interval)


def click(x, y, interval=0.25):
    log(COMMANDS["CLICK"], f"x={x}, y={y}", "blue")
    pyautogui.click(x, y, interval=interval)


def focus_window(id):
    log(COMMANDS["FOCUS"], id, "light_cyan")
    script = f"""
    tell application "{id}"
        activate
    end tell
    """

    subprocess.run(["osascript", "-e", script], check=True)


def check_sanity():
    log(COMMANDS["SANITY"], "_0_0_", "red")
    screenshot = pyautogui.screenshot()
    draw = ImageDraw.Draw(screenshot)
    x, y = 2157, 854
    dot_radius = 3
    dot_color = (255, 0, 0)
    # Draw the red dot on the image
    draw.ellipse(
        [(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)],
        fill=dot_color,
    )

    screenshot.show()


def is_available(x, y):
    red, green, blue = pyautogui.pixel(x, y)
    available = red == 0 and green == 0 and blue == 0
    log(COMMANDS["IS_AVAILABLE"], available, "green")
    return available


def get_numbers():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        query = "SELECT Телефон FROM 'users'"
        cursor.execute(query)

        results = cursor.fetchall()

        return results
    except sqlite3.Error as e:
        log(COMMANDS["ERROR"], e, "red")
        return []


def main():
    ITERATIONS = 0
    UNKNOWN_NUMBERS = 0
    DOUBLE_NUMBERS = 0
    UNAVAILABLE_NUMBERS = 0
    ALREADY_VISITED = 0
    DIVIDER = ";"

    log(COMMANDS["INIT"], "Advertiser v0.1", "yellow")
    focus_window("Viber")
    time.sleep(0.5)
    numbers = get_numbers()
    unique_numbers = list({number for number in numbers if number[0] is not None})
    for wnumber in unique_numbers:
        ITERATIONS += 1
        number = wnumber[0]

        if DIVIDER in number:
            DOUBLE_NUMBERS += 1
            number = number.split(DIVIDER)[0].strip()

        hotkey(CMD_KEYS["COMMAND"], "d")
        copy(number)
        hotkey(CMD_KEYS["COMMAND"], "v")
        click(OPEN_DIALOG_X, OPEN_DIALOG_Y)
        user_available = is_available(UNKNOWN_USER_X, UNKNOWN_USER_Y)
        if user_available is False:
            UNAVAILABLE_NUMBERS += 1
            log(COMMANDS["ERROR"], "user is not available", "red")
            continue
        user_is_unique = is_available(VISITED_USER_X, VISITED_USER_Y)
        if user_is_unique is False:
            ALREADY_VISITED += 1
            log(COMMANDS["ERROR"], "user is already visited", "red")
            continue

        copy(AD_CONTENT)
        hotkey(CMD_KEYS["COMMAND"], "v")
        pyautogui.press("enter")

    print(
        "UNAVAILABLE:",
        UNAVAILABLE_NUMBERS,
        "UNKNOWN:",
        UNKNOWN_NUMBERS,
        "DOUBLE:",
        DOUBLE_NUMBERS,
        "VISITED:",
        ALREADY_VISITED,
    )
    print("ITERATIONS:", ITERATIONS)


if __name__ == "__main__":
    main()
