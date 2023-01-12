import threading

from kivy.clock import Clock
from kivymd.app import MDApp
from functions import *


class EvolutionSimulationApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Game of Life"
        self.restart_button = None
        self.button_delete = None
        self.button_save = None
        self.reset_button = None
        self.in_simulation = False
        self.grid_zone_layout = None
        self.start_button = None
        self.simulation = None

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

        Clock.schedule_once(self.simulation.loading_modal.open, 2)
        delay = 2  # seconds
        start_time = threading.Timer(delay, self.simulation.load_cells_in_np_2d_array)
        start_time.start()

    def update_start_button(self):
        if self.in_simulation:
            self.start_button.background_normal = pause_button_logo_name
        else:
            self.start_button.background_normal = start_button_logo_name

    def start_simulation(self, *args):
        if not self.in_simulation:
            self.simulation.is_stability_reached = False
            self.in_simulation = True
            print('Starting simulation...')
            self.simulation.initial_state = self.simulation.active_cells_list.copy()
            self.update_start_button()
            # Schedule the update_grid method to be called every run_interval_seconds second
            Clock.schedule_interval(self.simulation.update_grid, 1)
        else:
            self.in_simulation = False
            print('Pausing simulation...')
            self.update_start_button()
            # Stop the clock
            Clock.unschedule(self.simulation.update_grid)

    def on_save_icon_clicked(self, *args):
        if self.in_simulation:
            show_toast(message="Cannot save while in simulation...", bg_col=[1, 0, 0, .5])
        else:
            if self.simulation.active_cells_list:
                self.simulation.save_state_modal.open()
            else:
                show_toast(message="Nothing to save", bg_col=[0, 0, 0, .5])

    def reset_grid(self, *args) -> None:
        """
        Reset the grid by deactivating all active cells (rectangles)
        :return:
        """
        if not self.in_simulation:
            self.simulation.reset_grid()
        else:
            show_toast(message="Cannot reset while in simulation", bg_col=[1, 0, 0, .5])
            print("Still in simulation. Cannot reset while in simulation...")

    def restart(self, *args) -> None:
        """
        Reset the grid by deactivating all active cells (rectangles)
        :return:
        """
        if not self.in_simulation:
            self.simulation.load_initial_state()
        else:
            show_toast(message="Cannot restart while in simulation", bg_col=[1, 0, 0, .5])
            print("Still in simulation. Cannot restart while in simulation")

    def on_delete_state_icon_clicked(self, *args):
        if self.in_simulation:
            show_toast(message="Cannot delete while in simulation...", bg_col=[1, 0, 0, .5])
        else:
            if self.simulation.current_selected_state_index is not None:
                self.simulation.delete_state_modal.open()
            else:
                show_toast(message="No saved state freshly selected", bg_col=[0, 0, 0, .5], duration=5)


# Run the app
if __name__ == '__main__':
    EvolutionSimulationApp().run()
