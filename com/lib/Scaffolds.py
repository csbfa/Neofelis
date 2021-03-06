"""
This module contains functions and Classes for finding contiguous regions
of genes and removing conflicting genes.

"""

import copy, functools
from Library import Exceptions
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Scaffolds")

class Scaffolds():

    class Scaffold():
        """
        This structure contains the information that describes a scaffold,
        where it starts, where is stops, and the genes contained in it.
        """

        def __init__(self, start, stop, genes):
            self._logger.info("Method call: Scaffold.__init__")
            self.start = start
            self.stop = stop
            self.genes = genes
        
        def __str__(self):
            self._logger.info("Method call: Scaffold.__str__")
            result = "<"
            result += "start = " + str(self.start) + ", "
            result += "stop = " + str(self.stop) + ", "
            result += "genes = " + str(self.genes) + ">"
            return result

    def extractScaffolds(self, genes, scaffoldingDistance = 100):
        self._logger.info("Method call: extractScaffolds")
        """
        genes:               A list of Iteration objects.
        scaffoldingDistance: Maximum distance between neighboring genes in a scaffold.

        return:              A 2-tuple, first object is a list of Scaffold objects for the forward genes,
                             and the second a list of scaffold objects for the reverse genes.
        """

        forwardScaffolds, reverseScaffolds = [], []

        for gene in genes:

            if gene.location[0] < gene.location[1]:
                newScaffold = self.Scaffold(gene.location[0], gene.location[1], [gene])
                scaffolds = forwardScaffolds
            else:
                newScaffold = self.Scaffold(gene.location[1], gene.location[0], [gene])
                scaffolds = reverseScaffolds

            running = True

            while running:

                running = False

                for scaffold in scaffolds:

                    if abs(newScaffold.stop - scaffold.start) < scaffoldingDistance:
                        newScaffold.stop = scaffold.stop
                        newScaffold.genes += scaffold.genes
                        scaffolds.remove(scaffold)
                        running = True
                        break
                    elif abs(newScaffold.start - scaffold.stop) < scaffoldingDistance:
                        newScaffold.start = scaffold.start
                        newScaffold.genes += scaffold.genes
                        scaffolds.remove(scaffold)
                        running = True
                        break

            scaffolds.append(newScaffold)

        map(lambda x: x.genes.sort(key = lambda y: (y.location[0] + y.location[1])/2), forwardScaffolds)
        map(lambda x: x.genes.sort(key = lambda y: (y.location[0] + y.location[1])/2), reverseScaffolds)

        return forwardScaffolds, reverseScaffolds

    def overlap(self, intervalOne, intervalTwo):
        self._logger.info("Method call: overlap")
        """
        intervalOne: A 2-tuple of integers.
        intervalTwo: A 2-tuple of integers.

        return:      Amount of overlap between the intervals or -1 for no overlap.
        """

        if intervalOne.start < intervalTwo.start <= intervalOne.stop < intervalTwo.stop:
            return intervalOne.stop - intervalTwo.start
        elif intervalTwo.start < intervalOne.start <= intervalTwo.stop < intervalOne.stop:
            return intervalTwo.stop - intervalOne.start
        elif intervalOne.start <= intervalTwo.start and intervalTwo.stop <= intervalOne.stop:
            return intervalTwo.stop - intervalTwo.start
        elif intervalTwo.start <= intervalOne.start and intervalOne.stop <= intervalTwo.stop:
            return intervalOne.stop - intervalOne.start
        else:
            return -1
    
    def filterScaffolds(self, originalForwardScaffolds, originalReverseScaffolds):
        self._logger.info("Method call: filterScaffolds")
        """
        originalForwardScaffolds: List of Scaffold objects for the forward genes.
        originalReverseScaffolds: List of Scaffold objects for the reverse genes.

        return:     A 2-tuple, first object is a list of Scaffold objects for the forward genes,
                    and the second a list of scaffold objects for the reverse genes.

        For each forward scaffold this function iterates over each reverse scaffold.  If any two scaffolds conflict with each other
        then any intergenic genes on the conflicting edges are removed, and if this fails to resolve the conflict then both scaffolds are
        kept.  The result of this product is what is returned.
        """

        forwardScaffolds, reverseScaffolds = copy.deepcopy(originalForwardScaffolds), copy.deepcopy(originalReverseScaffolds)
        newForwardScaffolds, newReverseScaffolds = copy.copy(forwardScaffolds), copy.copy(reverseScaffolds)

        for forwardScaffold in forwardScaffolds:

            for reverseScaffold in copy.copy(newReverseScaffolds):

                forwardScaffoldRemoved = False

                while self.overlap(forwardScaffold, reverseScaffold) > 3:

                    forwardHasGenemark = functools.reduce(lambda x, y: x or not y.intergenic, forwardScaffold.genes, False)
                    reverseHasGenemark = functools.reduce(lambda x, y: x or not y.intergenic, reverseScaffold.genes, False)

                    forwardCenter = (forwardScaffold.start + forwardScaffold.stop)/2
                    reverseCenter = (reverseScaffold.start + reverseScaffold.stop)/2

                    if forwardCenter < reverseCenter:

                        if forwardHasGenemark and not reverseHasGenemark:
                            removableItem = [reverseScaffold.genes[0]]
                        elif not forwardHasGenemark and reverseHasGenemark:
                            removableItem = [forwardScaffold.genes[-1]]
                        else:
                            removableItem = [forwardScaffold.genes[-1], reverseScaffold.genes[0]]
                    else:

                        if forwardHasGenemark and not reverseHasGenemark:
                            removableItem = [reverseScaffold.genes[-1]]
                        elif not forwardHasGenemark and reverseHasGenemark:
                            removableItem = [forwardScaffold.genes[0]]
                        else:
                            removableItem = [reverseScaffold.genes[-1], forwardScaffold.genes[0]]

                    removable = list(filter(lambda x: x.intergenic, removableItem))

                    if removable:


                        toRemove = min(removable, key = lambda x: abs(x.location[1] - x.location[0]))

                        if toRemove.location[0] < toRemove.location[1]:

                            forwardScaffold.genes.remove(toRemove)

                            if not forwardScaffold.genes:
                                newForwardScaffolds.remove(forwardScaffold)
                                forwardScaffoldRemoved = True
                                break
                            elif forwardCenter < reverseCenter:
                                forwardScaffold.stop = forwardScaffold.genes[-1].location[1]
                            else:
                                forwardScaffold.start = forwardScaffold.genes[0].location[0]
                        else:

                            reverseScaffold.genes.remove(toRemove)

                            if not reverseScaffold.genes:
                                newReverseScaffolds.remove(reverseScaffold)
                                break
                            elif forwardCenter < reverseCenter:
                                reverseScaffold.start = reverseScaffold.genes[0].location[1]
                            else:
                                reverseScaffold.stop = reverseScaffold.genes[-1].location[0]

                    elif forwardHasGenemark and reverseHasGenemark:
                        break
                    elif forwardScaffold.stop - forwardScaffold.start < reverseScaffold.stop - reverseScaffold.start:
                        newForwardScaffolds.remove(forwardScaffold)
                        forwardScaffoldRemoved = True
                        break
                    else:
                        newReverseScaffolds.remove(reverseScaffold)
                        break

                if forwardScaffoldRemoved:
                    break

        return newForwardScaffolds, newReverseScaffolds

    def refineScaffolds(self, genes, scaffoldingDistance, pipeline):
        self._logger.info("Method call: refineScaffolds")
        """
        genes:               A dictionary that maps query names to Iteration objects.
        scaffoldingDistance: Maximum distance between neighboring genes in a scaffold.

        return:              A dictionary that maps query names to Iteration objects.

        This function will organize genes into scaffolds, which are contiguous regions of genes.  Any
        scaffolds which conflict will have intergenic genes removed in order to try and resolve the
        conflict, failing this both Scaffolds are kept.  The returned dictionary will contain the
        remaining genes after this process.
        """

        if genes is None:
            print("Expected dictionary 'genes'. Found 'None' instead at refineScaffolds")
            raise Exceptions.ScaffoldsError

        forwardScaffolds, reverseScaffolds = self.extractScaffolds(genes.values(), int(scaffoldingDistance))
        if pipeline.stopped():
            return

        forwardFiltered, reverseFiltered = self.filterScaffolds(forwardScaffolds, reverseScaffolds)
        if pipeline.stopped():
            return

        remainingGenes = functools.reduce(lambda x, y: x + y, map(lambda x: x.genes, forwardFiltered), [])
        if pipeline.stopped():
            return

        remainingGenes.extend(functools.reduce(lambda x, y: x + y, map(lambda x: x.genes, reverseFiltered), []))
        if pipeline.stopped():
            return

        return dict(map(lambda x: (x.query, x), remainingGenes))
