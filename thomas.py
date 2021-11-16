import mouse
import time
import random
import itertools

HBounds = (-4096, -2049)
VBounds = (0, 1151)
i=itertools.cycle([1,-1])


while True:
    print(mouse.get_position())
    # x=random.randint(*HBounds)
    # y=random.randint(*VBounds)
    sign = next(i)
    x = 100*sign
    y= x
    d=random.random()*5
    mouse.move(x=x,y=y, absolute=False, duration=d)
    time.sleep(random.random()*10)
    

print('DONE')


