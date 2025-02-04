def printResult(swarm, iteration):
    return """Iteration: {iter}

Best Position: {bestpos}
Best Final Func: {finalfunc}
----------------------------
""".format(
        iter=iteration,
        bestpos=swarm.globalBestPosition,
        finalfunc=swarm.globalBestFinalFunc,
    )
