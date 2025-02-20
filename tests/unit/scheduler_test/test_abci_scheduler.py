from aiaccel.scheduler import AbciScheduler

from tests.base_test import BaseTest


class TestAbciScheduler(BaseTest):

    def test_get_stats(
        self,
        clean_work_dir,
        config_json,
        data_dir,
        fake_process,
        database_remove
    ):
        database_remove()
        scheduler = AbciScheduler(self.load_config_for_test(self.configs["config.json"]))
        xml_path = data_dir.joinpath('qstat.xml')
        fake_process.register_subprocess(['qstat', '-xml'], stdout=[])
        assert scheduler.get_stats() is None

        with open(xml_path, 'r') as f:
            xml_string = f.read()

        fake_process.register_subprocess(
            ['qstat', '-xml'],
            stdout=[xml_string]
        )
        assert scheduler.get_stats() is None

    def test_parse_trial_id(
        self,
        config_json,
        database_remove
    ):
        database_remove()
        scheduler = AbciScheduler(self.load_config_for_test(self.configs["config.json"]))
        s = {"name": "run_000005.sh"}
        trial_id = int(scheduler.parse_trial_id(s['name']))
        assert trial_id == 5

        s = {"name": "run_xxxxxx.sh"}
        trial_id = scheduler.parse_trial_id(s['name'])
        assert trial_id is None
