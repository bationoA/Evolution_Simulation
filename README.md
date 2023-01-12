# Game Of Life | Evolution Simulation
This is a cellular automaton simulation of the [Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) invented by mathematician John Horton Conway in 1970. It simulates a grid of cells, where each cell can be in one of two states, alive or dead. The simulation is run in discrete time steps, and at each step, the state of each cell is updated based on the state of its eight neighboring cells. 

## Illustration images
- App interface (50 x 100 grid example)
![App interface image](https://github.com/bationoA/Evolution_Simulation/blob/main/resources/images/Game-of-Life-intro-0_ed.png)
- Example of a simulation output
- ![Example of a simulation output image](https://github.com/bationoA/Evolution_Simulation/blob/main/resources/images/sharingan_ed.png)

## Features

- Dynamic and responsive user interface created with Kivy.
- Save different states of a simulation.
- Changing the settings of the simulation (Time between each generation, grid size).
- Efficient handling of the huge amount of cells using PyQtrees library and Numpy 2-dimensional array (2d-array).

## Getting Started

To run the app, you will need to have Python 3 installed on your system. You can download the latest version of Python from the official website (https://www.python.org/downloads/).

You also need to install kivy, numpy and pyqtree using pip:

pip install kivy numpy pyqtree


Then you can run the app with the following command:

python main.py


## Customize

You can customize the app by changing the following parameters in main.py file

- the number of rows and columns of the grid.
- The window size (in config.py file)
- and more.
- Note: The toroidal grid is not implemented

## Contribution

If you want to contribute to this project, please feel free to submit pull requests or contact me directly.

## Licence

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/)

This is just a sample, so you can edit it as you need, adding more details about how to install dependencies, how to run the app, examples of usage, screenshots, etc.
You can also add some further customizations if you have any.
Please let me know if there is anything else I can help you with.

###### <p><i>Icons source: <a target="_blank" href="https://icons8.com">Icons8</a></i></p>