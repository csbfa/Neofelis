"""
Module for cleaning excess signals.
"""

import copy
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Signals")

class Signals():

    def __init__(self):
        self._logger.info("Method call: Signals.__init__")
        pass

    def removeSignals(self, genes, signals):
        self._logger.info("Method call: removeSignals")
        """
        genes:   List of Iteration objects.
        signals: List of signals(any object with a location tuple) to filter

        return:  A filtered list of the singals which does not contain any signal which has a center of
                mass inside a gene

        A helper function for filter signals that expects genes and signals on the same direction.
        """

        remainingSignals = copy.copy(signals)
    
        for signal in signals:
            nearStart = False
            for gene in genes:
                center = (signal.location[0] + signal.location[1])/2
                nearStart = nearStart or abs(gene.location[0] - center) < 100
                if min(gene.location) < center < max(gene.location):
                    remainingSignals.remove(signal)
                    break
            if not nearStart and signal in remainingSignals:
                remainingSignals.remove(signal)
            
        return remainingSignals

    def filterSignals(self, genes, signals, pipeline):
        self._logger.info("Method call: filterSignals")
        """
        genes:   List of Iteration objects.
        signals: List of signals(any object with a location tuple) to filter

        return:  A filtered list of the signals which does not contain any signal which has a center of
                mass inside a gene
        """

        forwardGenes = list(filter(lambda x: x.location[0] < x.location[1], genes))
        forwardSignals = list(filter(lambda x: x.location[0] < x.location[1], signals))
        if pipeline.stopped():
            return

        forwardResult = self.removeSignals(forwardGenes, forwardSignals)

        reverseGenes = list(filter(lambda x: x.location[1] < x.location[0], genes))
        reverseSignals = list(filter(lambda x: x.location[1] < x.location[0], signals))
        if pipeline.stopped():
            return

        reverseResult = self.removeSignals(reverseGenes, reverseSignals)
    
        return forwardResult + reverseResult
