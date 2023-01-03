import json
import random

from kivy.config import Config
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown

Config.set('graphics', 'resizable', '0')
from kivy.core.window import Window
import time

import schedule
from kivy.app import App
from kivy.graphics import Rectangle, Color, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window

window_width = 1480
window_height = 800
Window.size = (window_width, window_height)
Window.minimum_width, Window.minimum_height = Window.size
Window.clearcolor = (.1, .1, .1, 1)

HorizontalMenuLayout_height_proportion = .07
HorizontalMenuLayout_width_proportion = 1
GridZoneLayout_height_proportion = 1 - HorizontalMenuLayout_height_proportion
GridZoneLayout_width_proportion = 1


# Create a custom widget to hold the grid
class MainInterface(BoxLayout):
    pass


def save_initial_sate(active_cells_coord: list):
    with open('resources/logs/predefined_states.json', 'r') as f:
        predefined_states = json.load(f)

    predefined_states.append(active_cells_coord)

    with open('resources/logs/predefined_states.json', 'w'):
        json.dump(predefined_states)


class HorizontalMenuLayout(RelativeLayout):
    gen_label = StringProperty('Gen')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_button = None
        self.gen_label = "Gen: "

    def on_kv_post(self, *args):
        # Get the main button to open the dropdown menu
        self.dropdown_button = self.parent.ids.id_button_Predefined_initial_state

        self.right_dopdown_menu()

    def start_simulation(self):
        print("start_simulation")

    def right_dopdown_menu(self):
        dropdown = DropDown()

        with open('resources/logs/predefined_states.json', 'r') as f:
            predefined_states = json.load(f)

        for itm in predefined_states:
            # Create buttons and Add them to the dropdown menu
            dropdown.add_widget(Button(text=itm['name'], size_hint_y=None, height=44))

        # Attach the dropdown menu to the main button
        self.dropdown_button.bind(on_release=dropdown.open)


# Define a custom button class with a background color property
class CellRectangle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._color = (0, 0, 0, 0)  # Transparent to let visible a white background
        self._size = (200, 200)
        self._position = (0, 0)
        self.is_active = False
        # Create a widget to hold the rectangle
        self.rectangle_widget = Widget()
        with self.rectangle_widget.canvas:
            # Create the rectangle object
            self.rectangle = Rectangle(size=(200, 300), color=(1, 0, 1, 1))
        self.bind(on_press=self.on_press)
        self.add_widget(self.rectangle_widget)  # Add the rectangle_widget widget to the CellRectangle class

    def on_press(self):
        print('on_press')
        # Change the background color of the clicked cell
        if self.is_active:
            self.rectangle.color = (0, 0, 0, 0)  # transparent
            self.is_active = False
        else:
            self.rectangle.color = (0, 0, 0, 1)  # black
            self.is_active = True


class GridZoneLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = window_height * GridZoneLayout_height_proportion
        self.width = window_width * GridZoneLayout_width_proportion


