### imports ###
import math
import pygame
import random
###  ###




### classes ###

## animation class help in animate images ##
class Animation:
    def __init__(self, animations, current_animation_name, animation_time=120):
        # prepare images of animation
        self.animations = animations
        self.current_animation_name = current_animation_name
        self.images = animations[current_animation_name].copy()
        self.image = self.images[0]

        # prepare time of animation
        self.animation_time = animation_time
        self.animation_time_prev = pygame.time.get_ticks()
        self.animation_trigger = False

        # some variables
        self.animations_num = 0

    def animate(self, check=True):
        if check:
            self.animation_trigger = self.check_animation_time
        if self.animation_trigger:
            self.animations_num += 1
            self.image = self.images[0]
            self.images.rotate(-1)

    def change_animation(self, animation_name, cut=False, animation_time=120):
        if animation_name in self.animations.keys():
            self.images = self.animations[animation_name].copy()
            self.current_animation_name = animation_name
            if cut:
                self.animation_time = animation_time
                self.animation_time_prev = pygame.time.get_ticks() - self.animation_time
            else:
                self.animation_time_prev += self.animation_time - animation_time
                self.animation_time = animation_time

    @property
    def check_animation_time(self):
        time_now = pygame.time.get_ticks()
        if time_now > self.animation_time_prev + self.animation_time:
            self.animation_time_prev = time_now
            return True
        else:
            return False

    @property
    def check_animation_end(self):
        return self.images == self.animations[self.current_animation_name] and self.animation_trigger
##  ##


## ray class for raycasting ##
class Ray:
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle

    def change_angle(self, angle):
        if type(angle) in (int, float):
            self.angle = angle
        else:
            self.angle = math.atan2(angle[1] - self.pos[1], angle[0] - self.pos[0])
        self.angle %= math.tau

    def intersection_line(self, line):
        x1, y1 = line[0][0], line[0][1]
        x2, y2 = line[1][0], line[1][1]
        x3, y3 = self.pos[0], self.pos[1]
        x4, y4 = self.pos[0] + math.cos(self.angle), self.pos[1] + math.sin(self.angle)

        divisor = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if divisor == 0:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / divisor
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / divisor

        if 0 <= t < 1 and u > 0:
            intersection_point = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
            depth = math.sqrt((intersection_point[0] - self.pos[0]) ** 2 + (intersection_point[1] - self.pos[1]) ** 2)
            return {"point": intersection_point, "depth": depth}
        else:
            return None

    def intersection_lines(self, lines):
        intersections = []
        for line in lines:
            intersection = self.intersection_line(line)
            if intersection:
                intersections.append(intersection)
        return intersections

    def intersection_near_line(self, lines):
        depth = -1
        ordered_intersection = None
        for intersection in self.intersection_lines(lines):
            if intersection["depth"] < depth or depth == -1:
                depth = intersection["depth"]
                ordered_intersection = intersection
        return ordered_intersection

    def intersection_rect(self, rect):
        x, y, w, h = rect
        lines = [((x, y), (x + w - 1, y)),
                 ((x, y), (x, y + h - 1)),
                 ((x + w - 1, y), (x + w - 1, y + h - 1)),
                 ((x, y + h - 1), (x + w - 1, y + h - 1))]
        return self.intersection_near_line(lines)
##  ##


