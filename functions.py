import datetime
import json
import os.path
import sys

import numpy as np
import pyqtree
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.graphics import Rectangle, Color, Line
from kivy.uix.button import Button
from kivymd.toast import toast
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
def remove_duplicates(_list: list) -> list:
    """
    Remove duplicates from the list
    :param _list: List
    :return:
    """
    return list(set(_list))


def remove_cell_by_id_from(_id, cells_list: list) -> list:
    _cells_list = cells_list.copy()
    cell = [_cells_list.index(c) for c in _cells_list if c.custom_id == _id]
    _cells_list.remove(cell[0])
    return _cells_list


class StateButton(Button):
    custom_id = ObjectProperty(None)


class HorizontalMenuLayout(MDRelativeLayout):
    start_btn_logo = StringProperty()
    restart_btn_logo = StringProperty()
    reset_btn_logo = StringProperty()
    save_btn_logo = StringProperty()
    bookmarks_btn_logo = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_btn_logo = start_button_logo_name
        self.restart_btn_logo = restart_button_logo_name
        self.reset_btn_logo = reset_button_logo_name
        self.save_btn_logo = save_button_logo_name
        self.delete_btn_logo = delete_button_logo_name
        self.bookmarks_btn_logo = bookmarks_button_logo_name
        self.dropdown_menu = None
        self.dropdown_button = None
        self.dropdown_items = []
        self.dropdown_items_custom_ids = []

    def on_kv_post(self, *args):
        # Get the main button to open the dropdown menu
        self.dropdown_button = self.parent.ids.id_button_bookmarks_state
        self.right_dopdown_menu()

    def right_dopdown_menu(self, updating=False):
        if updating:
            # Remove an item from the list
            self.dropdown_menu.clear_widgets()
        else:
            self.dropdown_menu = DropDown(size_hint = (1, 0.5))
            self.dropdown_menu.size_hint_min_y = 1

        with open('resources/logs/saved_states.json', 'r') as f:
            saved_states = json.load(f)

        for itm in saved_states:
            # Create buttons and Add them to the dropdown menu
            btn = StateButton(custom_id=itm['id'], text=itm['name'], size_hint_y=None, height=44)
            self.dropdown_items.append(btn)
            self.dropdown_items_custom_ids.append(itm['id'])
            self.dropdown_menu.add_widget(btn)

        # Attach the dropdown menu to the main button
        if not updating:  # if updating then this operation was already done when the app started
            # Bind button to dropdown to open on click
            self.dropdown_button.bind(on_release=lambda widget: self.dropdown_menu.open(widget))


