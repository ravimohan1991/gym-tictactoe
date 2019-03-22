import gym
import numpy as np
import math
import pyglet
import logging
from gym import spaces
from gym.utils import seeding
from gym.envs.classic_control import rendering
from pyglet.window import mouse
from array import *
from gym_tictactoe.agent.an_agent import AnAgent, check_game_status


logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

class TicTacToe(gym.Env):
    metadata = {
        'render.modes': ['human']
    }

    """
    Description:
        A simple GUI based game with the aim of conquering 3 consequtive boxes along any orientation

    Source:
        The computor moves are based on the Reinforcement Learning algorithm proposed in Barto and Sutton's
        Reinforcement Learning: An Introduction, section 1.5

    Observation:
        Type: Array
        Num     Observation     Box Number      Value 1      Value 2         Value 3
        0       Shape           0-8             -1 (Empty)   0 (Circle)      1 (Cross)

    Action:
        Type: List
        Num     Action
        0-8     Fill Shape (Cross, by the Agent)

    """

    def __init__(self):

        self.action_space = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.observation_space = spaces.Discrete(9)

        self.min_position = -1.2
        self.max_position = 0.6
        self.max_speed = 0.07
        self.goal_position = 0.5


        self.viewer = None
        self.pgwindow = None

        self.screen_width = 600
        self.screen_height = 600

        self.dataCC = array('i', [-1, -1, -1, -1, -1, -1, -1, -1, -1]) # Game board

        self.agent = AnAgent()

        self.seed()

	self.agent.setRandomizer(self.np_random)


    def reset(self):
        """Resets the state of the environment and returns an initial observation.

            Returns: observation (tuple): the initial observation of the
                     space.
        """
        for i in range(9):
            self.dataCC[i] = -1
        self.done = False
        return tuple(self.dataCC)


    def render(self, mode='human'):
        """Renders the environment.

         The conventional mode is:
            - human: render to the current display or terminal and
                     return nothing. Usually for human consumption.

         Args:
            mode (str): the mode to render with

        """

        print("Howdy!")

        world_width = self.max_position - self.min_position
        scale = self.screen_width / world_width

        if self.viewer is None:
            self.viewer = rendering.Viewer(self.screen_width, self.screen_height)

            pgwindow = self.viewer.window

            @pgwindow.event
            def on_mouse_press(x, y, button, modifiers):
                bN = self.figureOutBoxNumber(x,y)
                #print("Mouse Press at x = {0} and y = {1} and inside box number = {2}".format(x, y, bN))
                if button == mouse.LEFT:
                    self.dataCC[bN] = 1
                if button == mouse.RIGHT:
                    self.dataCC[bN] = 0

                # Human Agent Step
                # TODO: Add sanity check!
                self.dataCC[bN] = 0
                self.state = tuple(self.dataCC)

                self.moveForward()
                self.renderStuff(self.viewer)
                self.viewer.render()

            self.renderStuff(self.viewer)

        self.viewer.render()

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator.

        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.

        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """

        self.np_random, seed = seeding.np_random(seed)
        self.sSeed = seed # Funky way
        return [seed]

    def initializeState(self, state):
        """Initializes the state for the begining of the gameplay

        Args:
            state (tuple): the initial state

        """
        self.state = state


    def moveForward(self):
        """Moving on ...

        Self explanatory!
        """

        # See if human wins
        gStatus = check_game_status(self.state)
        if gStatus >= 0:
            logging.debug(
                "+----------------------------------------------------------------------------------------------")
            self.agent.ask_value(tuple(self.dataCC))# Funcky hack to update win
            logging.debug(
                "+----------------------------------------------------------------------------------------------")
            logging.debug("")
            self.handleEndgame()
            print(gStatus)
            return

        action = self.agent.act(self.state, self.action_space)
        state, reward, done, info = self.step(action)

        # See if agent wins
        gStatus = check_game_status(state)
        if gStatus >= 0:
            self.handleEndgame()
            print(gStatus)


    def step(self, action):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state.

        Accepts an action and returns a quartet (observation, reward, done, info).

        Args:
            action (object): an action provided by the environment

        Returns:
            observation (tuple): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        loc = action
        if self.done:
            return tuple(self.dataCC), 0, True, None

        # place the Cross on that location
        self.dataCC[loc] = 1

        return tuple(self.dataCC), 0, self.done, None


    def handleEndgame(self):
        """Processing events for the end-of-the-game time

        """

        self.done = True # Safety switch!
        self.initializeState(self.reset())


    def renderStuff(self, sViewer):

        # Render the partitions for 3 * 3 Tic Tac Toe
        partition_color = (0, 204, 85)

        start = (self.screen_width / 3, 0)
        end = (self.screen_width / 3, self.screen_height)
        self.line = sViewer.draw_line(start, end, linewidth=3, color=partition_color)

        start = (2 * self.screen_width / 3, 0)
        end = (2 * self.screen_width / 3, self.screen_height)
        self.line = sViewer.draw_line(start, end, linewidth=3, color=partition_color)

        start = (0, self.screen_height / 3)
        end = (self.screen_width, self.screen_height / 3)
        self.line = sViewer.draw_line(start, end, linewidth=3, color=partition_color)

        start = (0, 2 * self.screen_height / 3)
        end = (self.screen_width, 2 * self.screen_height / 3)
        self.line = sViewer.draw_line(start, end, linewidth=3, color=partition_color)

        # Render Circles and Crosses
        for i in range(9):
            if self.dataCC[i] == 1:
                self.renderCross(80, i, sViewer)
            elif self.dataCC[i] == 0:
                self.renderCircle(80, i, sViewer)



    def renderCircle(self, radius, boxNumber, sViewer):

        offsetx = self.offsetxFromBox(boxNumber)
        offsety = self.offsetyFromBox(boxNumber)
        points = []
        for i in range(30):
            ang = 2 * math.pi * i / 30
            points.append((offsetx + math.cos(ang) * radius, offsety + math.sin(ang) * radius))
        geom = rendering.FilledPolygon(points)
        geom.set_color(0, 0, 128)
        sViewer.add_onetime(geom)


    def renderCross(self, length, boxNumber, sViewer):

        offsetx = self.offsetxFromBox(boxNumber)
        offsety = self.offsetyFromBox(boxNumber)
        points = []

        begin = (offsetx - length / 1.414, offsety - length / 1.414)
        end = (offsetx + length / 1.414, offsety + length / 1.414)

        geom = rendering.Line(begin, end)
        geom.set_color(255, 0, 0)
        geom.set_linewidth(2)
        sViewer.add_onetime(geom)

        begin = (offsetx - length / 1.414, offsety + length / 1.414)
        end = (offsetx + length / 1.414, offsety - length / 1.414)

        geom = rendering.Line(begin, end)
        geom.set_color(255, 0, 0)
        geom.set_linewidth(2)
        sViewer.add_onetime(geom)


    def offsetxFromBox(self, boxNumber):
        if (boxNumber == 0 or boxNumber == 3 or boxNumber == 6):
            return (0 + self.screen_width / 3) / 2
        if (boxNumber == 1 or boxNumber == 4 or boxNumber == 7):
            return (self.screen_width / 3 + 2 * self.screen_width / 3) / 2
        if (boxNumber == 2 or boxNumber == 5 or boxNumber == 8):
            return (2 * self.screen_width / 3 + self.screen_width) / 2


    def offsetyFromBox(self, boxNumber):
        if (boxNumber == 0 or boxNumber == 1 or boxNumber == 2):
            return (0 + self.screen_height / 3) / 2
        if (boxNumber == 3 or boxNumber == 4 or boxNumber == 5):
            return (self.screen_height / 3 + 2 * self.screen_height / 3) / 2
        if (boxNumber == 6 or boxNumber == 7 or boxNumber == 8):
            return (2 * self.screen_height / 3 + self.screen_height) / 2


    def figureOutBoxNumber(self, x, y):

        boxNumber = -1
        if (x <= self.screen_width / 3 and y <= self.screen_height / 3):
            boxNumber = 0
        elif (x > self.screen_width / 3 and x < 2 * self.screen_width / 3 and y <= self.screen_height / 3):
            boxNumber = 1
        elif (x > 2 * self.screen_width / 3 and y <= self.screen_height / 3):
            boxNumber = 2
        elif (x <= self.screen_width / 3 and y > self.screen_height / 3 and y <= 2 * self.screen_height / 3):
            boxNumber = 3
        elif (x > self.screen_width / 3 and x <= 2 * self.screen_width / 3 and y > self.screen_height / 3 and y <= 2 * self.screen_height / 3):
            boxNumber = 4
        elif (x > 2 * self.screen_width / 3 and y > self.screen_height / 3 and y <= 2 * self.screen_height / 3):
            boxNumber = 5
        elif (x <= self.screen_width / 3 and y > 2 * self.screen_height / 3 ):
            boxNumber = 6
        elif (x > self.screen_width / 3 and x <= 2 * self.screen_width / 3 and y >= 2 * self.screen_height /3):
            boxNumber = 7
        else:
            boxNumber = 8

        return(boxNumber)


