import numpy as np
import picar_4wd as fc
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
import math as math

#Create a 100x100 array filled with zeros
map_grid = np.zeros((100,100))
#Initialize variables
x_offset = len(map_grid[0])/2
init_angle = 0
prev_x = 0
prev_y = 0
left_limit_angle = -90
right_limit_angle = 90
source_x = x_offset
source_y = 0
dest_x = 90
dest_y = 90

def set_coordinates(angle, distance, grid_x_offset):
  x = int(math.ceil(distance * math.sin(angle)) + grid_x_offset)
  y = int(math.ceil(distance * math.cos(angle)))
  print('angle ', angle, ', distance ', distance, ', x ',x,', y ',y)
  map_grid[x,y] = 1
  return x, y

def set_slope_coordinates(x1, x2, y1, y2):
  #m = (y2 -y1) / (x2 - x1)
  for x in range(x1, x2):
    for y in range(y1, y2):
      map_grid[x][y] = 1

def scan_row():
  global prev_x, prev_y
  for curr_angle in range(left_limit_angle, right_limit_angle, 5):
    distance = fc.get_distance_at(curr_angle)
    reading = fc.get_status_at(curr_angle)
    if reading != 2:
      x, y = set_coordinates(curr_angle, distance, x_offset)
      if prev_x ==0 or prev_y ==0:
        prev_x = x
        prev_y = y
    else:
      if prev_x != 0 or prev_y != 0:
        set_slope_coordinates(prev_x, x, prev_y, y)
        prev_x = 0
        prev_y = 0

def main():
  print("in main")
  servo = Servo(PWM("P0"), 0)
  print(fc.get_distance_at(init_angle))
  curr_x, curr_y = source_x, source_y
  while source_x != dest_x and source_y != dest_y:
    scan_row()
    print(map_grid)

    #TODO
    calculate_next_move()
    #Run A* to find route
    #Follow for x steps

if __name__ == "__main__":
  try:
    main()
  finally:
    fc.stop()
