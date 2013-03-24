"""
This module contains functions for writing artemis files.
"""

import os
import com.log.Log as Log

self._logger = Log.new()
self._logger.info("Logging started for Artemis")

class Artemis():

    def writePromoters(self, output, promoters):
        self._logger.info("Method call: writePromoters")
        """
        output: File object to write to.
        promoters: List of Promoter objects.
    
        Writes promoters to the file.
        """

        for promoter in promoters:
            if promoter.signal10Location[0] < promoter.signal10Location[1]:
                output.write("     -10_signal             " + "..".join(map(str, promoter.signal10Location)) + "\n")
            else:
                output.write("     -10_signal             complement(" + "..".join(map(str, promoter.signal10Location)) + ")\n")
            output.write("                            /note=Promoter Position:" + str(promoter.position) + "\tScore:" + str(promoter.score) + "\n")
            output.write("                            /colour=255 0 255\n")
            if promoter.signal35Location[0] < promoter.signal35Location[1]:
                output.write("     -35_signal             " + "..".join(map(str, promoter.signal35Location)) + "\n")
            else:
                output.write("     -35_signal             complement(" + "..".join(map(str, promoter.signal35Location)) + ")\n")
            output.write("                            /note=Promoter Position:" + str(promoter.position) + "\tScore:" + str(promoter.score) + "\n")
            output.write("                            /colour=255 0 255\n")

    def writeTerminators(self, output, terminators):
        self._logger.info("Method call: writeTerminators")
        """
        output:      File object to write to.
        terminators: List of Terminator objects.

        Writes terminators to the file.
        """

        for terminator in terminators:
            if terminator.location[0] < terminator.location[1]:
                output.write("     terminator             " + "..".join(map(str, terminator.location)) + "\n")
            else:
                output.write("     terminator             complement(" + "..".join(map(str, terminator.location)) + ")\n")
            output.write("                            /note=\"confidence:" + str(terminator.confidence) + "\thp_score:" + str(terminator.hpScore) + "\ttail_score:" + str(terminator.tailScore) + "\"\n")

    def writeTransferRNAs(self, output, transferRNAs):
        self._logger.info("Method call: writeTransferRNAs")
        """
        output:       File object to write to.
        transferRNAs: List of TransferRNA objects.

        Writes transfer RNAs to the file.
        """

        for transferRNA in transferRNAs:
            if transferRNA.location[0] < transferRNA.location[1]:
                output.write("     gene                   " + "..".join(map(str, transferRNA.location)) + "\n")
            else:
                output.write("     gene                   complement(" + "..".join(map(str, transferRNA.location)) + ")\n")
            output.write("                            /note=\"type:" + str(transferRNA.type) + "\tanti codon:" + str(transferRNA.antiCodon) + "\tcove_score:" + str(transferRNA.coveScore) + "\"\n")

    def writeGenes(self, output, genes):
        self._logger.info("Method call: writeGenes")
        """
        output: File object to write to.
        genes:  List of Iteration objects.

        Writes genes to the file.
        """

        for gene in genes:
            if gene.location[0] < gene.location[1]:
                output.write("     CDS                   " + str(gene.location[0]) + ".." + str(gene.location[1]) + "\n")
            else:
                output.write("     CDS                   complement(" + str(gene.location[0]) + ".." + str(gene.location[1]) + ")\n")
            output.write("                            /gene=\"" + gene.title + "\"\n")
            output.write("                            /note=\"" + gene.note + "\"\n")
            output.write("                            /colour=" + gene.color + "\n")

    def writeGenome(self, output, genome):
        self._logger.info("Method call: writeGenome")
        """
        output: File object to write to.
        genome: Genome as a string.

        Writes genome to the file.
        """

        output.write("\nORIGIN\n\n")
        for i in range(0, len(genome), 50):
            output.write(genome[i:min(i+50, len(genome))] + "\n")

    def writeArtemisFile(self, fileName, genome, pipeline, genes=[], promoters=[], terminators=[], transferRNAs=[]):
        self._logger.info("Method call: writeArtemisFile")
        """
        fileName:     Name of the artemis file to write.
        genome:       Genome as a string.
        genes:        List of Iteration objects.
        promoters:    List of Promoter objects.
        terminators:  List of Terminator objects.
        transferRNAs: List of TransferRNA object.

        Writes an artemis file consisting of the genome, genes, promoters, terminators, and transfer RNAs.
        """

        output = open(fileName, "w")
        self.writePromoters(output, promoters)
        if pipeline.stopped():
            os.remove(fileName)
            return

        self.writeTerminators(output, terminators)
        if pipeline.stopped():
            os.remove(fileName)
            return

        self.writeTransferRNAs(output, transferRNAs)
        if pipeline.stopped():
            os.remove(fileName)
            return

        self.writeGenes(output, genes)
        if pipeline.stopped():
            os.remove(fileName)
            return

        self.writeGenome(output, genome)

        output.close()
