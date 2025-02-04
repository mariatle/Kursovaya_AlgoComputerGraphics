from abc import ABCMeta, abstractmethod
from typing import Optional

import numpy as np

from .particle import Particle


class Swarm(metaclass=ABCMeta):
    """
    Базовый класс для роя частиц. Его надо переопределять для конкретной целевой функции
    """
    def __init__(
        self,
        swarmsize: int,
        minvalues: list[float],
        maxvalues: list[float],
        currentVelocityRatio: float,
        localVelocityRatio: float,
        globalVelocityRatio: float,
    ):
        """
        swarmsize - размер роя (количество частиц)
        minvalues - список, задающий минимальные значения для каждой координаты частицы
        maxvalues - список, задающий максимальные значения для каждой координаты частицы
        currentVelocityRatio - общий масштабирующий коэффициент для скорости
        localVelocityRatio - коэффициент, задающий влияние лучшей точки, найденной частицей на будущую скорость
        globalVelocityRatio - коэффициент, задающий влияние лучшей точки, найденной всеми частицами на будущую скорость
        """
        self._swarmsize = swarmsize

        assert len(minvalues) == len(maxvalues)
        assert (localVelocityRatio + globalVelocityRatio) > 4

        self._minvalues = np.array(minvalues[:])
        self._maxvalues = np.array(maxvalues[:])

        self._currentVelocityRatio = currentVelocityRatio
        self._localVelocityRatio = localVelocityRatio
        self._globalVelocityRatio = globalVelocityRatio

        self._globalBestFinalFunc: Optional[float] = None
        self._globalBestPosition = None

        self._swarm = self._createSwarm()

    def __getitem__(self, index):
        """
        Возвращает частицу с заданным номером
        """
        return self._swarm[index]

    def _createSwarm(self):
        """
        Создать рой из частиц со случайными координатами
        """
        return [Particle(self) for _ in range(self._swarmsize)]

    def nextIteration(self):
        """
        Выполнить следующую итерацию алгоритма
        """
        for particle in self._swarm:
            particle.nextIteration(self)

    @property
    def minvalues(self):
        return self._minvalues

    @property
    def maxvalues(self):
        return self._maxvalues

    @property
    def currentVelocityRatio(self):
        return self._currentVelocityRatio

    @property
    def localVelocityRatio(self):
        return self._localVelocityRatio

    @property
    def globalVelocityRatio(self):
        return self._globalVelocityRatio

    @property
    def globalBestPosition(self):
        return self._globalBestPosition

    @property
    def globalBestFinalFunc(self):
        return self._globalBestFinalFunc

    def getFinalFunc(self, position) -> float:
        assert len(position) == len(self.minvalues)

        finalFunc = self._finalFunc(position)

        if self._globalBestFinalFunc is None or finalFunc < self._globalBestFinalFunc:
            self._globalBestFinalFunc = finalFunc
            self._globalBestPosition = position[:]

        return finalFunc

    @abstractmethod
    def _finalFunc(self, position) -> float:
        return 0.0

    @property
    def dimension(self):
        """
        Возвращает текущую размерность задачи
        """
        return len(self.minvalues)

    def _getPenalty(self, position, ratio):
        """
        Рассчитать штрафную функцию
        position - координаты, для которых рассчитывается штраф
        ratio - вес штрафа
        """
        penalty1 = sum(
            [
                ratio * abs(coord - minval)
                for coord, minval in zip(position, self.minvalues)
                if coord < minval
            ]
        )

        penalty2 = sum(
            [
                ratio * abs(coord - maxval)
                for coord, maxval in zip(position, self.maxvalues)
                if coord > maxval
            ]
        )

        return penalty1 + penalty2
