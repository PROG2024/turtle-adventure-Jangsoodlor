"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random
import tkinter as tk
import os

# from PIL import Image, ImageTk


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )

# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class RandomWalkEnemy(Enemy):
    """
    Enemy that will walk randomly on the screen
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.x = self.random_x()
        self.y = self.random_y()
        self.__x_dest = self.random_x()
        self.__y_dest = self.random_y()
        self.__spd = random.randint(1,2)

    def create(self) -> None:
        self.__id = self.game.canvas.create_oval(0,
                                                 0,
                                                 self.size,
                                                 self.size,fill=self.color)

    def random_x(self):
        return random.randint(0, self.canvas.winfo_width())

    def random_y(self):
        return random.randint(0, self.canvas.winfo_height())

    def move_x(self):
        if self.x in range(self.__x_dest-100, self.__x_dest+100):
            self.__x_dest = self.random_x()
            self.__spd = random.randint(3,10)
        if self.__x_dest > self.x:
            self.x += self.__spd
        else:
            self.x -= self.__spd

    def move_y(self):
        if self.y in range(self.__y_dest-self.size, self.__y_dest+self.size):
            self.__y_dest = self.random_y()
            self.__spd = random.randint(3,10)
        if self.__y_dest > self.y:
            self.y += self.__spd
        else:
            self.y -= self.__spd

    def update(self) -> None:
        self.move_x()
        self.move_y()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.game.canvas.coords(self.__id, self.x - self.size/2,
                                self.y - self.size/2,
                                self.x + self.size,
                                self.y + self.size)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class ChasingEnemy(Enemy):
    """
    Enemy that will try chasing the player.
    """
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__img = None
        self.__img_obj = None
        self.__spd = 2
        self.x = random.randint(200,self.canvas.winfo_width()-100)
        self.y = random.randint(200,self.canvas.winfo_height()-100)
        self.__x_spd = 0
        self.__y_spd = 0
        self.__hide = False
        # self.canvas.after(1000, self.delete)
        # self.canvas.after(10000, self.create)

    def create(self):
        self.__hide = False
        self.__img = tk.PhotoImage(file=os.path.join(os.getcwd(), 'skibidi_toilet.gif'))
        # self.__img = ImageTk.PhotoImage(Image.open('skibidi_toilet2.png'))
        self.__img_obj = self.canvas.create_image(self.x,self.y, image=self.__img, anchor=tk.CENTER)

    def update(self):
        if not self.__hide:
            player_x, player_y = self.game.player.x, self.game.player.y
            delta_x, delta_y = player_x - self.x, player_y - self.y
            delta_c = (delta_x**2 + delta_y**2)**0.5
            self.__x_spd = self.__spd * (delta_x/delta_c)
            self.__y_spd = self.__spd * (delta_y/delta_c)
            self.x += self.__x_spd
            self.y += self.__y_spd
            if self.hits_player():
                self.game.game_over_lose()

    def render(self):
        self.canvas.move(self.__img_obj,self.__x_spd, self.__y_spd)

    def delete(self):
        self.canvas.delete(self.__img_obj)
        self.canvas.delete(self.__img)
        self.__hide = True

class FencingEnemy(Enemy):
    """Enemy that will walk around the home in a square-like pattern"""
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.west = self.game.home.x - self.size - self.game.home.size - 10
        self.east = self.game.home.x + self.game.home.size + self.size + 10
        self.north = self.game.home.y - self.game.home.size - self.size - 10
        self.south = self.game.home.y + self.game.home.size + self.size + 10
        self.x = random.randint(self.west, self.east)
        self.y = self.north
        self.__move = self.move_left
        self.__spd = self.game.level

    def create(self):
        self.__id = self.canvas.create_rectangle(0,0,self.size,self.size, fill=self.color)

    def move_left(self):
        self.x -= self.__spd
        if self.x in range(self.west-self.__spd+1, self.west+self.__spd-1):
            self.__move = self.move_down

    def move_down(self):
        self.y += self.__spd
        if self.y in range(self.south-self.__spd+1, self.south+self.__spd-1):
            self.__move = self.move_right

    def move_right(self):
        self.x += self.__spd
        if self.x in range(self.east-self.__spd+1, self.east+self.__spd-1):
            self.__move = self.move_up

    def move_up(self):
        self.y -= self.__spd
        if self.y in range(self.north-self.__spd+1, self.north + self.__spd-1):
            self.__move = self.move_left
    
    def update(self):
        self.__move()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self):
        self.game.canvas.coords(self.__id, self.x - self.size/2,
                                self.y - self.size/2,
                                self.x + self.size,
                                self.y + self.size)

    def delete(self):
        self.canvas.delete(self.__id)

class TruckKun(Enemy):
    """Unique Enemy that will attempts to send our little turtle to another world"""
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.__img = None
        self.__img_obj = None
        self.__is_animating = False
        self.__spd = 10
        self.x = self.game.winfo_width()+100
        self.y = self.game.player.y

    def create(self):
        if self.__is_animating:
            self.__img = tk.PhotoImage(file=os.path.join(os.getcwd(), 'truck_kun.gif'))
            self.__img_obj = self.canvas.create_image(self.x,self.y, image=self.__img, anchor=tk.CENTER)

    def trigger(self):
        if random.randint(1,max(100-self.game.level**3, 10)) == 1:
            print('lol')
            self.__is_animating = True
            self.x = self.game.winfo_width()+100
            self.y = self.game.player.y
            self.create()

    def move(self):
        if self.x <= 0:
            self.__is_animating = False
            self.delete()
        elif self.__spd > 0:
            self.__spd *= -1
        else:
            self.x += self.__spd

    def update(self):
        if not self.__is_animating:
            self.trigger()
        elif self.hits_player():
            self.game.game_over_lose()
        else:
            self.move()

    def render(self):
        if self.__is_animating:
            self.canvas.move(self.__img_obj, self.__spd, 0)

    def delete(self):
        self.canvas.delete(self.__img_obj)
        self.canvas.delete(self.__img)
        self.__is_animating = False


# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        for _ in range(self.game.level):
            new_enemy = RandomWalkEnemy(self.__game, 20, "red")
            self.game.add_element(new_enemy)
        for _ in range(1+self.game.level//10):
            skibidi = ChasingEnemy(self.__game, 65, "red")
            self.game.add_element(skibidi)
        for _ in range(4):
            fencer = FencingEnemy(self.__game, 10, "green")
            self.game.add_element(fencer)
        truck = TruckKun(self.__game, 100, "red")
        self.game.add_element(truck)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