# camera 2D
class Camera:
    def __init__(self, pos, size, screen_pos=None, screen_size=None):
        self.x, self.y = pos
        self.w, self.h = size

        if screen_pos:
            self.sx, self.sy = screen_pos
        else:
            self.sx, self.sy = 0, 0

        if screen_size:
            self.sw, self.sh = screen_size
        else:
            self.sw, self.sh = size

        self.zoom = 1
        self.min_zoom = .5
        self.max_zoom = 2

    @property
    def width(self):
        return self.w / self.zoom

    @property
    def height(self):
        return self.h / self.zoom

    @property
    def scale_x(self):
        return self.sw / self.width

    @property
    def scale_y(self):
        return self.sh / self.height

    def pos_real_to_screen(self, real_pos):
        x, y = real_pos
        x -= self.x
        y -= self.y
        x *= self.scale_x
        y *= self.scale_y
        x += self.sx
        y += self.sy
        return x, y

    def pos_screen_to_real(self, pos):
        x, y = pos
        x -= self.sx
        y -= self.sy
        x /= self.scale_x
        y /= self.scale_y
        x += self.x
        y += self.y
        return x, y

    def size_real_to_screen(self, real_size):
        w, h = real_size
        w *= self.scale_x
        h *= self.scale_y
        return w, h

    def size_screen_to_real(self, size):
        w, h = size
        w /= self.scale_x
        h /= self.scale_y
        return w, h

    def change_zoom(self, zoom, center=False):
        center_pos = self.center
        self.zoom += zoom
        print(self.zoom)
        self.zoom = round(self.zoom, 2)
        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom
        elif self.zoom < self.min_zoom:
            self.zoom = self.min_zoom
        if type(self.zoom) == float and self.zoom.is_integer():
            self.zoom = int(self.zoom)
        if center:
            self.set_center(center_pos)

    @property
    def center(self):
        return self.x + self.width / 2, self.y + self.height / 2

    def set_center(self, pos):
        self.x, self.y = pos
        self.x -= self.width / 2
        self.y -= self.height / 2

    def resize(self, size):
        self.w, self.h = size

    def resize_screen(self, size):
        self.sw, self.sh = size

    @property
    def pos(self):
        return self.x, self.y
##  ##


