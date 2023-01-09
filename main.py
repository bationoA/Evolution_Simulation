from kivy.app import App
from kivy.clock import Clock
from kivymd.app import MDApp

from functions import *

import schedule
from kivy.uix.widget import Widget


class EvolutionSimulationApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.restart_button = None
        self.button_delete = None
        self.button_save = None
        self.reset_button = None
        self.in_simulation = False
        self.grid_zone_layout = None
        self.start_button = None
        self.simulation = None

    # def on_kv_post(self, *args):
    def build(self):
        self.grid_zone_layout = GridZoneLayout()
        self.simulation = self.root.ids.id_SimulationBoxLayout
        # Get a reference to the Button widget
        self.restart_button = self.root.ids.id_restart_button
        self.start_button = self.root.ids.id_start_button
        self.button_delete = self.root.ids.id_button_delete
        self.button_save = self.root.ids.id_button_save
        self.reset_button = self.root.ids.id_button_reset_grid

        # Bind the Button's on_release event to the button_callback method
        self.reset_button.bind(on_release=self.reset_grid)
        self.restart_button.bind(on_release=self.restart)
        self.start_button.bind(on_release=self.start_simulation)
        self.button_delete.bind(on_release=self.on_delete_state_icon_clicked)
        self.button_save.bind(on_release=self.on_save_icon_clicked)

    def update_start_button(self):
        # <a target="_blank" href="https://icons8.com/icon/60449/play-button-circled">Play Button Circled</a>
        # icon by <a target="_blank" href="https://icons8.com">Icons8</a>
        if self.in_simulation:
            self.start_button.background_normal = pause_button_logo_name
        else:
            self.start_button.background_normal = start_button_logo_name

    def start_simulation(self, *args):
        if not self.in_simulation:
            self.in_simulation = True
            print('Starting simulation...')
            self.simulation.initial_state = self.simulation.active_rectangles_list.copy()
            self.update_start_button()
            # Schedule the update_grid method to be called every 1 second
            Clock.schedule_interval(self.simulation.update_grid, run_interval_seconds)
        else:
            self.in_simulation = False
            print('Pausing simulation...')
            self.update_start_button()
            # Stop the clock
            Clock.unschedule(self.simulation.update_grid)

    def on_save_icon_clicked(self, *args):
        if self.in_simulation:
            self.simulation.show_toast(message="Cannot save while in simulation...", bg_col=[1, 0, 0, .5])
        else:
            if self.simulation.active_rectangles_list:
                self.simulation.save_state_modal.open()
            else:
                self.simulation.show_toast(message="Nothing to save", bg_col=[0, 0, 0, .5])

    def reset_grid(self, *args) -> None:
        """
        Reset the grid by deactivating all active cells (rectangles)
        :return:
        """
        if not self.in_simulation:
            self.simulation.reset_grid()
        else:
            self.simulation.show_toast(message="Cannot reset while in simulation", bg_col=[1, 0, 0, .5])
            print("Still in simulation. Cannot reset while in simulation...")

    def restart(self, *args) -> None:
        """
        Reset the grid by deactivating all active cells (rectangles)
        :return:
        """
        if not self.in_simulation:
            self.simulation.load_initial_state()
        else:
            self.simulation.show_toast(message="Cannot restart while in simulation", bg_col=[1, 0, 0, .5])
            print("Still in simulation. Cannot restart while in simulation")

    def on_delete_state_icon_clicked(self, *args):
        if self.in_simulation:
            self.simulation.show_toast(message="Cannot delete while in simulation...", bg_col=[1, 0, 0, .5])
        else:
            if self.simulation.current_selected_state_index is not None:
                self.simulation.delete_state_modal.open()
            else:
                self.simulation.show_toast(message="Nothing to delete", bg_col=[0, 0, 0, .5])



# Run the app
if __name__ == '__main__':
    EvolutionSimulationApp().run()