# Define a custom grid layout class with a method to change the background color of a cell
class SimulationGridLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rect_width_size = None
        self.rect_height_size = None
        self.nb_rows = 50
        self.nb_cols = 2 * self.nb_rows
        self.horizontal_lines_coords = []
        self.vertical_lines_coords = []
        self.rectangles_list_in_canvas = []
        self.active_rectangle_pos_list = []
        self.all_rectangles_list = []
        self.rectangles_with_next_new_state = []  # [dict(next_state: activate|deactivate, rect: Rectangle)]

    def on_kv_post(self, *args):
        # When Layouts are rendered then...
        self.size = self.parent.size
        self.generate_grid()

    def init_vertical_line(self, x0: float, y1: float, y0=0):
        self.vertical_lines_coords.append([x0, y0, x0, y1])
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=(x0, y0, x0, y1), width=1)

    def init_horizontal_line(self, x1: float, y0: float, x0=0):
        self.horizontal_lines_coords.append([x0, y0, x1, y0])
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=(x0, y0, x1, y0), width=1)

    def init_rectangle(self, x: float, y: float, w: float, h: float):
        with self.canvas:
            # Color(random.choice([0, 1]), random.choice([0, 1]), random.choice([0, 1]), 1)
            Color(1, 1, 1, 1)
            rect = Rectangle(pos=(x, y), size=(w, h), color=(1, 1, 1, 1))
            self.rectangles_list_in_canvas.append(rect)
            if rect in self.active_rectangle_pos_list:
                self.active_rectangle_pos_list.remove(rect)  # Then activate the corresponding cell
                # by removing it (to have a black cell)

    def get_pressed_rectangle(self, press_x: float, press_y: float):
        pressed_rect = [rect for rect in self.rectangles_list_in_canvas if rect.pos[0] <= press_x <= rect.pos[
            0] + self.rect_width_size and rect.pos[1] <= press_y <= rect.pos[1] + self.rect_height_size]

        if pressed_rect:
            return pressed_rect[0]
        else:
            return None

    def activate_rect(self, rect: Rectangle):
        self.canvas.remove(rect)  # activate
        self.rectangles_list_in_canvas.remove(rect)
        self.active_rectangle_pos_list.append(rect)

    def deactivate_rect(self, rect: Rectangle):
        with self.canvas:
            # Color((1, 1, 1, 0))
            self.init_rectangle(x=rect.pos[0], y=rect.pos[1],
                                w=self.rect_width_size, h=self.rect_height_size)

    def get_rectangle_from_removed_list(self, press_x: float, press_y: float):
        rmd_rect = [rect for rect in self.active_rectangle_pos_list if rect.pos[0] <= press_x <= rect.pos[
            0] + self.rect_width_size and rect.pos[1] <= press_y <= rect.pos[1] + self.rect_height_size]

        if rmd_rect:
            return rmd_rect[0]
        else:
            return None

    def is_touch_inside_current_layout(self, touch) -> bool:
        return touch.y <= self.height

    def on_touch_down(self, touch):
        if self.is_touch_inside_current_layout(touch):
            rect = self.get_pressed_rectangle(press_x=touch.x, press_y=touch.y)

            if rect is not None:
                # print(f"Found rectangle with position: {rect.pos}")
                self.activate_rect(rect=rect)
            else:
                # print(f"Not found rectangle with position")
                rect = self.get_rectangle_from_removed_list(press_x=touch.x, press_y=touch.y)
                # print(f"Found removed rectangle with position: {rect.pos}")
                if rect is not None:
                    self.deactivate_rect(rect=rect)
                else:
                    print("Error: No rectangle found")

            if rect is not None:
                self.canvas.ask_update()

    def get_surrounding_cells_list(self, rect: Rectangle) -> [Rectangle]:
        """
        This function returns the list of all rectangles touching the rectangle given in argument 'rect'
        :param rect:
        :return:
        """
        tl = 1 / 1000000
        rect_list = [Rectangle]
        rect_x, rect_y = rect.pos

        # 1  2  3
        # 4  r  6
        # 7  8  9
        # r is the rectangle of interest
        # Each rectangle is surrounded by at most 8 others rectangles
        # We start by the bottom left rectangle, progress left to right, down to up, and finish by the top right
        start_x = rect_x - self.rect_width_size
        start_y = rect_y - self.rect_height_size

        end_x = rect_x + self.rect_width_size
        end_y = rect_y + self.rect_height_size

        list_x = [start_x + i * self.rect_width_size for i in range(3)]
        list_y = [start_y + i * self.rect_height_size for i in range(3)]

        for y in list_y:
            for x in list_x:
                # Only try to get a rectangle if the coordinates (x, y) is not referring to a rectangle outside the grid
                if 0 <= x <= end_x and 0 <= y <= end_y:
                    current_rect = [r for r in self.all_rectangles_list if (r.pos[0]-x) <= tl and (r.pos[1]-y) <= tl]
                    # Normally current_rect should always contain a Rectangle instance. But let's just test with an if
                    if current_rect:
                        rect_list.append(current_rect[0])

        return rect_list

    def get_number_of_close_active_rect_of(self, rect: Rectangle):
        return len(self.get_surrounding_cells_list(rect=rect))

    # def is_rectangle_active(self, rect: Rectangle) -> bool:
    #     return rect in self.

    def evaluate_rect_next_state(self, rect: Rectangle):
        number_of_close_active_rect = self.get_number_of_close_active_rect_of(rect=rect)
        if (self.is_active and self.number_of_close_active_cells in [2, 3]) or \
                (not self.is_active and self.number_of_close_active_cells == 3):
            self.next_state_activate = True
            self.text_size = '1'
        else:
            self.next_state_activate = False
            self.text_size = '0'

    def evaluate_grid_next_state(self):
        self.rectangles_with_next_new_state = []

    def generate_grid(self):
        w, h = self.size
        self.rect_height_size = h / self.nb_rows
        self.rect_width_size = w / self.nb_cols

        y = 0
        for i in range(self.nb_rows):  # rows: y
            x = 0
            for j in range(self.nb_cols):  # cols: x
                self.init_rectangle(x=x, y=y, w=self.rect_width_size, h=self.rect_height_size)
                x += self.rect_width_size
            y += self.rect_height_size

        # After generating the list of rectangles, make a copy of it. This copy should never be changed
        self.all_rectangles_list = self.active_rectangle_pos_list.copy()
        x0 = 0
        y0 = 0
        for i in range(self.nb_cols + 1):
            self.init_vertical_line(x0=x0, y1=self.size[1])
            x0 += self.rect_width_size
        for i in range(self.nb_rows + 1):
            self.init_horizontal_line(x1=self.size[0], y0=y0)
            y0 += self.rect_height_size


class EvolutionSimulationApp(App):
    pass
