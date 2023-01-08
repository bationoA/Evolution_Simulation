import datetime
import json
from typing import List

from kivy.config import Config
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.graphics import Rectangle, Color, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.toast import toast
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from config import *

Config.set('graphics', 'resizable', '0')

Window.size = (window_width, window_height)
Window.minimum_width, Window.minimum_height = Window.size
Window.maximum_width, Window.maximum_height = Window.size

Window.clearcolor = window_background_color


# Create a custom widget to hold the grid
class MainInterface(MDBoxLayout):
    pass


# Define a custom grid layout class with a method to change the background color of a cell
def remove_duplicates_rect(rect_list: List[Rectangle]) -> list:
    return list(set(rect_list))


class StateButton(Button):
    custom_id = ObjectProperty(None)


class HorizontalMenuLayout(MDRelativeLayout):
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
        self.dropdown_items = []
        self.dropdown_items_custom_ids = []

    def on_kv_post(self, *args):
        # Get the main button to open the dropdown menu
        self.dropdown_button = self.parent.ids.id_button_bookmarks_state
        # self.dropdown_button.opacity = 1
        # self.dropdown_button.disabled = False
        self.right_dopdown_menu()

    def right_dopdown_menu(self):
        dropdown = DropDown()

        with open('resources/logs/saved_states.json', 'r') as f:
            saved_states = json.load(f)

        for itm in saved_states:
            # Create buttons and Add them to the dropdown menu
            btn = StateButton(custom_id=itm['id'], text=itm['name'], size_hint_y=None, height=44)
            self.dropdown_items.append(btn)
            self.dropdown_items_custom_ids.append(itm['id'])
            dropdown.add_widget(btn)

        # Attach the dropdown menu to the main button
        # self.dropdown_button.bind(on_release=self.dropdown.open)
        # dropdown.open(self.dropdown_button)
        self.dropdown_button.bind(on_release=lambda widget: dropdown.open(widget))


class GridZoneLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = window_height * GridZoneLayout_height_proportion
        self.width = window_width * GridZoneLayout_width_proportion


class SaveStateModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glyt = MDGridLayout(rows=1, cols=3, md_bg_color=(1, 1, 1, 1), size_hint=(1, 1), padding=5)
        self.glyt.add_widget(MDLabel(text="Name:", size_hint=(.1, .1)))
        self.text_input = TextInput(multiline=False, font_size=30, size_hint=(.8, .1))
        self.submit_button = Button(text="Save", size_hint=(.1, .1),
                                    color=(1, 1, 1, 1),
                                    background_color=(0, 1, 0, 1))
        self.glyt.add_widget(self.text_input)
        self.glyt.add_widget(widget=self.submit_button)
        self.add_widget(widget=self.glyt)


class DeleteStateModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glyt = MDGridLayout(rows=1, cols=2, md_bg_color=(1, 1, 1, 1), size_hint=(1, 1), padding=5)
        self.cancel = Button(text="Cancel",
                             size_hint=(.7, .1),
                             color=(1, 1, 1, 1),
                             background_color=(0, 0, 1, 1))
        self.yes_delete = Button(text="Yes Delete",
                                 size_hint=(.3, .1),
                                 color=(1, 1, 1, 1),
                                 background_color=(0, 0, 0, 1))
        self.glyt.add_widget(widget=self.cancel)
        self.glyt.add_widget(widget=self.yes_delete)
        self.add_widget(widget=self.glyt)


