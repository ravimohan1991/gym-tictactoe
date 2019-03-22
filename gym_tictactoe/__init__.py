from gym.envs.registration import register

register(
    id='tictactoe-v1',
    entry_point='gym_tictactoe.envs:TicTacToe',
)
register(
    id='tictactoe-anagent-v1',
    entry_point='gym_tictactoe.agent:AnAgent',
)
