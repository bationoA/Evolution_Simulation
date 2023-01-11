# Game Of Life | Evolution Simulation
This is a cellular automaton simulation of the Game of Life invented by mathematician John Horton Conway in 1970. It simulates a grid of cells, where each cell can be in one of two states, alive or dead. The simulation is run in discrete time steps, and at each step, the state of each cell is updated based on the state of its eight neighboring cells. 

## Features

- Dynamic and responsive user interface created with Kivy.
- Zoom in and out of the simulation.
- Changing the settings of the simulation.
- Efficient handling of the huge amount of cells using PyQtrees library.
- Spatial queries like finding all live cells, dead cells or cells that will be dead next turn.

## Getting Started

To run the app, you will need to have Python 3 installed on your system. You can download the latest version of Python from the official website (https://www.python.org/downloads/).

You also need to install kivy, numpy and pyqtree using pip:

pip install kivy numpy pyqtree


Then you can run the app with the following command:

python main.py


## Customize

You can customize the app by changing the following parameters in main.py file

- the number of rows and columns of the grid.
- the shape of the grid ( toroidal or not)
- the rate of randomness when randomly initializing the grid
- and more.

## Contribution

If you want to contribute to this project, please feel free to submit pull requests or contact me directly.

## Licence

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/)

This is just a sample, so you can edit it as you need, adding more details about how to install dependencies, how to run the app, examples of usage, screenshots, etc.
You can also add some further customizations if you have any.
Please let me know if there is anything else I can help you with.

###### <p><i>Icons source: <a target="_blank" href="https://icons8.com">Icons8</a></i></p>