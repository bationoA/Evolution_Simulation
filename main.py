from kivy.clock import Clock

from functions import *
import schedule
from kivy.uix.widget import Widget


class EvolutionSimulationApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.in_simulation = False
        self.grid_zone_layout = None
        self.start_button = None
        self.simulation = None

    # def on_kv_post(self, *args):
    def build(self):
        self.grid_zone_layout = GridZoneLayout()
        self.simulation = self.root.ids.id_SimulationBoxLayout
        # Get a reference to the Button widget
        self.start_button = self.root.ids.id_start_button

        print(f"self.root : {self.root}")
        print(f"self.start_button : {self.start_button}")
        # Bind the Button's on_release event to the button_callback method
        self.start_button.bind(on_release=self.start_simulation)

    def update_start_button(self):
        # <a target="_blank" href="https://icons8.com/icon/60449/play-button-circled">Play Button Circled</a>
        # icon by <a target="_blank" href="https://icons8.com">Icons8</a>
        if self.in_simulation:
            self.start_button.background_normal = pause_button_logo_name
        else:
            self.start_button.background_normal = start_button_logo_name

    def start_simulation(self, *args):
        print(f"start_simulation")
        if not self.in_simulation:
            self.in_simulation = True
            print('Starting simulation...')
            self.update_start_button()
            # Schedule the update_grid method to be called every 1 second
            Clock.schedule_interval(self.simulation.update_grid, 1)
        else:
            self.in_simulation = False
            print('Pausing simulation...')
            self.update_start_button()
            # Stop the clock
            Clock.unschedule(self.simulation.update_grid)


# Run the app
if __name__ == '__main__':
    EvolutionSimulationApp().run()
