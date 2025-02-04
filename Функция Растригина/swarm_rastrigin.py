import numpy as np

from particleswarm import Swarm


class SwarmRastrigin(Swarm):
    def __init__(
        self,
        swarmsize: int,
        minvalues: list[float],
        maxvalues: list[float],
        currentVelocityRatio: float,
        localVelocityRatio: float,
        globalVelocityRatio: float,
    ):
        super().__init__(
            swarmsize,
            minvalues,
            maxvalues,
            currentVelocityRatio,
            localVelocityRatio,
            globalVelocityRatio,
        )

    def _finalFunc(self, position):
        function = 10.0 * len(self.minvalues) + sum(
            position * position - 10.0 * np.cos(2 * np.pi * position)
        )
        penalty = self._getPenalty(position, 10000.0)

        return function + penalty
