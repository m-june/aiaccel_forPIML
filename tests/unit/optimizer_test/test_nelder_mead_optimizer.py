from unittest.mock import patch

import numpy as np
import pytest

from aiaccel.common import goal_maximize
from aiaccel.converted_parameter import ConvertedParameterConfiguration
from aiaccel.optimizer import NelderMead, NelderMeadOptimizer
from aiaccel.parameter import HyperParameterConfiguration
from tests.base_test import BaseTest


class TestNelderMeadOptimizer(BaseTest):

    @pytest.fixture(autouse=True)
    def setup_optimizer(self, clean_work_dir):
        self.optimizer = NelderMeadOptimizer(self.load_config_for_test(self.configs["config.json"]))
        yield
        self.optimizer = None

    def test_generate_initial_parameter(self):
        expected = [
            {'parameter_name': 'x1', 'type': 'uniform_float', 'value': 0.74},
            {'parameter_name': 'x2', 'type': 'uniform_float', 'value': 2.98},
            {'parameter_name': 'x3', 'type': 'uniform_float', 'value': 3.62},
            {'parameter_name': 'x4', 'type': 'uniform_float', 'value': 0.9},
            {'parameter_name': 'x5', 'type': 'uniform_float', 'value': 1.99},
            {'parameter_name': 'x6', 'type': 'uniform_float', 'value': -2.78},
            {'parameter_name': 'x7', 'type': 'uniform_float', 'value': 1.0},
            {'parameter_name': 'x8', 'type': 'uniform_float', 'value': 4.97},
            {'parameter_name': 'x9', 'type': 'uniform_float', 'value': 1.98},
            {'parameter_name': 'x10', 'type': 'uniform_float', 'value': 4.03}
        ]

        _optimizer = NelderMeadOptimizer(self.load_config_for_test(self.configs["config.json"]))
        _optimizer._rng = np.random.RandomState(0)
        _nelder_mead = _optimizer.generate_initial_parameter()
        self.optimizer._rng = np.random.RandomState(0)

        with patch.object(self.optimizer, "nelder_mead", None):
            assert self.optimizer.generate_initial_parameter() == expected

        with patch.object(self.optimizer, "nelder_mead", _nelder_mead):
            assert self.optimizer.generate_initial_parameter() is None

    def test_pre_process(self):
        assert self.optimizer.pre_process() is None
        self.optimizer.config.optimize.goal = [goal_maximize]
        self.optimizer.post_process()
        assert self.optimizer.pre_process() is None

    def test_check_result(self, setup_result):
        self.optimizer.pre_process()
        self.optimizer.generate_initial_parameter()
        setup_result(1)
        # params = self.optimizer.nelder_mead.get_ready_parameters()
        params = self.optimizer.get_ready_parameters()
        print(params)
        assert self.optimizer.check_result() is None

    def test_generate_parameter(
        self,
        load_test_config_org,
        setup_result
    ):
        self.optimizer.pre_process()
        # config = load_test_config()
        config = self.load_config_for_test(self.configs["config_nelder_mead.json"])
        self.optimizer.params = ConvertedParameterConfiguration(
            HyperParameterConfiguration(config.optimize.parameters), convert_log=True, convert_int=True,
            convert_choices=True, convert_sequence=True,
        )
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(
            self.optimizer.params.get_parameter_list(),
            rng=rng
        )
        # params = self.optimizer.nelder_mead.get_ready_parameters()
        params = self.optimizer.get_ready_parameters()
        assert params is not None
        setup_result(len(params))
        assert len(self.optimizer.generate_parameter()) > 0

        self.optimizer.nelder_mead._max_itr = 0
        assert self.optimizer.generate_parameter() is None

        # if len(self.parameter_pool) == 0:
        self.optimizer.nelder_mead = NelderMead(self.optimizer.params.get_parameter_list(), rng=rng)
        self.optimizer.generate_initial_parameter()
        with patch.object(self.optimizer, 'nelder_mead_main', return_value=[]):
            with patch.object(self.optimizer, 'parameter_pool', []):
                assert self.optimizer.generate_parameter() is None

    def test_generate_parameter2(
        self,
        load_test_config_org,
        setup_result
    ):
        self.optimizer.pre_process()
        config = self.load_config_for_test(self.configs["config.json"])
        self.optimizer.params = ConvertedParameterConfiguration(
            HyperParameterConfiguration(config.optimize.parameters), convert_log=True, convert_int=True,
            convert_choices=True, convert_sequence=True,
        )
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(
            self.optimizer.params.get_parameter_list(),
            rng=rng
        )
        # params = self.optimizer.nelder_mead.get_ready_parameters()
        # params = self.optimizer.get_ready_parameters()
        params = self.optimizer.nelder_mead._executing
        setup_result(len(params))
        assert len(self.optimizer.generate_parameter()) > 0

    def test_update_ready_parameter_name(
        self,
        load_test_config_org
    ):
        self.optimizer.pre_process()
        config = self.load_config_for_test(self.configs["config.json"])
        self.optimizer.params = ConvertedParameterConfiguration(
            HyperParameterConfiguration(config.optimize.parameters), convert_log=True, convert_int=True,
            convert_choices=True, convert_sequence=True,
        )
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(
            self.optimizer.params.get_parameter_list(),
            rng=rng
        )
        self.optimizer.nelder_mead._executing.append({'vertex_id': '001'})

        pool_p = {"vertex_id": "001"}
        assert self.optimizer.update_ready_parameter_name(pool_p, 'new') is None

        pool_p = {"vertex_id": "002"}
        assert self.optimizer.update_ready_parameter_name(pool_p, 'new') is None

    def test_get_ready_parameters(
        self,
        load_test_config_org
    ):
        self.optimizer.pre_process()
        config = load_test_config_org()
        config = self.load_config_for_test(self.configs["config.json"])
        self.optimizer.params = ConvertedParameterConfiguration(
            HyperParameterConfiguration(config.optimize.parameters), convert_log=True, convert_int=True,
            convert_choices=True, convert_sequence=True,
        )

        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(
            self.optimizer.params.get_parameter_list(),
            rng=rng
        )
        assert len(self.optimizer.get_ready_parameters()) == 11

    def test_get_nm_results(self):
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(self.optimizer.params.get_parameter_list(), rng=rng)

        self.optimizer.get_nm_results()

        expected = [
            {
                'vertex_id': 'abc',
                'parameters': [{'parameter_name': 'x1', 'value': -4.87}, {'parameter_name': 'x2', 'value': -0.71}],
                'state': 'WaitInitialize',
                'itr': 1,
                'index': 1,
                'out_of_boundary': False
            },
            {
                'parameters': [{'parameter_name': 'x1', 'value': -4.87}, {'parameter_name': 'x2', 'value': -0.71}],
                'state': 'WaitInitialize',
                'itr': 1,
                'index': 1,
                'out_of_boundary': False
            }
        ]

        result_content = {'trial_id': 0, 'result': 123}
        with patch.object(self.optimizer.nelder_mead, '_executing', expected):
            with patch.object(self.optimizer.storage.result, 'get_any_trial_objective', return_value=result_content):
                self.optimizer.get_nm_results()

    def test__add_result(self):
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(self.optimizer.params.get_parameter_list(), rng=rng)
        self.optimizer.generate_initial_parameter()
        nm_results = [
            {
                'vertex_id': '0001',
                'parameters': [{'parameter_name': 'x1', 'value': -4.87}, {'parameter_name': 'x2', 'value': -0.71}],
                'state': 'WaitInitialize',
                'itr': 1,
                'index': 1,
                'out_of_boundary': False
            },
        ]
        order = [
            {
                'vertex_id': '0001',
                'parameters': [{'parameter_name': 'x1', 'value': -4.87}, {'parameter_name': 'x2', 'value': -0.71}]
            }
        ]
        order2 = [
            {
                'vertex_id': 'invalid',
                'parameters': [{'parameter_name': 'x1', 'value': -4.87}, {'parameter_name': 'x2', 'value': -0.71}]
            }
        ]
        assert self.optimizer._add_result(nm_results) is None

        with patch.object(self.optimizer, 'order', order):
            assert self.optimizer._add_result(nm_results) is None

        with patch.object(self.optimizer, 'order', order2):
            assert self.optimizer._add_result(nm_results) is None

    def test_nelder_mead_main(self):
        rng = np.random.RandomState(0)
        self.optimizer.nelder_mead = NelderMead(self.optimizer.params.get_parameter_list(), rng=rng)
        self.optimizer.generate_initial_parameter()
        self.optimizer.nelder_mead_main()

        with patch.object(self.optimizer.nelder_mead, 'search', return_value=None):
            assert self.optimizer.nelder_mead_main() is None

        with patch.object(self.optimizer.nelder_mead, 'search', return_value=[]):
            assert self.optimizer.nelder_mead_main() is None

    def test__get_all_trial_id(self):
        with patch.object(self.optimizer.storage.trial, 'get_all_trial_id', return_value=None):
            assert self.optimizer._get_all_trial_id() == []

        expected = [1, 2, 3]
        with patch.object(self.optimizer.storage.trial, 'get_all_trial_id', return_value=expected):
            assert self.optimizer._get_all_trial_id() == expected