## game structure in pygame ##
class Game:
    def __init__(self):
        ### set screen of game ###
        self.screen = pg.surface.Surface((800, 500))
        self.window = pg.display.set_mode((800, 500))

        self.screen_ratio = self.screen.get_width() / self.screen.get_height()
        self.ww, self.wh = pg.display.get_window_size()
        self.window_ratio = self.ww / self.wh
        self.new_h = self.wh
        self.new_w = self.ww
        self.zoom_ratio = 1
        self.prepare_screen()

        ### set fps ###
        self.clock = pg.time.Clock()

        ### set variables of events ###
        self.key_down = []
        self.key_still = []
        self.key_up = []
        self.mouse_down = []
        self.mouse_still = []
        self.mouse_up = []

        ### game properties ###

    def events(self):
        self.key_down = []
        self.key_up = []
        self.mouse_down = []
        self.mouse_up = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                self.key_down.append(event.key)
                if event.key not in self.key_still:
                    self.key_still.append(event.key)
            elif event.type == pg.KEYUP:
                self.key_up.append(event.key)
                if event.key in self.key_still:
                    self.key_still.remove(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_down.append(event.button)
                if event.button not in self.mouse_still:
                    self.mouse_still.append(event.button)
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_up.append(event.button)
                if event.button in self.mouse_still:
                    self.mouse_still.remove(event.button)
        if pg.K_ESCAPE in self.key_down:
            pg.quit()
            quit()

    def update(self):
        ### display fbs on title ###
        self.clock.tick(30)
        pg.display.set_caption(str(int(self.clock.get_fps())))

        ### prepare screen ###
        self.prepare_screen()

        ### logic here ###

    def draw(self):
        self.screen.fill("black")

        ### drawing here ###

        ### draw screen on window ###
        new_screen = pg.transform.scale(self.screen.copy(), (self.new_w, self.new_h))
        self.window.blit(new_screen, ((self.ww - self.new_w) // 2, (self.wh - self.new_h) // 2))
        pg.display.flip()

        self.window.blit(self.screen, (0, 0))
        pg.display.update()

    def run(self):
        while True:
            self.events()
            self.update()
            self.draw()

    def prepare_screen(self):
        self.screen_ratio = self.screen.get_width() / self.screen.get_height()
        self.ww, self.wh = pg.display.get_window_size()
        self.window_ratio = self.ww / self.wh
        if self.window_ratio > self.screen_ratio:
            self.new_h = self.wh
            self.new_w = self.wh * self.screen_ratio
        elif self.window_ratio < self.screen_ratio:
            self.new_w = self.ww
            self.new_h = self.ww / self.screen_ratio
        else:
            self.new_w = self.ww
            self.new_h = self.wh
        self.zoom_ratio = self.new_w / self.screen.get_width()

    @property
    def get_mouse_pos(self):
        mx, my = pg.mouse.get_pos()
        return (mx - (self.ww - self.new_w) / 2) / self.zoom_ratio, (my - (self.wh - self.new_h) / 2) / self.zoom_ratio

    def set_mouse_pos(self, pos):
        x, y = pos
        x = x * self.zoom_ratio + (self.ww - self.new_w) / 2
        y = y * self.zoom_ratio + (self.wh - self.new_h) / 2
        pg.mouse.set_pos(x, y)

    @property
    def get_mouse_rel(self):
        x, y = pg.mouse.get_rel()
        return x / self.zoom_ratio, y / self.zoom_ratio
##  ##

###  ###




### functions ###

## get random list ##
def randlist(ulist):
    rand_list = []
    while True:
        randingr = ulist[random.randint(0, len(ulist) - 1)]
        rand_list.append(randingr)
        for i in range(len(rand_list) - 1):
            if rand_list[i] == randingr:
                rand_list.pop()
        if len(rand_list) == len(ulist):
            break
    return rand_list
##  ##


## تنسخ ملف عدد مرات محددة ##
def copying(file1, imtdad='', loop=1):
    a = open(str(file1), 'r')
    b = a.read()
    a.close()
    print(b)
    i = 0
    while i < int(loop):
        i += 1
        c = open(str(i) + '.' + str(imtdad), 'w')
        c.write(b)
        c.close()
##  ##


## تأخذ قائمة جمل من ملف ##
def taseli(file, start=1, end=None):
    address = open(file, 'r')
    listofsent = address.readlines()[start - 1:end]
    address.close()
    return listofsent
##  ##


## تزيل أو تضع (n\) التي تنشئ سطر جديد ##
def remoredn(list, remove=True):
    if remove == True:
        for i in range(len(list)):
            list[i] = list[i][:len(list[i]) - 1]
    elif remove == False:
        for i in range(len(list)):
            list[i] = list[i] + '\n'
    return list
##  ##


## تأخذ قائمة وتفصلها إلي قوائم أصغر حسب العدد المكتوب قبل عناصر كل قائمة صغيرة// ##
def listseption(numedlist):
    sepedlist = []
    while len(numedlist) != 0:
        num = int(numedlist[0])
        # if num>len(numedlist):
        # num=len(numedlist)
        sepedlist.append(numedlist[1:num])
        for i in range(num):
            numedlist.remove(numedlist[0])
    return sepedlist
##  ##


## تنشئ قائمة بها كل الاحتمالات لترتيب عدد من عناصر في عدد من خانات ##
def possibilities(num_of_cells, ingredients, task=None):
    # possibilities=[]
    nums = []
    for i in range(num_of_cells):
        nums.append(0)

    while True:
        num = -1
        while nums[num] >= len(ingredients):
            nums[num] = 0
            num -= 1
            nums[num] += 1
            if nums[0] >= len(ingredients):
                return  # possibilities
        possibility = []
        for i in nums:
            possibility.append(ingredients[i])
        if task:
            task(possibility)
        # possibilities.append(possibility)
        nums[-1] += 1
##  ##


## get the biggest number from several numbers ##
def largest_num(*nums):
    if type(nums[0]) == list:
        nums = nums[0]
    nums = list(nums)
    nums2 = nums.copy()
    nums3 = nums2.copy()
    for i in nums2:
        for y in nums:
            if i < y:
                nums3.remove(i)
                break
    return nums3
##  ##


## get number of data and separate it to the smallest data ####
def separation(*fulllist):
    l = []
    ingredients = []
    l.append(list(fulllist))
    while True:
        i = l[-1][0]
        if type(i) in (list, tuple, set):
            l.append(list(i))
        else:
            ingredients.append(i)
            l[-1].remove(i)
            if len(l) > 1 and len(l[-1]) == 0:
                l.pop()
                l[-1].remove(l[-1][0])
        if len(l) == 1 and len(l[-1]) == 0:
            return ingredients
##  ##

###  ###
