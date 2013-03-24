import threading, sys, os
import Library.Event as event
from Library.Exceptions import *
from Library.Utils import loadGenome
from Library import Artemis, Extend, Genemark, Intergenic, Promoters, Report, tRNA, Scaffolds, Signals, Terminators
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Processor")

class Processor(event.Event, threading.Thread):
    """

    """

    def __init__(self, query, params, lock):
        self._logger.info("Method call: Processor.__init__")

        event.Event.__init__(self)
        threading.Thread.__init__(self)

        self.progress = 0
        self._panic = threading.Event()
        self.lock = lock
        self._query = query
        self._queryDirectory, self._filename = os.path.split(self._query)
        self._name = os.path.splitext(self._filename)[0]

        self._blastLocation = params["blast"]
        self._database = params["database"]
        self._eValue = params["e-value"]
        self._genemarkLocation = params["genemark"]
        self._matrix = params["matrix"]
        self._minLength = params["min-length"]
        self._scaffoldingDistance = params["scaffolding-distance"]
        self._promoterScoreCutoff = params["promoter-score-cutoff"]
        self._transtermLocation = params["transterm"]
        self._tRNAscanLocation = params["trna-scan"]
        self._output = params["output"]

        self._genemark = Genemark.Genemark(self._output)
        self._extend = Extend.Extend(self._output)
        self._intergenic = Intergenic.Intergenic(self._output)
        self._scaffolds = Scaffolds.Scaffolds()
        self._promoters = Promoters.Promoters(self._output)
        self._terminators = Terminators.Terminators()
        self._signals = Signals.Signals()
        self._trna = tRNA.tRNA(self._output)
        self._artemis = Artemis.Artemis()
        self._report = Report.Report()

    def stop(self):
        self._logger.info("Method call: stop")
        """

        """

        self._panic.set()

    def stopped(self):
        self._logger.info("Method call: stopped")
        """

        """

        return self._panic.isSet()

    def run(self):
        self._logger.info("Method call: run")
        """

        """

        #try:

        self._genome = loadGenome(self._query)
        self._swapFileName = self._output + "/" + "query." + str(self._name) + ".fas"
        self._queryFile = open(self._swapFileName, "w")
        self._queryFile.write(">" + self._filename + "\n")

        for i in range(0, len(self._genome), 50):
            self._queryFile.write(self._genome[i:min(i + 50, len(self._genome))] + "\n")

        self._queryFile.close()

        self.progress += 1
        self.fire(self)

        if self.stopped():
                sys.exit()

        try:
            self._initialGenes = self._genemark.findGenes(self._swapFileName, self._filename, self._blastLocation,
                    self._database, self._eValue, self._genemarkLocation, self._matrix, self._output, self)
        except GenemarkError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        try:
            self._extendedGenes = self._extend.extendGenes(self._swapFileName, self._initialGenes, self._filename,
                    self._blastLocation, self._database, self._eValue, self._output, self)
        except ExtendError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        try:
            self._intergenicGenes = self._intergenic.findIntergenics(self._swapFileName, self._extendedGenes,
                    self._filename, self._minLength, self._blastLocation, self._database, self._eValue, self._output, self)
        except IntergenicError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        self._genes = {}
        if self._intergenicGenes is not None:
            self._genes = dict(list(self._extendedGenes.items()) + list(self._intergenicGenes.items()))
        else:
            self.stop()

        if self.stopped():
            sys.exit()

        try:
            self._scaffolded = self._scaffolds.refineScaffolds(self._genes, self._scaffoldingDistance, self)
        except ScaffoldsError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        try:
            self._initialPromoters = self._promoters.findPromoters(self._swapFileName, self._filename,
                self._promoterScoreCutoff, self._output, self)
        except PromotersError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        try:
            # the .crd file might be failing
            self._initialTerminators = self._terminators.findTerminators(self._swapFileName, self._filename,
                    self._genes.values(), self._transtermLocation, self)
        except TerminatorsError:
            self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
            self.fire(self, message="failed")
            self.stop()
        finally:
            self.progress += 1
            self.fire(self)
            if self.stopped():
                sys.exit()

        if self._initialTerminators is not None and self._scaffolded.values() is not None:

            try:
                self._filteredSignals = self._signals.filterSignals(self._scaffolded.values(), self._initialTerminators + self._initialPromoters, self)
            except SignalsError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                self.stop()
            finally:
                self.progress += 1
                self.fire(self)
                if self.stopped():
                    sys.exit()

            try:
                self._filteredPromoters = list(filter(lambda x: isinstance(x, self._promoters.Promoter), self._filteredSignals))
                self._filteredTerminators = list(filter(lambda x: isinstance(x, self._terminators.Terminator), self._filteredSignals))
            except PromotersError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                return
            except TerminatorsError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                self.stop()
            finally:
                self.progress += 1
                self.fire(self)
                if self.stopped():
                    sys.exit()

            try:
                self._transferRNAs = self._trna.findtRNAs(self._tRNAscanLocation, self._swapFileName, self._name, self)
            except RNAError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                self.stop()
            finally:
                self.progress += 1
                self.fire(self)
                os.remove(self._swapFileName)
                if self.stopped():
                    sys.exit()

            try:
                self._artemis.writeArtemisFile(self._output + "/" + self._name + ".art", self._genome, self,
                        self._scaffolded.values(), self._filteredPromoters, self._filteredTerminators, self._transferRNAs)
            except ArtemisError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                self.stop()
            finally:
                self.progress += 1
                self.fire(self)
                if self.stopped():
                    sys.exit()

            try:
                self._report.report(self._filename, self._scaffolded, self._output, self)
            except ReportError:
                self._logger.exception("pipeline " + self._name + " failed. Terminating thread.")
                self.fire(self, message="failed")
                self.stop()
            finally:
                self.progress += 1
                self.fire(self)
                if self.stopped():
                    sys.exit()

        else:

            print("Processing error in thread: ", self._name, "\nNo result can be returned")
            self.fire(self, message="failed")
            sys.exit()

        #except PipelineException:
        #    self.fire(self, message="failed")
        #    return

        self.fire(self, message="completed")

# __Processor__

