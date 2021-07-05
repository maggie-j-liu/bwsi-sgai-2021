from gym.envs.registration import register

register(
    id='SGW-v0',
    entry_point='gym_sgw.envs.SGWEnv:SGW'
)
