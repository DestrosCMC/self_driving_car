import numpy as np
import picar_4wd as fc
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
import math as math
import matplotlib.pyplot as plt
import detect

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
dest_y = 120
dir = 'North'
print(dir)

def set_coordinates(angle, distance, grid_x_offset):
  x = int(math.ceil(distance * math.sin(math.radians(abs(angle)))) + grid_x_offset)
  x = 99 if x > 99 else x
  #x = int(math.ceil(distance * math.sin(angle)))
  y = int(math.ceil(distance * math.cos(math.radians(abs(angle)))))
  y = 99 if y > 99 else y
  #print('angle ', angle, ', distance ', distance, ', x ',x,', y ',y)
  map_grid[x,y] = 1
  return x, y

def set_slope_coordinates(x1, x2, y1, y2):
  if x2-x1 != 0:
    m = (y2-y1)/(x2-x1)
    for x in range(x1+1, x2):
      prev_diff = 0
      for y in range(y1+1, y2):
        if x2-x != 0:
          m1 = (y2 - y)/(x2 - x)
          curr_diff = abs(m1-m)
          if curr_diff < prev_diff or prev_diff == 0:
            prev_diff = curr_diff
            #print('coordinates to set', x, y)
            map_grid[x][y] = 1
def scan_row():
  global prev_x, prev_y, x, y
  map_grid = np.zeros((100,100))
  for curr_angle in range(left_limit_angle, right_limit_angle, 5):
    distance = fc.get_distance_at(curr_angle)
    reading = fc.get_status_at(curr_angle)
    print('angle ', curr_angle, reading, distance)
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


def turnleft():
  fc.turn_left(30)
  fc.time.sleep(1.7)
  fc.stop()
def moveforward():
  fc.forward(20)
  fc.time.sleep(0.5)
  fc.stop()
  detect()
def turnright():
  fc.turn_right(30)
  fc.time.sleep(1.5)
  fc.stop()

def calculate_next_move():
    global dir,source_y,source_x,dest_x,dest_y,map_grid
    if source_y>=dest_y:
      if dest_x<source_x:
        turnleft()
        while dest_x<source_x:
          moveforward()
          source_x-=13
      else:
        turnright()
        while dest_x>source_x:
          moveforward()
          source_x+=13
    elif dir =='North':
        print("North")
        if np.all(map_grid[45:55, 0:13]==0):
            moveforward()
            source_y += 13
        elif source_x<dest_x:
            #np.all(map_grid[20:45,0:13]==0):
            turnright()
            dir = 'East'
        elif source_x>dest_x: #np.all(map_grid[55:80,0:13]==0):
            turnleft()
            dir = 'West'
        else:
            print()
    elif dir == 'West':
        print("West")
        if np.all(map_grid[45:55,0:13]==0):
            moveforward()
            source_x -= 13
            map_grid = np.zeros((100,100))
            scan_row()
            if np.all(map_grid[45:55,0:13]==0):
              moveforward()
              source_x+=13
        turnright()
        dir = 'North'
        map_grid = np.zeros((100,100))
        scan_row()
        if np.all(map_grid[45:55,0:13]==0):
          moveforward()
          source_y += 13
        else:
          turnright()
          dir = 'East'
        '''elif np.all(map_grid[55:80,0:13]==0):
            turnleft'''
    elif dir == 'East':
        print("East")
        if np.all(map_grid[45:55,0:13]==0):
            moveforward()
            source_x += 13
            map_grid = np.zeros((100,100))
            scan_row()
            if np.all(map_grid[45:55,0:13]==0):
              moveforward()
              source_x+=13
        turnleft()
        dir = 'North'
        map_grid = np.zeros((100,100))
        scan_row()
        if np.all(map_grid[45:55,0:13]==0):
          moveforward()
          source_y+=13
        else:
          turnleft()
          dir = 'West'
        '''elif np.all(map_grid[55:80,0:13]==0):
            fc.turn_right(30)
            fc.time.sleep(1.75)
            fc.stop()
            dir = 'South'''
        #else:
         #   print()
    else:
        print("South")
        if np.all(map_grid[20:45,0:13]==0):
            fc.turn_right(30)
            fc.time.sleep(1.75)
            fc.stop()
            dir = 'West'
        elif np.all(map_grid[55:80,0:13]==0):
            fc.turn_left(30)
            fc.time.sleep(2.2)
            fc.stop()
            dir = 'East'
        elif np.all(map_grid[45:55,0:13]==0):
            fc.forward(20)
            fc.time.sleep(0.5)
            fc.stop()
            source_y -= 13
        else:
            print()
def main():
  print("in main")
  servo = Servo(PWM("P0"), 0)
  print(fc.get_distance_at(init_angle))
  curr_x, curr_y = source_x, source_y
  while (source_x <= dest_x) or (source_y <= dest_y):
    global map_grid
    map_grid = np.zeros((100,100))
    scan_row()
    for j in range(100):
      print(list(map_grid[j]))
    plt.imshow(map_grid,origin='lower')
    plt.show()
    calculate_next_move()
    print("X and Y are: ("+str(source_x) + "," + str(str(source_y))+")")

    #Run A* to find route
    #Follow for x steps

if __name__ == "__main__":
  try:
    main()
  finally:
    fc.stop()
