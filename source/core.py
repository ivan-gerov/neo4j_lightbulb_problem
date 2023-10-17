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
        r"([0-9]{,10})\s+(TurnOff|(Delta\s+([+-](?:\d+\.\d+|\d+))))"
    )

    def __init__(self):
        self._energy_consumption_logs: Dict[str, EnergyConsumptionLog] = dict()

    def add_log(self, raw_energy_log: str):
        processed_energy_log = self._process_energy_log(raw_energy_log)

        if not processed_energy_log:
            return

        self._energy_consumption_logs.update(processed_energy_log)

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


# class EnergyEstimator:
#     """A class that estimates the energy used by an energy consumator in
#     the course of a sequence of enery logs."""

#     def estimate_energy(self, energy_logs: List[EnergyConsumptionLog]) -> float:
#         total_energy_estimate = 0

#         current_expendature = 0

#         next_ = 0
#         for energy_log in energy_logs:
#             if next_ > len(energy_logs):
#                 break

#             time_elapsed_between_logs_secs = (
#                 energy_logs[next_].timestamp - energy_log.timestamp
#             )

#             current_expendature = max(
#                 0, current_expendature + energy_log.delta_consumption
#             )
#             total_energy_estimate = max(
#                 0, (time_elapsed_between_logs_secs / 60 / 60) * current_expendature
#             )
