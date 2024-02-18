class BongoTamagochi:
    def __init__(self, name):
        self.name = name
        # attributes
        self.hunger = 50
        self.happiness = 10
        self.energy = 100
        self.age = 1  # in days

        # states
        self.animations = [
            "idle",
            "typing1",
            "typing2",
            "playing1",
            "playing2" "happy",
            "eating",
            "sleeping",
            "playing",
        ]
        self.state = "idle"
        self.animation_switcher = False
        self.cooldown = 0
        self.multiplier = 100
        self.state_counter = 1

    def getAnimation(self):
        switcher = {
            "idle": "idle",
            "typing1": "handsupleft1",
            "typing2": "handsuprigth1",
            "playing1": "playing1",
            "playing2": "playing2",
            "happy": "handsupboth1",
            "eating": "eating",
            "sleeping": "sleeping",
            "playing": "handsupboth1",
        }
        # get asset name
        asset_name = f"{switcher.get(self.state)}.png"
        return asset_name

    def updateAnimationTo(self, state):
        switcher = {
            "idle": "idle",
            "typing1": "handsupleft1",
            "typing2": "handsuprigth1",
            "happy": "handsupboth1",
            "eating": "eating",
            "sleeping": "sleeping",
            "playing": "playing",
        }

        self.state = switcher.get(state, "idle")

        asset_name = f"{self.state}.png"

        return asset_name

    def waitForCooldownDecorator(func):
        def wrapper(self):
            if self.cooldown > 0:
                print(f"{self.name} is on cooldown for {self.cooldown} clicks.")
            else:
                func(self)

        return wrapper

    @waitForCooldownDecorator
    def feed(self):
        self.happiness += 1
        self.cooldown = 3 * self.multiplier
        self.state = "eating"

    @waitForCooldownDecorator
    def play(self):
        self.happiness += 1
        self.cooldown = 2 * self.multiplier
        self.state = "playing1"

    @waitForCooldownDecorator
    def sleep(self):
        self.energy += 1
        self.cooldown = 20 * self.multiplier
        self.state = "sleeping"

    @waitForCooldownDecorator
    def type(self):
        if self.animation_switcher:
            self.state = "typing1"
            self.animation_switcher = False
        else:
            self.state = "typing2"
            self.animation_switcher = True

    def each(self, turns):
        # return true if N turns have passed (being turns * multiplier)
        return float(self.state_counter) % (float(turns) * float(self.multiplier)) == 0

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

            if self.state == "sleeping":
                if self.each(0.2):
                    self.hunger -= 1
                    self.energy += 1

            if self.state == "eating":
                if self.each(0.2):
                    self.hunger += 1
                    self.happiness += 1
                    self.energy -= 1

            if self.state in ["playing1", "playing2"]:
                if self.animation_switcher:
                    self.state = "playing1"
                else:
                    self.state = "playing2"
                self.animation_switcher = not self.animation_switcher

                if self.each(0.2):
                    self.happiness += 2
                    self.energy -= 1
                    self.hunger -= 1

        else:
            if self.state in [
                "typing1",
                "typing2",
            ]:
                if self.animation_switcher:
                    self.state = "typing1"
                else:
                    self.state = "typing2"
                if self.each(0.2):
                    self.animation_switcher = not self.animation_switcher
                    self.energy -= 1
                    self.hunger -= 1

            else:
                self.state = "idle"
                if self.each(0.2):
                    self.animation_switcher = not self.animation_switcher
                    self.energy -= 1
                    self.hunger -= 1

        self.state_counter += 1

        save_data(self.to_file())
        return self.getAnimation()

    def status(self):
        print(
            f"{self.name} is {self.state} with {self.hunger} hunger, {self.happiness} happiness and {self.energy} energy."
        )

    def from_file(self, data):
        self.name = data["name"]
        self.hunger = data["hunger"]
        self.happiness = data["happiness"]
        self.energy = data["energy"]
        self.age = data["age"]

    def to_file(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "age": self.age,
        }


import json


