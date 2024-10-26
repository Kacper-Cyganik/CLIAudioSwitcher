#!/usr/bin/env python
"""
An extended example with a main menu and submenus using prompt_toolkit.
"""

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
import pulsectl


class MenuApp:
    def __init__(self):
        # Initialize the application state
        self.current_menu = "Main"
        self.text_area = TextArea(
            focusable=False, text="Toggle Audio & Display settings"
        )

        # Set up the initial layout
        self.root_container = self.create_root_container()
        self.layout = Layout(container=self.root_container)

        # Set up style
        self.style = Style(
            [
                ("left-pane", "bg:#888800 #000000"),
                ("right-pane", "bg:#00aa00 #000000"),
                ("button", "#000000"),
                ("button-arrow", "#000000"),
                ("button focused", "bg:#ff0000"),
                ("text-area focused", "bg:#ff0000"),
            ]
        )

        # Set up key bindings
        self.kb = KeyBindings()
        self.kb.add("tab")(focus_next)
        self.kb.add("s-tab")(focus_previous)

        # Build the main application
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
        )

    def create_root_container(self):
        """Creates the root container layout based on the current menu."""
        return Box(
            HSplit(
                [
                    Label(text="Press Tab to move the focus."),
                    VSplit(
                        [
                            Box(
                                body=HSplit(
                                    self.create_buttons_for_current_menu(),
                                    padding=1,
                                ),
                                padding=1,
                                style="class:left-pane",
                            ),
                            Box(
                                body=Frame(self.text_area),
                                padding=1,
                                style="class:right-pane",
                            ),
                        ]
                    ),
                ]
            )
        )

    def create_buttons_for_current_menu(self):
        """Creates buttons based on the current menu."""
        if self.current_menu == "Main":
            return [
                Button("Audio", handler=self.audio_clicked),
                Button("Display", handler=self.display_clicked),
                Button("Exit", handler=self.exit_clicked),
            ]
        elif self.current_menu == "Audio":
            return [
                Button("Volume", handler=self.volume_clicked),
                Button("Output Source", handler=self.audio_output_clicked),
                Button("Back", handler=self.show_main_menu),
            ]
        elif self.current_menu == "Display":
            self.text_area.text = "TO DO"
            return [
                Button("Back", handler=self.show_main_menu),
            ]
        elif self.current_menu == "Audio_Output_Source":
            output_devices = self.get_output_audio_devices()
            return [
                Button(
                    f"{output_device.description}",
                    handler=lambda index=index: self.set_output_audio_device(
                        output_devices, index
                    ),
                )
                for index, output_device in enumerate(output_devices)
            ] + [Button("Back", handler=self.audio_clicked)]

    def show_main_menu(self):
        """Switches to the main menu."""
        self.current_menu = "Main"
        self.update_display()

    def audio_clicked(self):
        """Switches to the audio menu."""
        self.current_menu = "Audio"
        self.update_display()

    def display_clicked(self):
        """Switches to the display menu."""
        self.current_menu = "Display"
        self.update_display()

    def volume_clicked(self):
        """Handles volume settings."""
        self.text_area.text = "Volume settings opened."

    def audio_output_clicked(self):
        """Handles audio output."""
        self.text_area.text = "Audio output settings opened."
        self.current_menu = "Audio_Output_Source"
        self.update_display()

    def exit_clicked(self):
        """Exits the application."""
        get_app().exit()

    def update_display(self):
        """Updates the display based on the current menu."""
        self.root_container = self.create_root_container()
        self.layout = Layout(container=self.root_container)
        self.application.layout = self.layout

        # Try to set focus on the first button if available
        try:
            first_button = self.create_buttons_for_current_menu()[0]
            self.layout.focus(first_button)
        except (IndexError, ValueError):
            # Log the error or pass if no button is available or not part of the layout
            pass

        # Update the app to show the new layout
        get_app().invalidate()

    ### Audio utils
    def get_output_audio_devices(self):
        pulse = pulsectl.Pulse("my-client")
        return pulse.sink_list()

    def set_output_audio_device(self, audio_devices, index):
        selected_source = audio_devices[index]
        pulse = pulsectl.Pulse("my-client")
        pulse.default_set(selected_source)  # Set the default source

    def run(self):
        """Runs the application."""
        self.application.run()


if __name__ == "__main__":
    app = MenuApp()
    app.run()
