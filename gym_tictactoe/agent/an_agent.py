#!/usr/bin/env python
import os
import sys
import random
import time
import logging
import json
from collections import defaultdict
from itertools import product
from multiprocessing import Pool
from tempfile import NamedTemporaryFile
from array import *


# Some default global values
EPSILON = 0.3
ALPHA = 0.4

st_values = {}
st_visits = defaultdict(lambda: 0) # Number of times we visited the state ? TODO: something wrong here

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def reset_state_values():
    global st_values, st_visits
    st_values = {}
    st_visits = defaultdict(lambda: 0)


def set_state_value(state, value):
    st_visits[state] += 1
    st_values[state] = value



# To find the max or min values in the array list
def best_val_indices(values, fn):
    best = fn(values)
    return [i for i, v in enumerate(values) if v == best]


class AnAgent(object):
    def __init__(self):
        self.epsilon = EPSILON
        self.alpha = ALPHA

    def act(self, state, ava_actions):
        return self.egreedy_policy(state, ava_actions)

    def setRandomizer(self, randomizer):

        self.randomizer = randomizer

    def egreedy_policy(self, state, ava_actions):
        """The Epsilon greedy policy.

        Return random action with epsilon probability or best action.

        Args:
            state: Board status
            ava_actions (list): Available actions (0-8)

        Returns:
            int: Selected action.
        """

        logging.debug("+----------------------------------------------------------------------------------------------")
        self.ask_value(state)  # Make sure that state exists in the st_values list
        logging.debug("+----------------------------------------------------------------------------------------------")
        logging.debug(" ")
        logging.debug("+----------------------------------------------------------------------------------------------")
        logging.debug("|egreedy_policy for Mark X")
        e = self.randomizer.uniform(low=0, high=1)
        if e < self.epsilon :# What is the role of episode_rate in randomizing the next move?
            logging.debug("|Exploring with randomizer's e-number {}".format(e))
            action = self.random_action(state)
            logging.debug("|The random action taken is {}".format(action))
        else:
            logging.debug("|Exploiting with randomizer's e-number {}".format(e))
            action = self.greedy_action(state, ava_actions)
            temp = st_values[state]
            set_state_value(state, st_values[state] + self.alpha * (st_values[after_action_state(state, action)] - st_values[state]))
            logging.debug("|Updated the estimated value {} <- {} + {} * ({} - {}) = {}".format(temp, temp,
                                self.alpha, st_values[after_action_state(state, action)], st_values[state], st_values[state]))
        logging.debug("|The resulting state of the policy is {}".format(after_action_state(state, action)))
        logging.debug("+----------------------------------------------------------------------------------------------")
        logging.debug(" ")
        logging.debug("+----------------------------------------------------------------------------------------------")
        self.ask_value(after_action_state(state, action))  # Make sure that state exists in the st_values list
        logging.debug("+----------------------------------------------------------------------------------------------")
        logging.debug(" ")
        return action

    def random_action(self, state):
        lState = fromTupletoArray(state)
        ava_free_actions = list()
        for i in range(len(state)):
            if lState[i] == -1:
                ava_free_actions.append(i)
        logging.debug("|    Inside random_action")
        return ava_free_actions[self.randomizer.randint(0, high=ava_free_actions.__len__())]

    def greedy_action(self, state, ava_actions):
        """Return best action by current state value.

        Evaluate each action, select best one. Tie-breaking is random.
        Agent plays with the Cross
        Args:
            state: Board status
            ava_actions (list): Available actions

        Returns:
            int: Selected action
        """

        ava_values = []
        logging.debug("|Computing the greedy action for the state {} ...".format(state))
        logging.debug("|Obtaining the next states by the linear operation of the list of available actions")
        i = 1
        for action in ava_actions:
            nstate = after_action_state(state, action)
            if not nstate:
                ava_values.append(-10)# Helpful to weed out negative values (unavailable actions) during random selection. Pretty neat if i may say so :)
                continue
            logging.debug("|    {}. Next state is {}, now computing its value ...".format(i, nstate))
            nval = self.ask_value(nstate)
            ava_values.append(nval) # Storing the values of next state with action parameter
            vcnt = st_visits[nstate]
            logging.debug("|        value is {}".format(nval))
            logging.debug("|        Visiting the state {} time(s)".format(vcnt))
            i = i + 1

        indices = best_val_indices(ava_values, max)

        # tie breaking by random choice
        aidx = indices[self.randomizer.randint(0, high=indices.__len__())]
        logging.debug("|greedy_action ava_values {} indices {} aidx {}".
                      format(ava_values, indices, aidx))

        action = ava_actions[aidx]

        return action

    def ask_value(self, state):
        """Returns value of given state. If state doesnot exist in the list, then create one.

        If state value does not exist, set it as default value.

        Args:
            state: State.

        Returns:
            float: Value of a state.

        TODO: Log the list st_values
        """
        if state not in st_values:
            logging.debug("|            New State detected. Appending the list of states for appropriate adjustments.")
            logging.debug("|            ask_value - new state {}".format(state))
            gstatus = check_game_status(state)
            logging.debug("|            Game Status - {}".format(gstatus))
            val = 0.5

            if gstatus == 0:
                val = 0
            elif gstatus == 1:
                val = 1
            set_state_value(state, val)
        return st_values[state]