def load_data():
    # Load the data from a file
    default_data = BongoTamagochi("Bongo").to_file()

    try:
        with open("data/appdata.json", "r") as file:
            data = json.load(file)
    except:
        data = default_data

    if data == {}:
        data = default_data

    return data


from datetime import date


def load_game_data():
    # Load the data from a file
    default_data = {"day": date.today().isoformat(), "multiplier": 40}

    try:
        with open("data/gamedata.json", "r") as file:
            data = json.load(file)
    except:
        data = default_data

    if data == {}:
        data = default_data

    return data


def save_game_data(data):
    with open("data/gamedata.json", "w") as file:
        json.dump(data, file)


def save_data(data):
    with open("data/appdata.json", "w") as file:
        json.dump(data, file)


# Keyboard setup
from pynput import keyboard


# TKinter setup
import tkinter as tk
from tkinter import ttk


class BongoTamagochiApp(tk.Tk):
    def __init__(self):
        # setup the window
        super().__init__()
        self.title("Genji")
        self.geometry("300x400+1920+0")
        self.attributes("-topmost", True)
        self.lift()

        # load data
        data = load_data()
        self.bongo = BongoTamagochi("Genji")
        self.bongo.from_file(data)
        save_data(self.bongo.to_file())

        # load game data
        game_data = load_game_data()
        self.game_day = game_data["day"]
        if self.game_day != date.today().isoformat():
            self.game_day = date.today().isoformat()
            self.bongo.age += 1
            game_data["day"] = self.game_day

        save_game_data(game_data)

        # add state img
        self.state_img = tk.PhotoImage(file=f"assets/{self.bongo.getAnimation()}")

        # add state click
        self.state_click = False

        # create a canvas for the image
        self.canvas = tk.Canvas(self, width=300, height=300)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)

        self.hunger_bar_container = tk.Frame(self)
        self.happiness_bar_container = tk.Frame(self)
        self.energy_bar_container = tk.Frame(self)

        self.hunger_status_container = tk.Frame(self)
        self.happiness_status_container = tk.Frame(self)
        self.energy_status_container = tk.Frame(self)

        # place the containers
        self.hunger_status_container.place(x=0, y=300, width=75, height=25)
        self.happiness_status_container.place(x=0, y=325, width=75, height=25)
        self.energy_status_container.place(x=0, y=350, width=75, height=25)

        self.hunger_bar_container.place(x=75, y=300, width=225, height=25)
        self.happiness_bar_container.place(x=75, y=325, width=225, height=25)
        self.energy_bar_container.place(x=75, y=350, width=225, height=25)

        # create bars to display the stats
        self.hunger_bar = ttk.Progressbar(
            self.hunger_bar_container,
            orient="horizontal",
            length=225,
            mode="determinate",
            style="yellow.Horizontal.TProgressbar",
        )
        self.happiness_bar = ttk.Progressbar(
            self.happiness_bar_container,
            orient="horizontal",
            length=225,
            mode="determinate",
            style="pink.Horizontal.TProgressbar",
        )
        self.energy_bar = ttk.Progressbar(
            self.energy_bar_container,
            orient="horizontal",
            length=225,
            mode="determinate",
            style="green.Horizontal.TProgressbar",
        )

        # Status being colored squares
        self.hunger_status = tk.Label(
            self.hunger_status_container, bg="red", width=75, text="Hunger"
        )
        self.happiness_status = tk.Label(
            self.happiness_status_container, bg="red", width=75, text="Happiness"
        )
        self.energy_status = tk.Label(
            self.energy_status_container, bg="red", width=75, text="Energy"
        )

        # place the bars
        self.hunger_bar.pack(in_=self.hunger_bar_container)
        self.happiness_bar.pack(in_=self.happiness_bar_container)
        self.energy_bar.pack(in_=self.energy_bar_container)

        self.hunger_status.pack(in_=self.hunger_status_container)
        self.happiness_status.pack(in_=self.happiness_status_container)
        self.energy_status.pack(in_=self.energy_status_container)

        def update_bars(self):
            # set values for the bars
            if self.bongo.hunger > 0:
                self.hunger_bar["value"] = self.bongo.hunger
                self.hunger_status["bg"] = "green"
            else:
                self.hunger_bar["value"] = 0
                self.hunger_status["bg"] = "red"

            if self.bongo.happiness > 0:
                self.happiness_bar["value"] = self.bongo.happiness
                self.happiness_status["bg"] = "green"
            else:
                self.happiness_bar["value"] = 0
                self.happiness_status["bg"] = "red"

            if self.bongo.energy > 0:
                self.energy_bar["value"] = self.bongo.energy
                self.energy_status["bg"] = "green"
            else:
                self.energy_bar["value"] = 0
                self.energy_status["bg"] = "red"

        # update the bars
        update_bars(self)

        def actionWrapper(action):
            def wrapper():
                action()
                self.bongo.update()
                self.state_img = tk.PhotoImage(
                    file=f"assets/{self.bongo.getAnimation()}"
                )
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)
                update_bars(self)

            return wrapper

        # add buttons
        self.feed_button = tk.Button(
            self, text="Feed", command=actionWrapper(self.bongo.feed)
        )
        self.play_button = tk.Button(
            self, text="Play", command=actionWrapper(self.bongo.play)
        )
        self.sleep_button = tk.Button(
            self, text="Sleep", command=actionWrapper(self.bongo.sleep)
        )
        self.feed_button.place(x=0, y=375, width=100, height=25)
        self.play_button.place(x=100, y=375, width=100, height=25)
        self.sleep_button.place(x=200, y=375, width=100, height=25)

        def update_buttons():
            if self.bongo.cooldown > 0:
                self.feed_button["state"] = "disabled"
                self.play_button["state"] = "disabled"
                self.sleep_button["state"] = "disabled"

                self.feed_button["text"] = f"Feed ({self.bongo.cooldown})"
                self.play_button["text"] = f"Play ({self.bongo.cooldown})"
                self.sleep_button["text"] = f"Sleep ({self.bongo.cooldown})"

            else:
                self.feed_button["state"] = "active"
                self.play_button["state"] = "active"
                self.sleep_button["state"] = "active"

                self.feed_button["text"] = "Feed"
                self.play_button["text"] = "Play"
                self.sleep_button["text"] = "Sleep"

        # update the buttons
        update_buttons()

        # waiter on finish typing, using timeout
        timeout = 500

        def on_timeout():
            self.state_img = tk.PhotoImage(
                file=f"assets/{self.bongo.updateAnimationTo('idle')}"
            )
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)

        # keyboard listener
        def on_press(key):
            if self.state_click:
                return
            # update the state "typing"
            if self.bongo.cooldown == 0:
                self.bongo.type()
                self.state_img = tk.PhotoImage(
                    file=f"assets/{self.bongo.getAnimation()}"
                )
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)
                self.after(int(timeout), on_timeout)
            else:
                if self.bongo.state in ["playing1", "playing2"]:
                    self.state_img = tk.PhotoImage(
                        file=f"assets/{self.bongo.getAnimation()}"
                    )
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)
                elif self.bongo.state in ["eating"]:
                    self.state_img = tk.PhotoImage(
                        file=f"assets/{self.bongo.getAnimation()}"
                    )
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)
                elif self.bongo.state in ["sleeping"]:
                    self.state_img = tk.PhotoImage(
                        file=f"assets/{self.bongo.getAnimation()}"
                    )
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)
                else:
                    self.state_img = tk.PhotoImage(
                        file=f"assets/{self.bongo.updateAnimationTo('idle')}"
                    )
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.state_img)

            self.state_click = True

        self.on_press = on_press

        def on_release(key):
            self.state_click = False
            self.bongo.update()
            update_bars(self)

        self.on_release = on_release


if __name__ == "__main__":
    app = BongoTamagochiApp()
    listener = keyboard.Listener(on_press=app.on_press, on_release=app.on_release)
    listener.start()

    app.mainloop()
