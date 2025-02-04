import numpy as np
from numpy.random import rand


class Particle:
    """
    Класс, описывающий одну частицу
    """

    def __init__(self, swarm):
        """
        swarm - экземпляр класса Swarm, хранящий параметры алгоритма, список частиц и лучшее значение роя в целом
        position - начальное положение частицы (список)
        """
        # Текущее положение частицы
        self._currentPosition = self._getInitPosition(swarm)

        # Лучшее положение частицы
        self._localBestPosition = self._currentPosition[:]

        # Лучшее значение целевой функции
        self._localBestFinalFunc = swarm.getFinalFunc(self._currentPosition)

        self._velocity = self._getInitVelocity(swarm)

    @property
    def position(self):
        return self._currentPosition

    @property
    def velocity(self):
        return self._velocity

    def _getInitPosition(self, swarm):
        """
        Возвращает список со случайными координатами для заданного интервала изменений
        """
        return (
            rand(swarm.dimension) * (swarm.maxvalues - swarm.minvalues)
            + swarm.minvalues
        )

    def _getInitVelocity(self, swarm):
        """
        Сгенерировать начальную случайную скорость
        """
        assert len(swarm.minvalues) == len(self._currentPosition)
        assert len(swarm.maxvalues) == len(self._currentPosition)

        minval = -(swarm.maxvalues - swarm.minvalues)
        maxval = swarm.maxvalues - swarm.minvalues

        return rand(swarm.dimension) * (maxval - minval) + minval

    def nextIteration(self, swarm):
        # Случайный вектор для коррекции скорости с учетом лучшей позиции данной частицы
        rnd_currentBestPosition = rand(swarm.dimension)

        # Случайный вектор для коррекции скорости с учетом лучшей глобальной позиции всех частиц
        rnd_globalBestPosition = rand(swarm.dimension)

        veloRatio = swarm.localVelocityRatio + swarm.globalVelocityRatio
        commonRatio = (
            2.0
            * swarm.currentVelocityRatio
            / (np.abs(2.0 - veloRatio - np.sqrt(veloRatio**2 - 4.0 * veloRatio)))
        )

        # Посчитать новую скорость
        newVelocity_part1 = commonRatio * self._velocity

        newVelocity_part2 = (
            commonRatio
            * swarm.localVelocityRatio
            * rnd_currentBestPosition
            * (self._localBestPosition - self._currentPosition)
        )

        newVelocity_part3 = (
            commonRatio
            * swarm.globalVelocityRatio
            * rnd_globalBestPosition
            * (swarm.globalBestPosition - self._currentPosition)
        )

        self._velocity = newVelocity_part1 + newVelocity_part2 + newVelocity_part3

        # Обновить позицию частицы
        self._currentPosition += self._velocity

        finalFunc = swarm.getFinalFunc(self._currentPosition)
        if finalFunc < self._localBestFinalFunc:
            self._localBestPosition = self._currentPosition[:]
            self._localBestFinalFunc = finalFunc
