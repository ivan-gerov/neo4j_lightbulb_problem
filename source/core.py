from typing import List, Dict

import re
from datetime import datetime


class EnergyConsumptionLog:
    """
    A class that represents a single energy log.

    Attributes:
        `timestamp : datetime`
            The timestamp of the energy log.\n
        `delta_consumption : float`
            The change in energy consumption represented by a float (e.g. +15.15, -2.1).\n
        `turned_on : bool, default True`
            Signifies that the consumator is turned on. If False, the delta_consumption is set to 0.
    """

    def __init__(
        self,
        timestamp: datetime,
        delta_consumption: float = None,
        turned_on: bool = True,
    ):
        self.timestamp = timestamp

        if delta_consumption and turned_on:
            self.delta_consumption = delta_consumption
        else:
            self.delta_consumption = 0

    def __str__(self) -> str:
        return f"{self.timestamp.timestamp()}:{self.delta_consumption}"


class EnergyConsumptionLogger:
    """
    A class that logs energy consumption data.

    Attributes:
        `energy_consumption_logs : Dict[str, EnergyConsumptionLog]`
            A dictionary of raw energy consumption logs to parsed EnergyConsumptionLog objects.
    """

    ENERGY_LOG_REGEX: re.Pattern = re.compile(
        r"(?:[>]\s)?([0-9]{,10})\s+(TurnOff|(Delta\s+([+-](?:\d+\.\d+|\d+))))"
    )

    def __init__(self):
        self._energy_consumption_logs: Dict[str, EnergyConsumptionLog] = dict()

    def add_log(self, raw_energy_log: str):
        processed_energy_log = self._process_energy_log(raw_energy_log)

        if not processed_energy_log:
            return

        self._energy_consumption_logs.update(processed_energy_log)

    def batch_add_logs(self, raw_energy_logs: List[str]):
        for raw_energy_log in raw_energy_logs:
            self.add_log(raw_energy_log)

    def _process_energy_log(
        self, raw_energy_log: str
    ) -> Dict[str, EnergyConsumptionLog]:
        """Processes a raw energy log and returns a Dict mapping a
        standardized raw energy log to EnergyConsumptionLog object"""
        match_obj = self.ENERGY_LOG_REGEX.match(raw_energy_log)

        if not match_obj:
            return

        m_groups = match_obj.groups()

        timestamp = datetime.fromtimestamp(float(m_groups[0]))

        if "TurnOff" in raw_energy_log:
            energy_log = EnergyConsumptionLog(timestamp=timestamp, turned_on=False)
        elif "Delta" in raw_energy_log:
            delta_consumption = float(m_groups[-1])
            energy_log = EnergyConsumptionLog(
                timestamp=timestamp, delta_consumption=delta_consumption
            )
        else:
            return

        return {str(energy_log): energy_log}

    def get_logs(self) -> List[EnergyConsumptionLog]:
        """Returns the energy consumption logs in a chronological order"""
        return [
            self._energy_consumption_logs[timestamp]
            for timestamp in sorted(self._energy_consumption_logs.keys())
        ]


class EnergyConsumer:
    """
    A class that represents an energy consumer. This could be
    a lightbulb or some other kind of energy consumer.

    Attributes:
        `kind : str`
            The kind of energy consumer - e.g. "lightbulb".\n
        `max_consumption : float`
            Max possible consumption of the energy consumer in Watts. It must be a positive value\n
        `current_consumption : float`
            The current consumption of the energy consumer - value between 0 (0% of max_consumption) and 1 (100% of max_consumption).\n
        `energy_consumption_logger : EnergyConsumptionLogger`
            Used to log energy consumption for the consumer.
    """

    def __init__(self, kind: str, max_consumption: float):
        if max_consumption < 0:
            raise ValueError(
                f"Max consumption should be a positive value! max_consumption:{max_consumption}"
            )

        self.kind = kind
        self.max_consumption = max_consumption
        self.current_consumption = 1
        self.energy_consumption_logger = EnergyConsumptionLogger()

    def set_consumption(self, delta_change: float):
        """Sets the current energy consumption for the energy consumer by
        passing a delta change augment the current value."""
        if delta_change < 0:
            self.current_consumption = max(0, self.current_consumption + delta_change)
        elif delta_change > 0:
            self.current_consumption = min(1, self.current_consumption + delta_change)
        else:
            self.current_consumption = 0


class EnergyEstimator:
    """A class that estimates the energy used by an energy consumator in
    the course of a sequence of enery logs."""

    def estimate_energy(self, energy_consumer: EnergyConsumer) -> float:
        energy_logs = energy_consumer.energy_consumption_logger.get_logs()

        total_energy_estimate = 0

        for current_log in range(len(energy_logs)):
            next_log = current_log + 1
            if next_log > len(energy_logs) - 1:
                break

            hours_elapsed_between_logs = (
                (
                    energy_logs[next_log].timestamp - energy_logs[current_log].timestamp
                ).total_seconds()
                / 60
                / 60
            )

            energy_consumer.set_consumption(energy_logs[current_log].delta_consumption)

            consumption_between_logs = hours_elapsed_between_logs * (
                energy_consumer.current_consumption * energy_consumer.max_consumption
            )

            total_energy_estimate += consumption_between_logs

        return total_energy_estimate


if __name__ == "__main__":
    lightbulb = EnergyConsumer(kind="lightbulb", max_consumption=5)
    energy_estimator = EnergyEstimator()

    try:
        while True:
            line = input()
            if "EOF" in line:
                break
            lightbulb.energy_consumption_logger.add_log(line)
    except EOFError:
        pass  # Handle Ctrl-D, etc.

    estimated_energy = energy_estimator.estimate_energy(lightbulb)
    print(f"Estimated energy used: {estimated_energy} Wh")
