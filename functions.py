import json
import random
from typing import List

import numpy as np

from kivy.config import Config
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown

Config.set('graphics', 'resizable', '0')
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
from config import *

Window.size = (window_width, window_height)
Window.minimum_width, Window.minimum_height = Window.size
Window.clearcolor = window_background_color


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
    start_btn_logo = StringProperty()
    restart_btn_logo = StringProperty()
    reset_btn_logo = StringProperty()
    save_btn_logo = StringProperty()
    predefined_btn_logo = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_btn_logo = start_button_logo_name
        self.restart_btn_logo = restart_button_logo_name
        self.reset_btn_logo = reset_button_logo_name
        self.save_btn_logo = save_button_logo_name
        self.predefined_btn_logo = predefined_button_logo_name
        self.dropdown_button = None

    def on_kv_post(self, *args):
        # Get the main button to open the dropdown menu
        self.dropdown_button = self.parent.ids.id_button_Predefined_initial_state
        self.right_dopdown_menu()

    def right_dopdown_menu(self):
        dropdown = DropDown()

        with open('resources/logs/predefined_states.json', 'r') as f:
            predefined_states = json.load(f)

        for itm in predefined_states:
            # Create buttons and Add them to the dropdown menu
            dropdown.add_widget(Button(text=itm['name'], size_hint_y=None, height=44))

        # Attach the dropdown menu to the main button
        self.dropdown_button.bind(on_release=dropdown.open)


class GridZoneLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = window_height * GridZoneLayout_height_proportion
        self.width = window_width * GridZoneLayout_width_proportion


# Define a custom grid layout class with a method to change the background color of a cell
def remove_duplicates_rect(rect_list: List[Rectangle]) -> list:
    return list(set(rect_list))


