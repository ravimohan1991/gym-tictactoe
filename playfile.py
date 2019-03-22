import gym
import gym_tictactoe
import pyglet
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Change these values in an_agent.py too for experimentation
EPSILON = 0.3
ALPHA = 0.4

env = gym.make("tictactoe-v1")  # TicTacToe(an_agent)


logging.debug("+-------------------------------------------")
logging.debug("| Game Agent Parameters:")
logging.debug("| Seed is {}".format(env.sSeed))
logging.debug("| Exploration Probability is {}".format(EPSILON))
logging.debug("| Step Size Parameter {}".format(ALPHA))
logging.debug("+-------------------------------------------")
logging.debug(" ")

state = env.reset()

# show start board for human agent and begin gameplay
env.initializeState(state)
env.render(state)
pyglet.app.run()
env.render(state)
input()
