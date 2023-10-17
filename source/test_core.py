from datetime import datetime

import unittest

from core import EnergyConsumptionLog, EnergyConsumptionLogger


class TestEnergyConsumptionLog(unittest.TestCase):
    def test_create_energy_consumption_log(self):
        """Tests that an energy consumption log is created
        properly depending on the turned_on value and delta
        consumption."""
        log = EnergyConsumptionLog(
            timestamp=datetime(2023, 10, 17), delta_consumption=+0.53
        )
        self.assertEqual(log.timestamp, datetime(2023, 10, 17))
        self.assertEqual(log.delta_consumption, +0.53)
        self.assertEqual(str(log), "1697497200.0:0.53")

        log = EnergyConsumptionLog(
            timestamp=datetime(2024, 2, 29), delta_consumption=-0.143
        )
        self.assertEqual(log.timestamp, datetime(2024, 2, 29))
        self.assertEqual(log.delta_consumption, -0.143)
        self.assertEqual(str(log), "1709164800.0:-0.143")

        log = EnergyConsumptionLog(
            timestamp=datetime(2024, 2, 29), delta_consumption=-0.143, turned_on=False
        )
        self.assertEqual(log.timestamp, datetime(2024, 2, 29))
        self.assertEqual(log.delta_consumption, 0)
        self.assertEqual(str(log), "1709164800.0:0")


class TestEnergyConsumptionLogger(unittest.TestCase):
    def test_add_log(self):
        """Tests that a raw energy consumption log in the format
        `<Unix epoch> Delta <signed float>` is successfully processed
        into an EnergyConsumptionLog object and added to the
        _energy_consumption_logs attribute of the Logger."""
        logger = EnergyConsumptionLogger()

        raw_log = "1544206563 Delta +0.5"
        logger.add_log(raw_log)
        processed_log = logger._energy_consumption_logs["1544206563.0:0.5"]
        self.assertEqual(processed_log.timestamp, datetime(2018, 12, 7, 18, 16, 3))
        self.assertEqual(processed_log.delta_consumption, +0.5)

        raw_log = "1544210163 Delta -0.5123"
        logger.add_log(raw_log)
        processed_log = logger._energy_consumption_logs["1544210163.0:-0.5123"]
        self.assertEqual(processed_log.timestamp, datetime(2018, 12, 7, 19, 16, 3))
        self.assertEqual(processed_log.delta_consumption, -0.5123)

        raw_log = "1544210163      Delta     -05123"
        logger.add_log(raw_log)
        processed_log = logger._energy_consumption_logs["1544210163.0:-5123.0"]
        self.assertEqual(processed_log.timestamp, datetime(2018, 12, 7, 19, 16, 3))
        self.assertEqual(processed_log.delta_consumption, -5123)

        raw_log = "1544210163 TurnOff"
        logger.add_log(raw_log)
        processed_log = logger._energy_consumption_logs["1544210163.0:0"]
        self.assertEqual(processed_log.timestamp, datetime(2018, 12, 7, 19, 16, 3))
        self.assertEqual(processed_log.delta_consumption, 0)

        logger._energy_consumption_logs = dict()
        raw_log = "1544210163 TurnedOff"
        logger.add_log(raw_log)
        self.assertEqual(len(logger._energy_consumption_logs), 0)

        raw_log = "1544210163 Delta"
        logger.add_log(raw_log)
        self.assertEqual(len(logger._energy_consumption_logs), 0)

        raw_log = "EOF"
        logger.add_log(raw_log)
        self.assertEqual(len(logger._energy_consumption_logs), 0)

    def test_get_logs(self):
        """Tests that when provided with a sequence of raw energy logs
        the EnergyConsumptionLogger correctly processes those as EnergyConsumptionLog
        objects and then returns them in a list in chronological order."""
        logger = EnergyConsumptionLogger()

        for raw_log in [
            "1544206562 TurnOff",
            "1544206563 Delta +0.5",
            "1544210163 Delta -0.25",
            "1544210163 Delta -0.25",
            "1544211963 Delta +0.75",
            "1544213763 TurnOff",
        ]:
            logger.add_log(raw_log)

        self.assertListEqual(
            [str(log) for log in logger.get_logs()],
            [
                "1544206562.0:0",
                "1544206563.0:0.5",
                "1544210163.0:-0.25",
                "1544211963.0:0.75",
                "1544213763.0:0",
            ],
        )
        logger._energy_consumption_logs = dict()

        for raw_log in [
            "1544206562 TurnOff",
            "1544206563 Delta +0.5",
            "1544206563 Delta +0.5",
            "1544210163 Delta                               -0.25",
            "1544210163 Delta -0.25",
            "15442101634123123 Delta -0.25",
            "1544211963 Delta +0.5123=====",
            "1544213763 TurnedOff",
            "EOF",
            "EOF",
            "1544213763 Delta TurnedOff",
            "1544213763 turnoff",
            "1231231123 TurnOff",
            "turnoff 1544213763",
        ]:
            logger.add_log(raw_log)

        self.assertListEqual(
            [str(log) for log in logger.get_logs()],
            [
                "1231231123.0:0",
                "1544206562.0:0",
                "1544206563.0:0.5",
                "1544210163.0:-0.25",
                "1544211963.0:0.5123",
            ],
        )


if __name__ == "__main__":
    unittest.main()