class SimulationBoxLayout(MDBoxLayout):
    generation = StringProperty()
    # current_selected_state_index = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save_state_text_input = None
        self.save_state_submit_button = None
        self.start_button = None
        self.rect_width_size = None
        self.rect_height_size = None
        self.nb_rows = grid_rows
        self.nb_cols = grid_cols if isinstance(grid_cols, int) else 2 * grid_rows
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
        self.toast_position = None
        self.save_state_modal = SaveStateModal(size_hint=(0.5, 0.08))
        self.save_state_modal_submit_button = self.save_state_modal.submit_button
        self.current_selected_state_index = None
        self.delete_state_modal = DeleteStateModal(size_hint=(0.5, 0.04))
        self.delete_state_modal_yes_button = self.delete_state_modal.yes_delete
        self.delete_state_modal_cancel_button = self.delete_state_modal.cancel

    def on_kv_post(self, *args):
        # When Layouts are rendered then...
        # Get starting button
        self.start_button = self.parent.parent.ids.id_button_save

        print(f"self.delete_state_modal_yes_button: {self.delete_state_modal_yes_button}")
        print(f"self.delete_state_modal_cancel_button: {self.delete_state_modal_cancel_button}")
        self.save_state_modal_submit_button.bind(on_release=self.save_sate)
        self.delete_state_modal_yes_button.bind(on_release=self.delete_state)
        self.delete_state_modal_cancel_button.bind(on_release=self.cancel_delete_state)

        # Get Save button position
        save_button = self.parent.parent.ids.id_start_button
        self.toast_position = (save_button.pos[0], save_button.pos[1] - .02)

        self.size = self.parent.size
        # Generate grid
        self.generate_grid()

        #
        self.bind_dorpdown_items_to_action()

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

    def bind_dorpdown_items_to_action(self):
        horizontal_menu_layout = self.parent.parent.ids.id_HorizontalMenuLayout
        if horizontal_menu_layout.dropdown_items:
            for btn in horizontal_menu_layout.dropdown_items:
                btn.bind(on_release=self.load_state)

    def load_state(self, *args):
        horizontal_menu_layout = self.parent.parent.ids.id_HorizontalMenuLayout
        dropdown_items = horizontal_menu_layout.dropdown_items
        btn_ids_list = horizontal_menu_layout.dropdown_items_custom_ids
        btn = args
        btn_address = str(btn).split('at')[-1].replace('>,)', '')
        index = [dropdown_items.index(b) for b in dropdown_items if btn_address in str(b)]
        if index:
            index = index[0]
            state = None
            # Get state
            try:
                with open('resources/logs/saved_states.json', 'r') as f:
                    states = json.load(f)

                state = [st for st in states if st['id'] == str(btn_ids_list[index])]
            except Exception as e:
                print(f"Error: {str(e)}")

            if state:
                state = state[0]
                # Reset the grid
                self.reset_grid()
                # get and activate the cells related to the state
                for pos in state['coordinates']:
                    rect = self.get_rect_from_list(obj=pos, rect_list=self.all_rectangles_list, as_rectangle=True)
                    self.activate_rectangle(rect=rect)

                # Toast message: Loaded
                self.show_toast(message="Loaded", bg_col=[0, 0, 0, .5])

                # Evaluate grid next status
                self.evaluate_grid_next_state()

                self.current_selected_state_index = index
            else:
                msg = "Unable to load the state"
                self.show_toast(message=msg, bg_col=[1, 0, 0, .5])
                print(msg)
        else:
            msg = f"Error: load_state - index = {index} in dropdown_items: {dropdown_items}"
            self.show_toast(message=msg, bg_col=[1, 0, 0, .5])
            print(msg)

    def save_sate(self, *args):
        self.show_toast(message="Saving...", bg_col=[0, 0, 0, .5])
        success = True
        index = str(datetime.datetime.now().timestamp())
        name = self.save_state_modal.text_input.text
        rects_position = [r.pos for r in self.active_rectangles_list]
        state = dict(id=index,
                     name=name,
                     coordinates=rects_position
                     )
        try:
            with open('resources/logs/saved_states.json', 'r') as f:
                states = json.load(f)
            states.append(state)

            with open('resources/logs/saved_states.json', 'w') as f:
                json.dump(states, f, indent=4, sort_keys=True)
        except Exception as e:
            success = False
            print("An Error occurred while saving")
            print(str(e))
            self.show_toast(message="An Error occurred while saving", bg_col=[1, 0, 0, .5])

        if success:
            self.current_selected_state_index = index  # So that the user can delete it right after it's create
            self.save_state_modal.dismiss()
            self.show_toast(message="State saved.")
            # Refresh dropdown menu items list
            self.parent.parent.ids.id_HorizontalMenuLayout.right_dopdown_menu()
            # Bind action to items
            self.bind_dorpdown_items_to_action()
        return success

    def delete_state(self, *args):
        success = True
        try:
            with open('resources/logs/saved_states.json', 'r') as f:
                states = json.load(f)
            states.remove(states[int(self.current_selected_state_index)])

            with open('resources/logs/saved_states.json', 'w') as f:
                json.dump(states, f, indent=4, sort_keys=True)
        except Exception as e:
            success = False
            print("An Error occurred while deleting")
            print(str(e))
            self.show_toast(message="An Error occurred while deleting", bg_col=[1, 0, 0, .5])

        if success:
            self.show_toast(message="State removed", )
            # Refresh dropdown menu items list
            self.parent.parent.ids.id_HorizontalMenuLayout.right_dopdown_menu()
            # Bind action to items
            self.bind_dorpdown_items_to_action()

        self.delete_state_modal.dismiss()  # close delete state modal

    def cancel_delete_state(self, *args):
        self.delete_state_modal.dismiss()

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

    def get_rect_from_list(self, obj, rect_list: list, as_rectangle=False):
        """
        If the given a Rectangle object or a tuple with (x, y) coordinates is found in the list rect_list, then
         it that (found) rectangle is returned; else None is returned
        :param obj: A Kivy Rectangle object or a tuple coordinates (x, y)
        :param rect_list: List a Kivy Rectangles object
        :param as_rectangle:
        :return:
        """
        rect_xy = obj
        _rect = None
        if isinstance(obj, Rectangle) or as_rectangle:
            # print(f"Rectangle given: {obj.pos}")
            # If Rectangle given, then
            if isinstance(obj, Rectangle):
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
        self.current_selected_state_index = None  # Set to " to prevent accidental deletion

        # Remove from the grid
        self.canvas.remove(rect)
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
        self.current_selected_state_index = None  # Set to None to prevent accidental deletion

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

    def show_toast(self, message, bg_col=None):
        if bg_col is None:
            bg_col = [0, 1, 0, .5]
        toast(text=message,
              background=bg_col
              )

    def reset_grid(self):
        to_be_deactivated = self.active_rectangles_list.copy()
        [self.deactivate_rectangle(rect=r) for r in to_be_deactivated]
        self.draw_horizontal_and_vertical_lines()  # Redraw horizontal and vertical lines

        # Reset generation counter
        self.generation_number = 0
        self.generation = self.generation_default

        # Delete al active cells and run a next state evaluation to reset 'to be activate' and 'desactivated' list
        self.evaluate_grid_next_state()
