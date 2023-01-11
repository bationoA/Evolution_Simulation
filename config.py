import os.path

window_width = 1480
window_height = 800


window_background_color = (.1, .1, .1, 1)

HorizontalMenuLayout_height_proportion = .07
HorizontalMenuLayout_width_proportion = 1
GridZoneLayout_height_proportion = 1 - HorizontalMenuLayout_height_proportion
GridZoneLayout_width_proportion = 1
run_interval_seconds = .1
grid_rows = 50  # if 'auto' then
grid_cols = 'auto'  # 'auto' = 2 * grid_rows
activated_color = [0, 0, 0, 1]  # black
deactivated_color = [1, 1, 1, 1]  # white
# ----------------
outputs_dir = 'outputs'
outputs_images_dir = os.path.join(outputs_dir, 'images')
resources_dir = 'resources'
resources_images_dir = os.path.join(resources_dir, 'images')

# ------------ <a target="_blank" href="https://icons8.com">Icons8</a>
start_button_logo_name = os.path.join(resources_images_dir, 'icons8-go-green-50.png')
pause_button_logo_name = os.path.join(resources_images_dir, 'icons8-pause-button-50.png')
restart_button_logo_name = os.path.join(resources_images_dir, 'icons8-rotate-48.png')
reset_button_logo_name = os.path.join(resources_images_dir, 'icons8-return-48.png')
save_button_logo_name = os.path.join(resources_images_dir, 'icons8-save-48.png')
delete_button_logo_name = os.path.join(resources_images_dir, 'icons8-delete-48.png')
bookmarks_button_logo_name = os.path.join(resources_images_dir, 'icons8-bookmark-48.png')
loading_image_name = os.path.join(resources_images_dir, 'Blinking-squares.gif')
screenshot_button_image_name = os.path.join(resources_images_dir, 'icons8-screenshot-50.png')
# -----------------------