class SimulationBoxLayout(BoxLayout):
    generation = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_button = None
        self.rect_width_size = None
        self.rect_height_size = None
        self.nb_rows = 50
        self.nb_cols = 2 * self.nb_rows
        self.horizontal_lines_coords = []
        self.vertical_lines_coords = []
        self.rectangles_list_in_canvas = []
        self.active_rectangles_list = []
        self.all_rectangles_list = []
        self.rectangles_to_be_active_in_next_generation = []
        self.rectangles_to_deactivate_in_next_generation = []
        self.generation_default = "GEN:"
        self.generation = self.generation_default
        self.generation_number = 0
        self.in_simulation = False
        self.run_interval_seconds = run_interval_seconds

    def on_kv_post(self, *args):
        # When Layouts are rendered then...
        # Get starting button
        self.start_button = self.parent.parent.ids.id_start_button

        self.size = self.parent.size
        # Generate grid
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
            new_rect = Rectangle(pos=(x, y), size=(w, h), color=(1, 1, 1, 1))
            self.rectangles_list_in_canvas.append(new_rect)
            # Replace the old rectangle in all_rectangles_list by the new one
            existing_rect = self.get_rect_from_list(obj=new_rect, rect_list=self.all_rectangles_list)
            if existing_rect is not None:
                self.all_rectangles_list.remove(existing_rect)
                self.all_rectangles_list.append(new_rect)

    def draw_horizontal_and_vertical_lines(self):
        x0 = 0
        y0 = 0
        for i in range(self.nb_cols + 1):
            self.init_vertical_line(x0=x0, y1=self.size[1])
            x0 += self.rect_width_size
        for i in range(self.nb_rows + 1):
            self.init_horizontal_line(x1=self.size[0], y0=y0)
            y0 += self.rect_height_size

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
        self.all_rectangles_list = self.rectangles_list_in_canvas.copy()
        self.draw_horizontal_and_vertical_lines()  # Drawing horizontal and vertical lines as borders

    def is_touch_inside_current_layout(self, touch) -> bool:
        return touch.y <= self.height

    def get_rect_from_list(self, obj, rect_list: list):
        """
        If the given a Rectangle object or a tuple with (x, y) coordinates is found in the list rect_list, then
         it that (found) rectangle is returned; else None is returned
        :param obj: A Kivy Rectangle object or a tuple coordinates (x, y)
        :param rect_list: List a Kivy Rectangles object
        :return:
        """
        rect_xy = obj
        _rect = None
        if isinstance(obj, Rectangle):
            # print(f"Rectangle given: {obj.pos}")
            # If Rectangle given, then
            rect_xy = obj.pos
            tl = 1 / 10000  # tolerance
            _rect = [r for r in rect_list if abs(rect_xy[0] - r.pos[0]) <= tl and abs(rect_xy[1] - r.pos[1]) <= tl]
        else:
            # print(f"Tuple given: {obj}")
            _rect = [r for r in rect_list if (rect_xy[0] - self.rect_width_size) <= r.pos[0] <= rect_xy[0]
                     and (rect_xy[1] - self.rect_height_size) <= r.pos[1] <= rect_xy[1]]

        if _rect is None:
            return None

        if len(_rect) == 1:
            return _rect[0]

        return None

    def activate_rectangle(self, rect: Rectangle):
        """
         Remove the rectangle from the grid (canvas) to have a black rectangle shape
         Add the removed rectangle to the list of active rectangle
        :param rect:
        :return:
        """
        # Remove from the grid
        self.canvas.remove(rect)
        # print(f"rect: {rect.pos}")
        # print(f"rectangles_list_in_canvas: {[r.pos for r in self.rectangles_list_in_canvas]}")
        # print(f"active_rectangles_list: {[r.pos for r in self.active_rectangles_list]}")
        self.rectangles_list_in_canvas.remove(rect)
        # Add to  list of active rectangles
        self.active_rectangles_list.append(rect)

    def deactivate_rectangle(self, rect: Rectangle):
        """
         Remove rectangle from active rectangles list
         Recreate and place a new rectangle with the same properties as the given rectangle on the grid
        :param rect:
        :return:
        """
        # Create and add the new rectangle to the grid
        self.init_rectangle(x=rect.pos[0], y=rect.pos[1],
                            w=self.rect_width_size, h=self.rect_height_size)
        # Remove rectangle from the list of active rectangle
        self.active_rectangles_list.remove(rect)

    def is_rectangle_active(self, obj):
        return self.get_rect_from_list(obj=obj, rect_list=self.active_rectangles_list) is not None

    def update_rectangle_status_on_touch(self, obj) -> None:
        if self.is_rectangle_active(obj):  # It was active, so we deactivate it
            self.deactivate_rectangle(rect=obj)
        else:  # It was not active, so we activate it
            self.activate_rectangle(rect=obj)

        # Redraw horizontal and vertical lines
        self.draw_horizontal_and_vertical_lines()

    def get_surrounding_cells_list(self, rect: Rectangle) -> [Rectangle]:
        """
        This function returns the list of all rectangles touching the rectangle given in argument 'rect'
        :param rect:
        :return:
        """
        # tl = 1 / 1000000
        rect_list = []
        rect_x, rect_y = rect.pos

        # 1  2  3
        # 4  r  6
        # 7  8  9
        # r is the rectangle of interest
        # Each rectangle is surrounded by at most 8 others rectangles
        # We start by the bottom left rectangle, progress left to right, down to up, and finish by the top right
        ws, hs = self.rect_width_size, self.rect_height_size

        start_x = rect_x - ws
        start_y = rect_y - hs

        end_x = rect_x + ws
        end_y = rect_y + hs

        list_x = [start_x + i * ws for i in range(3)]
        list_y = [start_y + i * hs for i in range(3)]

        count_rect = 1  # the 5th rectangle should be skipped as it refers to the rectangle of interest ('rect' param)
        for y in list_y:
            for x in list_x:
                if count_rect != 5:  # skipping the 5th rectangle
                    # Only try to get a rectangle if the coordinates (x, y) is not referring
                    # to a rectangle outside the grid
                    # the ws/2 and hs/2 are there as tolerances (a bit big but still fair) to avoid prevent not getting
                    # a rectangle due to Python comparison. could have also used tolerance = 1/10000 instead
                    if 0 <= x <= end_x + ws / 2 and 0 <= y <= end_y + hs / 2:
                        # print(f"iter {count_rect} / x, y: {x, y}")
                        current_rect = self.get_rect_from_list(obj=(x + ws / 2, y + hs / 2),
                                                               rect_list=self.all_rectangles_list)
                        # Normally current_rect should always contain a Rectangle instance.
                        # But let's just test with an if
                        if current_rect:
                            rect_list.append(current_rect)
                count_rect += 1

        return rect_list

    def get_number_of_close_active_rect_of(self, rect: Rectangle):
        list_surrounding_rect = self.get_surrounding_cells_list(rect=rect)

        list_active_rect = [r for r in list_surrounding_rect if self.is_rectangle_active(obj=r)]

        return len(list_active_rect)

    def is_rectangle_next_state_active(self, rect: Rectangle) -> bool:
        # print("-- is_rectangle_next_state_active--")
        number_of_close_active_rect = self.get_number_of_close_active_rect_of(rect=rect)
        is_rect_active = self.is_rectangle_active(obj=rect)

        if (is_rect_active and number_of_close_active_rect in [2, 3]) or \
                (not is_rect_active and number_of_close_active_rect == 3):
            return True
        else:
            return False

    def evaluate_grid_next_state(self) -> None:
        """
        Evaluate the status (active?) of each rectangle for the next generation
         Refresh list of active rectangles that will remain active in the next generation
         Refresh list of active rectangles that will be deactivated in the next generation
         Refresh list of no-active rectangles that will be activated in the next generation
        :return:
        """
        # print("------------ evaluate_grid_next_state")
        # Get list of active rectangles to keep active in the next generation
        active_rectangles_to_keep_active = [r for r in self.active_rectangles_list
                                            if self.is_rectangle_next_state_active(rect=r)]

        # Get list of non-active rectangles to be active in the next generation
        # get list of rectangles close to each active rectangles
        list_close_rect = [[rect for rect in self.get_surrounding_cells_list(r)] for r in self.active_rectangles_list]
        list_close_rect = [r[i] for r in list_close_rect for i in range(len(r))]
        # print(f"list_close_rect: {[r.pos for r in list_close_rect]}")
        list_close_rect = remove_duplicates_rect(rect_list=list_close_rect)
        # print(f"After remove_duplicates_rect list_close_rect: {[r.pos for r in list_close_rect]}")
        nonactive_rectangles_to_be_activated = [r for r in list_close_rect if
                                                self.is_rectangle_next_state_active(rect=r)]
        # print(f"nonactive_rectangles_to_be_activated: {[r.pos for r in nonactive_rectangles_to_be_activated]}")
        # List of all rectangles to be activated in the next generation
        self.rectangles_to_be_active_in_next_generation = active_rectangles_to_keep_active + \
                                                          nonactive_rectangles_to_be_activated

        # Get list of active rectangles to be deactivated in the next generation
        # Those are active rectangles that are not in the list of rectangles to be activated in the next generation
        self.rectangles_to_deactivate_in_next_generation = [r for r in self.active_rectangles_list
                                                            if r not in self.rectangles_to_be_active_in_next_generation]

    def on_touch_down(self, touch):
        """
         change cell color
         if cell was active then remove it from active cells list and add it to the list of non-active cells
         if cell was not active then remove it from non-active cells list and add it to the list of active cells
         Evaluate the next state of the grid
        :param touch:
        :return:
        """
        if self.is_touch_inside_current_layout(touch):
            # print(f"-------------------on_touch_down-----------------------")

            # Get the clicked rectangle
            touched_rect = self.get_rect_from_list(obj=touch.pos, rect_list=self.all_rectangles_list)

            if touched_rect is not None:
                # print(f"touched_rect: {touched_rect.pos}")
                # Since we got the touched rectangle, now we need to change it's color by activating or deactivating it
                self.update_rectangle_status_on_touch(obj=touched_rect)  # Updating new status: black or white

                # Evaluate the next state of the grid
                self.evaluate_grid_next_state()

                # print(f"AF EV - rectangles_list_in_canvas: {[r.pos for r in self.rectangles_list_in_canvas]}")
                # print(f"AF EV - active_rectangles_list: {[r.pos for r in self.active_rectangles_list]}")
                # print(f"AF EV - self.rectangles_to_be_active_in_next_generation: "
                #       f"{[r.pos for r in self.rectangles_to_be_active_in_next_generation]}")

            else:
                print(f"ERROR: No rectangle found at this coordinate: {touch.pos}")

    def update_grid(self, *args):
        # Get list rectangles to be active at the next generation
        # current active rectangles that are not in the list of rectangles to be activated at the next generation
        # those should be deactivated during the update
        self.rectangles_to_deactivate_in_next_generation = [r for r in self.active_rectangles_list
                                                            if r not in self.rectangles_to_be_active_in_next_generation]

        self.rectangles_to_be_active_in_next_generation = remove_duplicates_rect(
            self.rectangles_to_be_active_in_next_generation)
        self.rectangles_to_deactivate_in_next_generation = remove_duplicates_rect(
            self.rectangles_to_deactivate_in_next_generation)

        # Activate cells
        list_rect_to_activate = [self.get_rect_from_list(
            obj=r, rect_list=self.all_rectangles_list) for r in self.rectangles_to_be_active_in_next_generation]
        for rect in list_rect_to_activate:
            if not self.is_rectangle_active(obj=rect):
                self.activate_rectangle(rect=rect)

        # deactivate cells
        list_rect_to_deactivate = [self.get_rect_from_list(
            obj=r, rect_list=self.all_rectangles_list) for r in self.rectangles_to_deactivate_in_next_generation]
        for rect in list_rect_to_deactivate:
            self.deactivate_rectangle(rect=rect)

        # Redraw horizontal and vertical lines
        self.draw_horizontal_and_vertical_lines()

        self.canvas.ask_update()

        self.generation_number += 1
        self.generation = f"{self.generation_default}: {self.generation_number}"

        # Evaluate grid for next generation
        self.evaluate_grid_next_state()

    # def update_start_button(self):
    #     # <a target="_blank" href="https://icons8.com/icon/60449/play-button-circled">Play Button Circled</a>
    #     # icon by <a target="_blank" href="https://icons8.com">Icons8</a>
    #     if self.in_simulation:
    #         self.start_button.background_normal = pause_button_logo_name
    #     else:
    #         self.start_button.background_normal = start_button_logo_name

    # def start_simulation(self):
    #     if not self.in_simulation:
    #         self.in_simulation = True
    #         print('Starting simulation...')
    #         self.update_start_button()
    #     else:
    #         self.in_simulation = False
    #         print('Pausing simulation...')
    #         self.update_start_button()

    # def start(self):
    #     # Defining job to do every a certain amount of time
    #     schedule.every(self.run_interval_seconds).seconds.do(self.start_simulation)
    #
    #     while self.in_simulation:
    #         schedule.run_pending()
    #         time.sleep(.5)

    def reset_grid(self) -> None:
        """
        Reset the grid by deactivating all active cells (rectangles)
        :return:
        """
        if not self.in_simulation:
            to_be_deactivated = self.active_rectangles_list.copy()
            [self.deactivate_rectangle(rect=r) for r in to_be_deactivated]
            self.draw_horizontal_and_vertical_lines()  # Redraw horizontal and vertical lines

            # Reset generation counter
            self.generation_number = 0
            self.generation = self.generation_default
