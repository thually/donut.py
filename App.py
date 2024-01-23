import numpy as np
from Donut import Donut
from Stage import Stage
import os
import time

dona = Donut()
dona.rotate_x(np.pi / 6)
dona.plot() # Creates 3D plot of the donut

stage = Stage(dona)

A = 0.1
B = 0.1
# stage.animation(A, B) # Creates gif of the projected donut

clear_op = 'cls' if os.name == 'nt' else 'clear'

os.system(clear_op)
while True:
    stage.render_frame(A, B)
    os.system(clear_op)
    stage.pprint()
    time.sleep(0.05)
