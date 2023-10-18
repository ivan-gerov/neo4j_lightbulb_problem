from datetime import datetime

import unittest

from core import (
    EnergyConsumptionLog,
    EnergyConsumptionLogger,
    EnergyConsumer,
    EnergyEstimator,
)


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


class TestEnergyConsumer(unittest.TestCase):
    def test_create_energy_consumer(self):
        """Tests that an energy consumer is created, all fields work as intended
        and one can access and add energy logs via the energy_consumption_logger."""
        lightbulb = EnergyConsumer(kind="lightbulb", max_consumption=5)
        self.assertEqual(lightbulb.kind, "lightbulb")
        self.assertEqual(lightbulb.current_consumption, 1)
        self.assertEqual(lightbulb.max_consumption, 5)
        self.assertEqual(lightbulb.energy_consumption_logger.get_logs(), [])

        # Add an energy consumption log
        lightbulb.energy_consumption_logger.add_log("1544206563 Delta +0.5")
        self.assertEqual(
            str(lightbulb.energy_consumption_logger.get_logs()[0]), "1544206563.0:0.5"
        )

    def test_create_energy_consumer_invalid_max_consumption(self):
        """Tests that max_consumption must be a positive value."""
        with self.assertRaises(ValueError) as cm:
            lightbulb = EnergyConsumer(kind="lightbul", max_consumption=-5123123)
        self.assertEqual(
            str(cm.exception),
            "Max consumption should be a positive value! max_consumption:-5123123",
        )

    def test_set_consumption(self):
        """Tests that consumption can be set for the energy consumer based
        on a delta change (e.g. dimmer on a lightswitch). Also, assert
        that the minimum possible value is 0 and the maximum - the max_consumption
        of the energy consumer."""
        lightbulb = EnergyConsumer(kind="lightbulb", max_consumption=5)

        lightbulb.set_consumption(1)
        self.assertEqual(lightbulb.current_consumption, 1)

        lightbulb.set_consumption(-0.75)
        self.assertEqual(lightbulb.current_consumption, 0.25)

        lightbulb.set_consumption(-1.1525)
        self.assertEqual(lightbulb.current_consumption, 0)

        lightbulb.set_consumption(0)
        self.assertEqual(lightbulb.current_consumption, 0)

        lightbulb.set_consumption(5125)
        self.assertEqual(lightbulb.current_consumption, 1)


class TestEnergyEstimator(unittest.TestCase):
    def test_estimate_energy(self):
        """Tests that given a sequence of raw energy logs, an
        energy consumer can log those and then the estimator
        can estimate the energe used by the consumer."""
        energy_estimator = EnergyEstimator()

        lightbulb1 = EnergyConsumer(kind="lightbulb", max_consumption=5)
        lightbulb1.energy_consumption_logger.batch_add_logs(
            [
                "1544206562 TurnOff",
                "1544206563 Delta +0.5",
                "1544210163 TurnOff",
            ]
        )
        estimated_energy = energy_estimator.estimate_energy(lightbulb1)
        self.assertEqual(estimated_energy, 2.5)

        lightbulb2 = EnergyConsumer(kind="lightbulb", max_consumption=5)
        lightbulb2.energy_consumption_logger.batch_add_logs(
            [
                "1544206562 TurnOff",
                "1544206563 Delta +0.5",
                "1544210163 Delta -0.25",
                "1544210163 Delta -0.25",
                "1544211963 Delta +0.75",
                "1544213763 TurnOff",
            ]
        )
        estimated_energy = energy_estimator.estimate_energy(lightbulb2)
        self.assertEqual(estimated_energy, 5.625)

    def test_estimate_energy_invalid_logs(self):
        """Tests that the energy estimator can handle invalid logs"""
        energy_estimator = EnergyEstimator()

        lightbulb = EnergyConsumer(kind="lightbulb", max_consumption=5)
        lightbulb.energy_consumption_logger.batch_add_logs(
            [
                "1544206562 TurnOff",
                "1544206563 TurnedOff",
                "1544210163 TurnOff",
            ]
        )
        estimated_energy = energy_estimator.estimate_energy(lightbulb)
        self.assertEqual(estimated_energy, 0.0)
        lightbulb.energy_consumption_logger._energy_consumption_logs = dict()

        lightbulb.energy_consumption_logger.batch_add_logs(
            [
                "1544206562 TurnOff",
                "1544210163 Delta -0.25",
            ]
        )
        estimated_energy = energy_estimator.estimate_energy(lightbulb)
        self.assertEqual(estimated_energy, 0.0)


if __name__ == "__main__":
    unittest.main()
