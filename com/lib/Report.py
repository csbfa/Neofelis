"""

"""

import re
from xml.sax.handler import ContentHandler
from xml.sax.handler import EntityResolver
import xml.sax as xmls
from Library import Exceptions
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Report")

class Report():

    def __init__(self):
        self._logger.info("Method call: Report.__init__")
        self.xmlDictionary = {"&" : "&amp;", "\"" : "&quot;"}

    def handleXMLCharacters(self, input):
        self._logger.info("Method call: handleXMLCharacters")
        """
        Turns special characters into their xml form.
        """

        result = ""
        for q in input:
            result += self.xmlDictionary[q] if q in self.xmlDictionary else q
        return result

    class HTMLWriter(ContentHandler):
        """
        An xml parser that transforms an xml file into html.  The data is presented
        as iterations containing a list of hits, which then contain a list of hsps that
        show the alignment, evalue, bit score, and length of the hsp.
        """

        def __init__(self, output, instance):
            self._logger.info("Method call: HTMLWriter.__init__")
            self.output = output
            self.htmlDepth = 0
            self.querySequence = self.hitSequence = self.midline = self.tag = ""
            self.working_line = 0
            self.instance = instance
            super().__init__()

        def setDocumentLocator(self,locator):
            self._logger.info("Method call: setDocumentLocator")
            self.locator = locator

        def writeHTMLStartTag(self, tag):
            self._logger.info("Method call: writeHTMLStartTag")
            self.output.write("  " * self.htmlDepth + "<" + tag + ">\n")
            self.htmlDepth += 1

        def writeHTMLEndTag(self, tag):
            self._logger.info("Method call: writeHTMLEndTag")
            self.htmlDepth -= 1
            self.output.write("  "*self.htmlDepth + "</" + tag + ">\n")

        def writeHTMLParagraph(self, text):
            self._logger.info("Method call: writeHTMLParagraph")
            self.output.write("  "*self.htmlDepth + "<p>" + text + "</p>\n")

        def writeHTMLLine(self, text):
            self._logger.info("Method call: writeHTMLLine")
            self.output.write("  "*self.htmlDepth + text + "\n")

        def writeHTMLDefinitionItem(self, text):
            self._logger.info("Method call: writeHTMLDefinitionItem")
            self.output.write("  "*self.htmlDepth + "<dt>" + text + "</dt>\n")

        def startDocument(self):
            self._logger.info("Method call: startDocument")
            print ( "html start document")
            self.output = open(self.output, "w")
            self.writeHTMLStartTag("html")
            self.writeHTMLStartTag("body  style=\"font-family:monospace;white-space:nowrap;\"")

        def endDocument(self):
            self._logger.info("Method call: endDocument")
            print ( "html end document")
            self.writeHTMLEndTag("html")
            self.writeHTMLEndTag("body")
            self.output.write("\n")
            self.output.close()

        def startElement(self, tag, attributes):
            self._logger.info("Method call: startElement")

            print ( "html start element: ", tag)
            self.text, self.tag = "", tag
            if tag == "BlastOutput_iterations":
                self.writeHTMLStartTag("dl")
                self.writeHTMLDefinitionItem("Iterations:")
                self.writeHTMLStartTag("dd")
            elif tag == "Iteration_hits":
                self.writeHTMLStartTag("dl")
                self.writeHTMLDefinitionItem("Hits:")
                self.writeHTMLStartTag("dd")
            elif tag == "Hit_hsps":
                self.writeHTMLStartTag("dl")
                self.writeHTMLDefinitionItem("Hsps:")
                self.writeHTMLStartTag("dd")

        def endElement(self, tag):
            self._logger.info("Method call: endElement")

            print ( "html end element: ", tag)
            if tag == "BlastOutput_iterations":
                self.writeHTMLEndTag("dd")
                self.writeHTMLEndTag("dl")
            elif tag == "Iteration_hits":
                self.writeHTMLEndTag("dd")
                self.writeHTMLEndTag("dl")
            elif tag == "Hit_hsps":
                self.writeHTMLEndTag("dd")
                self.writeHTMLEndTag("dl")
            elif tag == "Iteration_query-def":
                self.writeHTMLStartTag("dl")
                self.writeHTMLDefinitionItem("Iteration: " + self.text)
                self.writeHTMLStartTag("dd")
            elif tag == "Iteration":
                self.writeHTMLEndTag("dd")
                self.writeHTMLEndTag("dl")
            elif tag == "Hit_def":
                self.writeHTMLStartTag("dl")
                self.writeHTMLDefinitionItem("Hit: " + self.text)
                self.writeHTMLStartTag("dd")
            elif tag == "Hit":
                self.writeHTMLEndTag("dd")
                self.writeHTMLEndTag("dl")
            elif tag == "Hsp_qseq":
                self.querySequence = self.text
            elif tag == "Hsp_hseq":
                self.hitSequence = self.text
            elif tag == "Hsp_evalue":
                self.eValue = self.text
            elif tag == "Hsp_midline":
                self.midline = self.text.replace(" ", "&nbsp;")
            elif tag == "Hsp_align-len":
                self.alignmentLength = self.text
            elif tag == "Hsp_identity":
                self.identity = self.text
            elif tag == "Hsp":
                self.writeHTMLStartTag("p")
                self.writeHTMLLine("E Value = " + self.eValue + "<br/>")
                self.writeHTMLLine("Alignment Length = " + self.alignmentLength + "<br/>")
                self.writeHTMLLine("Identity = " + self.identity + "<br/>")
                self.writeHTMLLine(self.querySequence + "<br/>")
                self.writeHTMLLine(self.midline + "<br/>")
                self.writeHTMLLine(self.hitSequence + "<br/>")
                self.writeHTMLEndTag("p")

        def characters(self, data):
            self._logger.info("Method call: characters")

            self.line = self.locator.getLineNumber()

            print ("html character: ", data)

            if self.working_line == self.line and self.text != "":
                self.text += self.instance.handleXMLCharacters(str(data))

            else:
                self.text = self.instance.handleXMLCharacters(str(data))
                self.working_line = self.line

        def resolveEntity(self, publicId, systemId):
            self._logger.info("Method call: resolveEntity")

            print("html resolveEntity: ", publicId, ", ", systemId)

            if systemId:
                resolver = EntityResolver()
                return resolver.resolveEntity(self, systemId)

            elif publicId:
                resolver = EntityResolver()
                return resolver.resolveEntity(self, publicId)

    class BlastMerger(ContentHandler):
        """
        A SAX handler for Deleting Genes.

        xml contents are echoed to the output depending on the printing and holding flags.  If printing is True then
        text may be written depending on holding.  If holding is true then chunks of text is saved in a list, which may
        simply be flushed, otherwise the text is written to the output.

        This parser starts with a root parse and a list of xml files.  Once the ending Iteration tag has been reached a
        new parser will be spawned to append the iterations in the next xml file.  The parent will start with printing
        set to True but the children won't so the contents of the xml outside the iterations are only written once.

        When an Iteration element is encountered printing and holding is set to True, so text is buffered.  Once the query definition
        is reached the buffered text and the rest of the iteration element will be written to the file if the definition is in the list
        of genes, otherwise it will be dumped and the rest of the iteration ignored.  Also, so iterations have unique numbers the iteration
        numbers are replaced with an incrementing counter.  Also, whitespace is buffered until a new element is reached so that empty
        lines can be removed before being written to a file.
        """

        def __init__(self, sources, genes, output, instance, printing = False, parent = None, iteration = 1):
            self._logger.info("Method call: BlastMerger.__init__")
            self.sources = sources
            self.output = output
            self.genes = genes
            self.text = []
            self.iterationQueryDef = True
            self.iterationQueryDefString = ""
            self.holding = False
            self.parent = parent
            self.printing = printing
            self.whitespace = []
            self.iteration = iteration
            self.iterationNumberTag = False
            self.working_line = 0
            self.instance = instance
            super().__init__()

        def setDocumentLocator(self,locator):
            self._logger.info("Method call: setDocumentLocator")
            self.locator = locator

        def startDocument(self):
            self._logger.info("Method call: startDocument")
            """
            If output is a string then nothing has been written, so it needs to be made into a file object
            and a header needs to be written.
            """

            print ( "start document")

            if isinstance(self.output, str):
                self.output = open(self.output, "w")
                self.output.write("<?xml version=\"1.0\"?>\n")
                self.output.write("<!DOCTYPE BlastOutput PUBLIC \"-//NCBI//NCBI BlastOutput/EN\" \"NCBI_BlastOutput.dtd\">\n")

        def endDocument(self):
            self._logger.info("Method call: endDocument")
            print ( "end document")
            self.output.write("\n")
            self.output.close()

        def startElement(self, tag, attributes):
            self._logger.info("Method call: startElement")

            print("start tag: ", tag)

            if tag == "Iteration":
                self.printing = self.holding = True
            self.iterationNumberTag = tag == "Iteration_iter-num"
            self.iterationQueryDef = tag == "Iteration_query-def"
            self.iterationQueryDefString = ""

            if self.printing:
                if self.holding:
                    self.text += re.sub("\n\s*\n", "\n", "".join(self.whitespace)) + "<" + tag + ">"
                else:
                    self.output.write(re.sub("\n\s*\n", "\n", "".join(self.whitespace)) + "<" + tag + ">")
                self.whitespace = []

        def endElement(self, tag):
            self._logger.info("Method call: endElement")

            print("end tag: ", tag)

            if tag == "BlastOutput_iterations":
                if self.sources:
                    self.output.write("  ")
                    reader = xmls.make_parser()
                    innerMerger = self.instance.BlastMerger(self.sources[1:], self.genes, self.output, False, self, self.iteration)
                    reader.setContentHandler(innerMerger)
                    reader.setEntityResolver(innerMerger)
                    try:
                        reader.parse(self.sources[0])
                    except self.instance.BreakParsingException:
                        self._logger.warning("Unable to parse self.sources[0]")
                        if self.parent:
                            self._logger.exception("Parent not found when unable to parse self.sources[0]")
                            raise self.instance.BreakParsingException()
                        else:
                            pass
                else:
                    raise self.instance.BreakParsingException()

            if self.iterationQueryDef:
                self.iterationQueryDef = False
                if self.iterationQueryDefString[:self.iterationQueryDefString.rfind(":")] in self.genes:
                    self.printing = True
                    self.holding = False
                    self.output.write("".join(self.text))
                    self.text = []
                else:
                    self.printing = False
                    self.holding = False
                    self.text = []

            if self.printing:
                if self.holding:
                    self.text += re.sub("\n\s*\n", "\n", "".join(self.whitespace)) + "</" + tag + ">"
                else:
                    self.output.write(re.sub("\n\s*\n", "\n", "".join(self.whitespace)) + "</" + tag + ">")
                self.whitespace = []

            if tag == "Iteration":
                self.holding = False
                self.printing = True

        def characters(self, data):
            self._logger.info("Method call: characters")

            print("characters: ", data)

            self.line = self.locator.getLineNumber()

            if self.iterationQueryDef:
                self.iterationQueryDefString += str(data)
            if self.printing:
                if self.holding:
                    if self.iterationNumberTag:

                        if self.working_line == self.line and self.text != "":
                            self.text += str(self.iteration)

                        else:
                            self.text = str(self.iteration)
                            self.working_line = self.line

                        self.iteration += 1

                    else:

                        if self.working_line == self.line and self.text != "":
                            self.text += self.instance.handleXMLCharacters(str(data))

                        else:
                            self.text = self.instance.handleXMLCharacters(str(data))
                            self.working_line = self.line
                else:
                    self.output.write(self.instance.handleXMLCharacters(str(data)))

        def ignorableWhitespace(self, raw):
            self._logger.info("Method call: ignorableWhitespace")
            self.whitespace += raw.tostring()

        def resolveEntity(self, publicId, systemId):
            self._logger.info("Method call: resolveEntity")

            print("resolveEntity: ", publicId, ", ", systemId)

            if systemId:
                resolver = EntityResolver()
                return resolver.resolveEntity(self, systemId)

            elif publicId:
                resolver = EntityResolver()
                return resolver.resolveEntity(self, publicId)


    class BreakParsingException(Exception):
        """
        Exception for halting xml parsing.
        """
        pass

    def writeSpreadsheet(self, genes, output):
        self._logger.info("Method call: writeSpreadsheet")
        """
        genes:  A list of Iteration objects.
        output: File name to write iterations to.

        Writes a spreadsheet of genes into output.
        """

        i = 0
        output = open(output + ".xls", "w")
        genes = sorted(filter(lambda x: x.numHits != 0, genes), key = lambda x: min(x.location)) + sorted(filter(lambda x: x.numHits == 0, genes), key = lambda x: min(x.location))
        output.write("Id\tStart\tStop\tHits\tBest bit score\tBest evalue\tBest identity\tAlignment Length\tBest hit gi\tDefinition\tOrganism\n")

        try:
            for gene in genes:
                #print("gene: ", gene)
                i += 1
                output.write(str(i) + "\t")
                output.write("\t".join(map(str, gene.location)) + "\t")
                output.write(str(gene.numHits) + "\t")
                output.write(str(gene.bitScore) + "\t")
                output.write(str(gene.eValue) + "\t")
                output.write(str(gene.identity) + "\t")
                output.write(str(gene.alignmentLength) + "\t")
                if gene.id == "None":
                    output.write(gene.id + "\t")
                else:
                    output.write(re.search(r"gi\|(\d+)\|", gene.id).groups()[0] + "\t")
                output.write(gene.title + "\t")
                output.write(gene.organism + "\n")
        except Exception as e:
            self._logger.exception("Exception occurred in xls writing: " + str(e))
            output.close()
            raise Exceptions.ReportError()

        output.close()

    def report(self, name, genes, output, pipeline):
        self._logger.info("Method call: report")
        """
        name:   Name of the genome.
        genes:  A dictionary that maps query names to Iteration objects.
        output: Output file name without an extension.

        Writes a report of the contents of the blast searchs for the queries in
        genes into "name.html", "name.blastp.xml", and "name.xls".
        """

        #reader = xmls.make_parser()
        #blastMerger = BlastMerger(["extendedBlasts/" + name + ".blastp.xml", "intergenicBlasts/" + name + ".blastp.xml"],
        #                           genes.keys(), output + "/" + name + ".blastp.xml", self, True)
        #if pipeline.stopped():
        #    return

        #reader.setEntityResolver(blastMerger)
        #reader.setContentHandler(blastMerger)
        #reader.parse("initialBlasts/" + name + ".blastp.xml")

        #if pipeline.stopped():
            #return

        #htmlWriter = HTMLWriter(output + "/" + name + ".blastp.html", self)
        #if pipeline.stopped():
        #    return

        #reader.setEntityResolver(htmlWriter)
        #reader.setContentHandler(htmlWriter)
        #reader.parse(output + "/" + name + ".blastp.xml")

        #if pipeline.stopped():
        #    return

        self.writeSpreadsheet(genes.values(), output + "/" + name )
        return
