import gym
import gym_tictactoe
import pyglet
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

EPSILON = 0.3
ALPHA = 0.4

an_agent = gym.make("tictactoe-anagent-v1") # AnAgent(EPSILON, ALPHA)  # The Agent plays with mark X
env = gym.make("tictactoe-v1")  # TicTacToe(an_agent)
an_agent.setRandomizer(env.np_random)

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
