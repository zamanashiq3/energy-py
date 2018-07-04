"""
The base class for energy_py environments
"""
import collections
import logging

import numpy as np
import pandas as pd

import energy_py
from energy_py.common.spaces import ContinuousSpace, DiscreteSpace, GlobalSpace
from energy_py.common.utils import load_csv


logger = logging.getLogger(__name__)


class BaseEnv(object):
    """
    The base environment class for time series environments

    args
        dataset (str) located in energy_py/experiments/datasets
        episode_sample (str) fixed, random

    Most energy problems are time series problems
    The BaseEnv has functionality for working with time series data
    """
    def __init__(self,
                 dataset='example',
                 episode_sample='fixed',
                 episode_length=2016):

        logger.info('Initializing environment {}'.format(repr(self)))

        self.state_space = GlobalSpace('state').from_dataset(dataset)
        self.observation_space = GlobalSpace('observation').from_dataset(dataset)

        if self.episode_sample == 'random':
            self.episode_sample = self.random_sample

        if self.episode_sample == 'fixed':
            self.episode_sample = self.fixed_sample

        self.episode_length = min(
            int(episode_length),
            self.state_space.shape[0]
        )

    def reset(self):
        """
        Resets the state of the environment, returns an initial observation

        returns
            observation (np array) initial observation
        """
        logger.debug('Resetting environment')

        self.info = collections.defaultdict(list)
        self.outputs = collections.defaultdict(list)

        self.sample_episode()

        logger.debug(
            'Episode start {} Episode end {}'.format(
                self.state_space.episode.index[0],
                self.state_space.episode.index[-1])
        )

        return self._reset()

    def step(self, action):
        """
        Run one timestep of the environment's dynamics.

        args
            action (object) an action provided by the environment
            episode (int) the current episode number

        returns
            observation (np array) agent's observation of the environment
            reward (np.float)
            done (boolean)
            info (dict) auxiliary information
        """
        action = np.array(action).reshape(1, *self.action_space.shape)

        logger.debug('step {} action {}'.format(self.steps, action))

        return self._step(action)

    def sample_episode(self):
        """
        Samples a single episode from the state and observation dataframes

        returns
            observation_ep (pd.DataFrame)
            state_ep (pd.DataFrame)
        """
        logging.debug('Sampling episode'.format(self.episode_sample))

        start, end = self.episode_sample()

        state_ep = self.state_space.sample_episode(start, end)
        obs_ep = self.observation_space.sample_episode(start, end)
        assert state_ep.shape[0] == obs_ep.shape[0]

        return state_ep, obs_ep

    def random_sample(self):
        start = np.random.randint(
            low=0,
            high=self.state_space.shape[0] - self.episode_length
        )
        return start, start + self.episode_length

    def fixed_sample(self):
        if self.episode_length == 0:
            ep_len = self.state_space.shape[0],
        else:
            ep_len = self.episode_length

        start = self.state_space.shape[0] - self.episode_length

        return start, start + ep_len

    def get_state_variable(self, variable_name):
        return self.state[self.state.info.index(variable_name)]

    def update_info(self, **kwargs):
        for name, data in kwargs.items():
            self.info[name].append(data)
        return self.info
