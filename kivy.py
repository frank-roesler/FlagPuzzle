from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from os.path import join
import json
import random


class FlagPuzzle(BoxLayout):
    def __init__(self):
        super().__init__(orientation="vertical", padding=10, spacing=10)

        # Load countries
        self.flags_folder = join("country-flags-main", "png")
        with open("country-flags-main/countries.json", "r", encoding="utf-8") as f:
            names_dict = json.load(f)
            self.country_names = [(k.lower(), v) for k, v in names_dict.items()]

        # Create widgets
        self.flag_image = Image(allow_stretch=True, keep_ratio=True, size_hint=(1, 0.8))

        self.name_label = Label(text="?", font_size="40sp", size_hint=(1, 0.1), halign="center")

        self.reveal_button = Button(text="Reveal", size_hint=(None, None), size=(200, 60), pos_hint={"center_x": 0.5}, on_press=self.on_button_press)

        # Add widgets to layout
        self.add_widget(self.flag_image)
        self.add_widget(self.name_label)
        self.add_widget(self.reveal_button)

        # Initialize state
        self.reveal_mode = True
        self.load_random_flag()

        # Bind keyboard
        Window.bind(on_key_down=self.on_key_down)

    def load_random_flag(self):
        img_name, self.current_country = random.choice(self.country_names)
        self.flag_image.source = join(self.flags_folder, f"{img_name}.png")

    def on_button_press(self, instance):
        if self.reveal_mode:
            self.name_label.text = self.current_country
            self.reveal_button.text = "Next"
        else:
            self.load_random_flag()
            self.name_label.text = "?"
            self.reveal_button.text = "Reveal"
        self.reveal_mode = not self.reveal_mode

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # keycode[1] contains the key name
        if keycode[1] == "spacebar":
            self.reveal_button.trigger_action()
            return True
        return False


class FlagPuzzleApp(App):
    def build(self):
        # Set window size
        Window.size = (1000, 600)
        Window.minimum_width = 200
        Window.minimum_height = 200
        return FlagPuzzle()


if __name__ == "__main__":
    FlagPuzzleApp().run()