class GridZoneLayout(MDBoxLayout):
    screenshot_button_image = StringProperty(screenshot_button_image_name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = window_height * GridZoneLayout_height_proportion
        self.width = window_width * GridZoneLayout_width_proportion

    def screenshot_grid(self, filename=None):
        success = True
        filename = f"Game-of-Life-saved-grid-state-image-{datetime.datetime.now()}.png" if filename is None else filename
        filename = os.path.join(outputs_images_dir, filename)
        # Export the layout to a PNG image
        try:
            self.export_to_png(filename=filename)
        except Exception as e:
            success = False
            msg = f"Error while exporting grid as png: {str(e)}"
            print(msg)
            show_toast(message=msg, duration=5)

        if success:
            msg = f"Grid successfully exported as png at: {filename}"
            print(msg)
            show_toast(message=msg, duration=5)


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


class LoadingModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glyt = MDGridLayout(rows=3, cols=1, md_bg_color=(1, 1, 1, 1), size_hint=(1, 1), padding=5)
        # loading image
        self.loading_image = Image(source=loading_image_name)

        # Progress percent...
        self.loadin_text_label = Label(text="Loading...",
                                       color=(0, 0, 0, 1),
                                       size_hint=(.4, 1),
                                       pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                       font_size=24)

        self.progress_percent_label = Label(text="-",
                                            color=(0, 0, 0, 1),
                                            size_hint=(.5, 1),
                                            pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                            font_size=24)
        # adding image to widget
        self.glyt.add_widget(self.loadin_text_label)
        self.glyt.add_widget(self.loading_image)
        self.glyt.add_widget(self.progress_percent_label)
        self.add_widget(self.glyt)


class CellWidget(Widget):
    def __init__(self, custom_id, pos: tuple, size: tuple, **kwargs):
        super().__init__(**kwargs)
        self.custom_id = custom_id
        self.size_hint = (None, None)
        self.pos = pos
        self.size = size
        self._is_active = False
        self.change_state_next = False
        self.bind(on_change=self.update)
        self.bind(on_touch_down=self.on_cell_click)

        with self.canvas:
            self.color = Color(rgba=deactivated_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value
        if self.on_change:  # call the callback function if it is set
            self.on_change(self, value)

    def update(self, *args):
        self.change_color()
        self.canvas.ask_update()

    def change_color(self):
        if self._is_active:  # black
            self.color.rgba = deactivated_color  # deactivate
            self._is_active = False
        else:
            self.color.rgba = activated_color  # activate
            self._is_active = True

    def custom_collide_point(self, x, y) -> bool:
        return self.rect.pos[0] <= x <= self.rect.pos[0] + self.rect.size[0] and \
               self.rect.pos[1] <= y <= self.rect.pos[1] + self.rect.size[1]

    def on_cell_click(self, widget, touch):
        if self.custom_collide_point(*touch.pos):
            self.update()


def show_toast(message, bg_col=None, duration=.8):
    """

    :param message:
    :param bg_col:
    :param duration: seconds before dismissing toast
    :return:
    """
    if bg_col is None:
        bg_col = [0, 1, 0, .5]
    toast(text=message,
          background=bg_col,
          duration=duration
          )


class SimulationBoxLayout(MDBoxLayout):
    generation = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accessing_list = []
        self.set_of_surrounding_cells = set()
        self.save_state_text_input = None
        self.save_state_submit_button = None
        self.start_button = None
        self.rect_width_size = None
        self.rect_height_size = None
        self.nb_rows = grid_rows
        self.nb_cols = grid_cols if isinstance(grid_cols, int) else 2 * grid_rows
        self.np_array_all_xmin_ymin_xmax_ymax = np.empty((self.nb_rows, 4))
        self.quadtree_active_cells = pyqtree.Index(bbox=[0, 0, self.width, self.height])
        self.nb_total_cells = self.nb_cols * self.nb_rows
        self.horizontal_lines_coords = []
        self.vertical_lines_coords = []
        self.cells_in_grid = []
        self.cells_xmin_ymin_xmax_ymax_dict = {}
        self.active_cells_list = set()
        self.all_rectangles_list = []
        self.list_surrounding_cells = []
        self.generation_default = "GEN:"
        self.generation = self.generation_default + " 0"
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
        self.loading_modal = LoadingModal(size_hint=(0.2, 0.2), auto_dismiss=False)
        self.initial_state = None
        self.is_stability_reached = False

    def on_kv_post(self, *args):
        # When Layouts are rendered then...
        # Get starting button
        self.start_button = self.parent.parent.ids.id_button_save
        self.save_state_modal_submit_button.bind(on_release=self.save_sate)
        self.delete_state_modal_yes_button.bind(on_release=self.delete_state)
        self.delete_state_modal_cancel_button.bind(on_release=self.cancel_delete_state)

        # Get Save button position
        save_button = self.parent.parent.ids.id_start_button
        self.toast_position = (save_button.pos[0], save_button.pos[1] - .02)

        self.size = self.parent.size

        # Generate grid
        self.generate_grid()

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
        new_id = (x, y, x + w, y + h)
        new_cell = CellWidget(custom_id=new_id, pos=(x, y), size=(w, h))
        self.add_widget(new_cell)
        self.cells_in_grid.append(new_cell)

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
        if not self.in_simulation:
            horizontal_menu_layout = self.parent.parent.ids.id_HorizontalMenuLayout
            dropdown_items = horizontal_menu_layout.dropdown_items
            index = args[0].custom_id
            if index:
                state = None
                # Get state
                try:
                    with open('resources/logs/saved_states.json', 'r') as f:
                        states = json.load(f)

                    state = [st for st in states if st['id'] == index]

                except Exception as e:
                    print(f"Error: {str(e)}")

                if state:
                    state = state[0]
                    self.display_state_on_grid(obj_list=state['coordinates'])
                    self.current_selected_state_index = index
                    # Toast message: Loaded
                    show_toast(message="State loaded", bg_col=[0, 0, 0, .5])
                else:
                    msg = "Unable to load the state"
                    show_toast(message=msg, bg_col=[1, 0, 0, .5])
                    print(msg)
            else:
                msg = f"Error: load_state - index = {index} in dropdown_items: {dropdown_items}"
                show_toast(message=msg, bg_col=[1, 0, 0, .5])
                print(msg)
        else:
            msg = f"Still in simulation..."
            show_toast(message=msg)
            print(msg)

    def display_state_on_grid(self, obj_list, reset_first=True):
        if reset_first:
            # Reset the grid
            self.reset_grid()
        if isinstance(list(obj_list)[0], CellWidget):
            obj_list = [c.rect.pos for c in list(obj_list)]

        # get and activate the cells related to the state
        for pos in obj_list:
            cell = self.get_cell_by_coords_from_all_cells(*pos)
            self.activate_cell(cell=cell)

    def save_sate(self, *args):
        show_toast(message="Saving...", bg_col=[0, 0, 0, .5])
        success = True
        index = str(datetime.datetime.now().timestamp())
        name = self.save_state_modal.text_input.text
        rects_position = [r.rect.pos for r in self.active_cells_list]
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
            show_toast(message="An Error occurred while saving", bg_col=[1, 0, 0, .5])

        if success:
            self.current_selected_state_index = index  # So that the user can delete it right after it's create
            self.save_state_modal.dismiss()
            show_toast(message="State saved.")
            # Refresh dropdown menu items list
            self.parent.parent.ids.id_HorizontalMenuLayout.right_dopdown_menu(updating=True)
            # Bind action to items
            self.bind_dorpdown_items_to_action()
        return success

    def delete_state(self, *args):
        success = True
        try:
            with open('resources/logs/saved_states.json', 'r') as f:
                states = json.load(f)

            states = [s for s in states if s['id'] != self.current_selected_state_index]

            with open('resources/logs/saved_states.json', 'w') as f:
                json.dump(states, f, indent=4, sort_keys=True)
        except Exception as e:
            success = False
            print("An Error occurred while deleting")
            print(str(e))
            show_toast(message="An Error occurred while deleting", bg_col=[1, 0, 0, .5])

        if success:
            show_toast(message="State removed", )
            # Refresh dropdown menu items list
            self.parent.parent.ids.id_HorizontalMenuLayout.right_dopdown_menu(updating=True)
            # Bind action to items
            self.bind_dorpdown_items_to_action()

        self.delete_state_modal.dismiss()  # close delete state modal

    def cancel_delete_state(self, *args):
        self.delete_state_modal.dismiss()

    def load_initial_state(self):
        if self.initial_state is not None:
            # Display
            self.display_state_on_grid(obj_list=self.initial_state)
            show_toast(message="Last initial state reloaded", bg_col=[0, 0, 0, .5])

    def _track_grid_initialization_progress_in_loading_modal(self, value, task_title, in_modal=True):
        # tracking progress...
        _percent = round(100 * value / self.nb_total_cells, 0)
        _percent_text = str(_percent) + "%"
        sys.stdout.write("\rProgress: {}".format(_percent_text))
        sys.stdout.flush()
        if in_modal:
            self.loading_modal.loadin_text_label.text = task_title
            self.loading_modal.progress_percent_label.text = _percent_text
        # ----------

    def generate_grid(self):
        task_title = "Generating grid..."
        print(task_title)
        w, h = self.size
        self.rect_height_size = h / self.nb_rows
        self.rect_width_size = w / self.nb_cols

        k = 1
        y = 0
        for i in range(self.nb_rows):  # rows: y
            x = 0
            for j in range(self.nb_cols):  # cols: x
                # tracking progress...
                self._track_grid_initialization_progress_in_loading_modal(value=k, task_title=task_title, in_modal=False)
                k += 1
                # ----------

                self.init_rectangle(x=x, y=y, w=self.rect_width_size, h=self.rect_height_size)
                x += self.rect_width_size
            y += self.rect_height_size

        print("")

        # After generating the list of rectangles, make a copy of it. This copy should never be changed
        # self.all_rectangles_list = self.cells_in_grid.copy()
        self.draw_horizontal_and_vertical_lines()  # Drawing horizontal and vertical lines as borders

    def load_cells_in_np_2d_array(self):
        task_title = "Optimizing..."
        print(task_title)
        k = 1
        for cell in self.children:
            # tracking progress...
            self._track_grid_initialization_progress_in_loading_modal(value=k, task_title=task_title)
            k += 1
            # ----------

            x, y = cell.rect.pos
            w, h = self.rect_width_size, self.rect_height_size
            xmin, ymin, xmax, ymax = x, y, x + w, y + h
            self.np_array_all_xmin_ymin_xmax_ymax = \
                np.append(self.np_array_all_xmin_ymin_xmax_ymax, [[xmin, ymin, xmax, ymax]], axis=0)
            self.cells_xmin_ymin_xmax_ymax_dict[(xmin, ymin, xmax, ymax)] = cell

        print("")
        self.loading_modal.dismiss()

    # def setup_grid(self, *args):
    #     self.loading_modal.loadin_text_label.text = "task_title"
    #
    #     self.generate_grid()
    #     self.load_cells_in_np_2d_array()
    #     # self.loading_modal.dismiss()

    def is_intersect(self, bbox1, bbox2):
        return (bbox1[0] <= bbox2[2]) & (bbox1[2] >= bbox2[0]) & (bbox1[1] <= bbox2[3]) & (bbox1[3] >= bbox2[1])

    def is_tuples_match(self, tp1: tuple, tp2: tuple, tl=.001):
        return np.abs(np.sum(np.array(tp1) - np.array(tp2))) <= tl

    def get_surrounding_cells_list(self, cell: CellWidget, include_current=False):
        """
        This returns the given cell (if include_current is True) alongside with all cells touching that cell
        :param include_current:
        :param cell:
        :return:
        """
        tl = .001
        x, y = cell.rect.pos
        w, h = self.rect_width_size, self.rect_height_size
        center_x, center_y = x + w / 2, y + h / 2
        center_bbox = (center_x - w, center_y - h, center_x + w, center_y + h)

        # Use the is_intersect function and numpy to get all the bounding
        # boxes that are inside or touching the given_box
        box_array = self.np_array_all_xmin_ymin_xmax_ymax[
            np.array([self.is_intersect(center_bbox, b) for b in self.np_array_all_xmin_ymin_xmax_ymax])]

        cells_list = []

        for box in box_array:
            key = tuple(box.tolist())
            if key in self.cells_xmin_ymin_xmax_ymax_dict:
                if include_current or (not self.is_tuples_match(tp1=key, tp2=cell.custom_id)):
                    cells_list.append(self.cells_xmin_ymin_xmax_ymax_dict[key])

        return cells_list

    def is_touch_inside_current_layout(self, touch) -> bool:
        return touch.y <= self.height

    def get_rect_from_list(self, obj, rect_list, as_rectangle=False):
        """
        If the given a Rectangle object or a tuple with (x, y) coordinates is found in the list rect_list, then
         it that (found) rectangle is returned; else None is returned
        :param obj: A Kivy Rectangle object or a tuple coordinates (x, y)
        :param rect_list: List|Set of CellWidget
        :param as_rectangle:
        :return:
        """
        rect_xy = obj
        _rect = None
        # x, y = None, None
        # w, h = self.rect_width_size, self.rect_height_size
        if isinstance(obj, CellWidget) or as_rectangle:
            # If Rectangle given, then
            if isinstance(obj, CellWidget):
                x, y = obj.rect.pos
            else:
                x, y = obj.pos
        else:
            x, y = rect_xy

        _rect = [r for r in rect_list if self.is_box_a_in_box_b(box_a_pos=(x, y), boxb=r)]

        if _rect is None:
            return None

        if len(_rect) == 1:
            return _rect[0]

        return None

    def activate_cell(self, cell: CellWidget):
        """
         Turn rectangle black rectangle shape
        :param cell: 
        :return:
        """
        self.current_selected_state_index = None  # Set to None to prevent accidental deletion
        if not cell.is_active:
            cell.update()
            self.active_cells_list.add(cell)
            x, y, w, h = cell.rect.pos[0], cell.rect.pos[1], cell.rect.size[1], cell.rect.size[1]
            xmin, ymin, xmax, ymax = x, y, x + w, y + h
            self.quadtree_active_cells.insert(item=cell, bbox=(xmin, ymin, xmax, ymax))

    def deactivate_cell(self, cell: CellWidget):
        """
         Turn rectangle white rectangle shape
         :param cell:
        :return:
        """
        self.current_selected_state_index = None  # Set to None to prevent accidental deletion
        if cell.is_active:
            cell.update()

            if cell in self.active_cells_list:
                self.active_cells_list.remove(cell)
            x, y, w, h = cell.rect.pos[0], cell.rect.pos[1], cell.rect.size[1], cell.rect.size[1]
            xmin, ymin, xmax, ymax = x, y, x + w, y + h
            self.quadtree_active_cells.remove(item=cell, bbox=(xmin, ymin, xmax, ymax))

    def deactivate_all_cells(self):
        [self.deactivate_cell(cell=c) for c in self.active_cells_list.copy()]
        # self.active_cells_list = set()

    def update_rectangle_status_on_touch(self, cell: CellWidget) -> None:
        if cell.is_active:  # It was active, so we deactivate it
            self.deactivate_cell(cell=cell)
        else:  # It was not active, so we activate it
            self.activate_cell(cell=cell)

    def on_touch_down(self, touch):
        if self.is_touch_inside_current_layout(touch):
            c = self.get_cell_by_coords_from_all_cells(*touch.pos)
            if c is not None:
                self.update_rectangle_status_on_touch(cell=c)

    def get_number_of_close_active_cells(self, cell: CellWidget):
        x, y = cell.rect.pos
        w, h = self.rect_width_size, self.rect_height_size
        center_x, center_y = x + w / 2, y + h / 2
        center_bbox = (center_x - w, center_y - h, center_x + w, center_y + h)

        close_cells = self.quadtree_active_cells.intersect(bbox=center_bbox)
        if cell.is_active:
            return len(close_cells) - 1
        return len(close_cells)

    def set_should_cell_change_state_next(self, cell: CellWidget) -> bool:
        number_of_close_active_cells = self.get_number_of_close_active_cells(cell=cell)

        next_activate = False
        if (cell.is_active and number_of_close_active_cells in [2, 3]) or \
                (not cell.is_active and number_of_close_active_cells == 3):
            # print(f"Result: Yes")
            next_activate = True

        return cell.is_active != next_activate

    def evaluate_grid_next_state(self) -> None:
        """
        Evaluate the status (active?) of each rectangle for the next generation
        :return:
        """
        # Set the list of all cells surrounding each active cell and remove duplicate
        self.set_of_surrounding_cells = set()
        for c in self.active_cells_list:
            self.set_of_surrounding_cells.update(self.get_surrounding_cells_list(cell=c))

        # Set accessing list and remove duplicates cells
        self.accessing_list = self.set_of_surrounding_cells | self.active_cells_list

        # For each cell in accessing list,
        # set change_state_next = True if they should change their state: activate/deactivate
        for i, c in enumerate(self.accessing_list):
            c.change_state_next = self.set_should_cell_change_state_next(cell=c)

    def is_box_a_in_box_b(self, box_a_pos, boxb, tl=.001) -> bool:
        return boxb.rect.pos[0] - tl <= box_a_pos[0] <= boxb.rect.pos[0] + self.rect_width_size + tl and \
               boxb.rect.pos[1] - tl <= box_a_pos[1] <= boxb.rect.pos[1] + self.rect_height_size + tl

    def get_cell_by_coords_from_all_cells(self, x, y):
        # print(f"len(self.children): {len(self.children)}")
        cell = [c for c in self.children if self.is_box_a_in_box_b(box_a_pos=(x, y), boxb=c)]
        if cell:
            return cell[0]
        else:
            return None

    def get_cell_by_id(self, _id):
        if _id in self.cells_xmin_ymin_xmax_ymax_dict:
            return self.cells_xmin_ymin_xmax_ymax_dict[_id]
        else:
            return None

    def custom_collide_point(self, x, y) -> bool:
        return self.get_cell_by_coords_from_all_cells(x=x, y=y) is not None

    # def func1(self):
    #     self.active_cells_list = set()
    #     for c in self.accessing_list:
    #         if c.change_state_next:
    #             if not c.is_active:  # if cell were not active then it will be activated, so add its position...
    #                 self.activate_cell(cell=c)
    #             else:
    #                 self.deactivate_cell(cell=c)
    #             c.change_state_next = False
    #         else:  # For cells that are not changing their state. Check if they are active
    #             if c.is_active:  # If there are active then add their position as they'll also be active next
    #                 self.active_cells_list.add(c)

    def update_grid(self, *args):
        """
        Updating the grid by setting cell's current state  their next generation state.
        This is done for only cells where 'change_state_next' is True
        :param args:
        :return:
        """

        if not self.is_stability_reached:
            # Evaluate next state of accessing_list
            self.evaluate_grid_next_state()

            # Update cells where 'change_state_next' is True
            change_occurred = False
            for c in self.accessing_list:
                if c.change_state_next:
                    change_occurred = True
                    if not c.is_active:  # if cell were not active then it will be activated, so add its position...
                        self.activate_cell(cell=c)
                    else:
                        self.deactivate_cell(cell=c)
                    c.change_state_next = False

            if not change_occurred:
                msg = f"Grid stability reached at generation {self.generation_number}"
                show_toast(message=msg, bg_col=None, duration=5)
                print(msg)
                self.is_stability_reached = True
            else:
                self.generation_number += 1
                self.generation = f"{self.generation_default}: {self.generation_number}"

    def reset_grid(self):
        self.deactivate_all_cells()
        self.draw_horizontal_and_vertical_lines()  # Redraw horizontal and vertical lines

        # Reset generation counter
        self.generation_number = 0
        self.generation = self.generation_default + " 0"