def check_game_status(state):
    """Return game status by current board status.

        Args:
            state (tuple): Current board state

        Returns:
            int:
                -1: game in progress
                2: draw game,
                0 or 1 for finished game(Circle or Cross).
        """
    circles = []
    crosses = []
    binprogress = False

    dataCC = fromTupletoArray(state)
    for i in range(9):
        if dataCC[i] == 0:
            circles.append(i)
        if dataCC[i] == 1:
            crosses.append(i)
        if dataCC[i] == -1:
            binprogress = True
    circles.sort()
    crosses.sort()

    if circles.__len__() > 2:
        if see_the_pattern(circles) == 1:
            return 0
    if crosses.__len__() > 2:
        if see_the_pattern(crosses) == 1:
            return 1

    if binprogress:
        return -1
    else:
        return 2

def see_the_pattern(list):
    for i in range(list.__len__()):
        for j in range(list.__len__()):
            for k in range(list.__len__()):
                if i == list.__len__() or j == list.__len__() or k == list.__len__():
                    continue
                if tic_tac_pat(i, j, k, list) == 1:
                    return 1
    return 0

def tic_tac_pat(a, b, c, list):
    if list[a] == 0:
        if list[b] == 1:
            if list[c] == 2:
                return 1
        elif list[b] == 3:
            if list[c] == 6:
                return 1
        elif list[b] == 4:
            if list[c] == 8:
                return 1
    elif list[a] == 1:
        if list[b] == 4:
            if list[c] == 7:
                return 1
    elif list[a] == 2:
        if list[b] == 4:
            if list[c] == 6:
                return 1
        if list[b] == 5:
            if list[c] == 8:
                return 1
    elif list[a] == 3:
        if list[b] == 4:
            if list[c] == 5:
                return 1
    elif list[a] == 6:
        if list[b] == 7:
            if list[c] == 8:
                return 1
    return 0

def after_action_state(state, action):
    """Execute an action and returns resulted state.
    For now, we assume that agent playes with the Cross

    Args:
        state: Board status
        action (int): Action to run

    Returns:
        Tuple: New state - if action can be executed
               Null  - if action can't be executed
    """
    lState = fromTupletoArray(state)

    if(lState[action] == -1):
        lState[action] = 1
        return tuple(lState)
    else:
        return tuple()

def fromTupletoArray(state):
    lState = list()
    for i in range(len(state)):
        lState.append(state[i])
    return lState
