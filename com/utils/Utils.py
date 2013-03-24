"""

"""

import os, sys, re, datetime, subprocess, functools, multiprocessing, fileinput
import xml.sax as xmls
from Library import Exceptions
import com.log.Log as Log

self._logger = Log.new()
self._logger.info("Logging started in Utils")

#Start and stop codons
startCodons = ("ATG", "GTG", "TTG")
stopCodons = ("TGA", "TAA", "TAG")

#Dictionary containing the complements of Nucleotides
complementDictionary = {"A":"T", "T":"A", "G":"C", "C":"G"}

#Dictionary containing the mappings from codons to proteins
translationDictionary = {"TTT":"F","TTC":"F",
                         "TTA":"L", "TTG":"L", "CTT":"L", "CTC":"L", "CTA":"L", "CTG":"L",
                         "TCT":"S", "TCC":"S", "TCA":"S", "TCG":"S", "AGT":"S", "AGC":"S",
                         "TAT":"Y", "TAC":"Y",
                         "TGA":"*", "TAA":"*", "TAG":"*",
                         "TGT":"C", "TGC":"C",
                         "TGG":"W",
                         "CCA":"P", "CCC":"P", "CCG":"P", "CCT":"P",
                         "CAC":"H", "CAT":"H",
                         "CAA":"Q", "CAG":"Q",
                         "CGA":"R", "CGC":"R", "CGG":"R", "CGT":"R", "AGA":"R", "AGG":"R",
                         "ATT":"I", "ATC":"I", "ATA":"I",
                         "ATG":"M",
                         "ACA":"T", "ACC":"T", "ACG":"T", "ACT":"T",
                         "AAT":"N", "AAC":"N",
                         "AAA":"K", "AAG":"K",
                         "GTA":"V", "GTT":"V", "GTG":"V", "GTC":"V",
                         "GCA":"A", "GCT":"A", "GCG":"A", "GCC":"A",
                         "GAT":"D", "GAC":"D",
                         "GAA":"E", "GAG":"E",
                         "GGA":"G", "GGT":"G", "GGG":"G", "GGC":"G"}

def ShortOptions(self, k):
    self._logger.info("Method call: ShortOptions")
    """

    """

    if k == "h":
        return "help"
    elif k == "m":
        return "man"
    elif k == "r":
        return "server"
    elif k == "i":
        return "interface"
    elif k == "x":
        return "matrix"
    elif k == "d":
        return "database"
    elif k == "g":
        return "genemark"
    elif k == "b":
        return "blast"
    elif k == "e":
        return "e-value"
    elif k == "l":
        return "min-length"
    elif k == "t":
        return "transterm"
    elif k == "p":
        return "promoter-score-cutoff"
    elif k == "s":
        return "scaffolding-distance"
    elif k == "q":
        return "query"
    elif k == "a":
        return "trna-scan"
    elif k == "o":
        return "output"
    elif k == "u":
        return "qsub"
    else:
        return ""

# __ShortOptions__

def FileIO(self, input_file=None, input_dir=None, output_file=None, output_dir=None):
    self._logger.info("Method call: FileIO")
    """

    """

    self.path = ""
    self.drive = ""

    if not input_file and not input_dir and not output_file and not output_dir:
        print("No input provided" and sys.exit(2))

    self.home = os.getenv('HOME')

    if input_file:
        if os.path.isfile(input_file):
            return input_file
        elif os.path.isfile(self.home + input_file):
            return self.home + input_file
        else:
            print("Invalid input file: " + input_file + ". Verify file existence and location")
            sys.exit(2)

    if input_dir:
        if os.path.isdir(input_dir):
            return input_dir
        elif os.path.isdir(self.home + input_dir):
            return self.home + input_dir
        else:
            print("Invalid input directory: " + input_dir + ". Verify directory existence and location")
            sys.exit(2)

    if output_file or output_dir:

        if sys.platform == 'win32':
            if output_file: drive, path = os.path.splitdrive(output_file)
            if output_dir: drive, path = os.path.splitdrive(output_dir)
        else:
            self.drive = ""
            self.path = output_file if output_file else output_dir

        # test if this returns a filename if output_dir
        self.path, self.filename = os.path.split(self.path)

        if os.path.isdir(self.drive + self.path) and self.path != "./":
            if output_file:
                if os.path.isfile(self.drive + self.path + self.filename):
                    while 1:
                        self.resposne = input("% exist. Overwrite? (y/n)" % self.filename)
                        if re.match(r'y.*', self.response, re.IGNORECASE):
                            os.remove(self.drive + self.path + self.filename)
                            break
                        elif re.match(r'n.*', self.response, re.IGNORECASE):
                            break
                        else:
                            continue
                return output_file

            if output_dir:
                return output_dir

        else:

            self.response = input("Invalid output paramater: " + self.drive + self.path + self.filename + ".\nUse default output? (y/n)")
            if re.match(r'n.*', self.response, re.IGNORECASE):
                print("Exiting program...Please verify " + self.drive + self.path + self.filename)
                sys.exit(2)

            self.formatted = self.home + "Neofelis"
            if not os.path.isdir(self.formatted):
                os.makedirs(self.formatted)

            self.calendar = datetime.datetime.now()
            self.formatted += (self.calendar.day + self.calendar.month + self.calendar.year)
            if not os.path.isdir(self.formatted):
                os.makedirs(self.formatted)

            self.formatted += (self.calendar.hour + self.calendar.minute + self.calendar.second)
            if not os.path.isdir(self.formatted):
                os.makedirs(self.formatted)

            if input_file:
                self.formatted += self.filename

            return self.formatted

# __FileIO__

def Prompt(params):
    self._logger.info("Method call: Prompt")
    """

    """
    _params = params
    # don't prompt for interface, server, port, parse

    _params = {
        "help"          : False,
        "man"           : False,
        "server"        : None,
        "port"          : None,
        "interface"     : "gui",
        "matrix"        : None,
        "database"      : None,
        "genemark"       : None,
        "blast"         : None,
        "e-value"       : None,
        "min-length"    : None,
        "transterm"     : None,
        "promoter-score-cutoff" : None,
        "scaffolding-distance"  : None,
        "input_file"    : None,
        "input_dir"     : None,
        "output"        : None,
        "trna-scan"     : None,
        "email"         : None,
        "smtp_server"   : None,
        "smtp_user"     : None,
        "smtp_password" : None,
        "prompt"        : None,
        "parse"         : None,
        "save"          : None,
    }

    val = input("Help? ")
    if re.match(r'^y(es)?$', val, re.IGNORECASE):
        _params["help"] = True
        return _params
    else:
        _params["help"] = False

    val = input("Manual? ")
    if re.match(r'^y(es)?$', val, re.IGNORECASE):
        _params["man"] = True
        return _params
    else:
        _params["man"] = False

    print("\nAt each prompt, use the keyboard to supply the input values on the prompt line. Press enter to submit.\nLeave the input line empty if no input is to be provided\n\n")

    val = input("Enter Server name ( IP or DNS ): ")
    if val != "":
        _params["server"] = val

    val = input("If server was specified, enter port number: ")
    if val != "":
        _params["port"] = val

    val = input("Enter 'GUI' or 'console' for interface type: ")
    if val != "":
        _params["interface"] = val

    val = input("Enter full NCBI Database path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["database"] = val

    val = input("Enter full Genemark path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["genemark"] = val

    val = input("Enter full BLAST+ path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["blast"] = val

    val = input("Enter the full Transterm path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["transterm"] = val

    val = input("Enter the full tRNAscan path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["trna-scan"] = val

    val = input("Enter the full input file path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["input_file"] = val

    val = input("Enter the full input input directory path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["input_dir"] = val

    val = input("Enter the full output directory path ( location ): ")
    if val != "":
        val = val.rstrip('/')
        val = val.rstrip('\\')
        _params["output"] = val

    val = input("Enter the Matrix to run genemark with: ")
    if val != "":
        _params["matrix"] = val

    val = input("Enter the E-Value to use: ")
    if val != "":
        _params["e-value"] = float(val)

    val = input("Enter the minimum length value: ")
    if val != "":
        _params["min-length"] = float(val)

    val = input("Enter the promoter-score-cutoff value: ")
    if val != "":
        _params["promoter-score-cutoff"] = float(val)

    val = input("Enter the scaffolding-distance value: ")
    if val != "":
        _params["scaffolding-distance"] = float(val)

    val = input("Enter the email address to use for automatic notification: ")
    if val != "":
        _params["email"] = val

    val = input("If email was provided, enter the smtp server: ")
    if val != "":
        _params["smtp_server"] = val

    val = input("If email was provided, enter the smtp user: ")
    if val != "":
        _params["smtp_user"] = val

    val = input("If email was provided, enter the smtp password: ")
    if val != "":
     _params["smtp_password"] = val

    #val = input("If desired, provide the directroy to create a save file ( full path ) for the input paramters: ")
    #if val != "":
        #_params["save"] = val

    return _params

# __Prompt__

def Parse(self, params):
    self._logger.info("Method call: Parse")
    """

    """
    self._params = params

# __Parse__

def Save(self, params):
    self._logger.info("Method call: Save")
    """

    """

    pass

# __Save__

def loadGenome(fileName):
    self._logger.info("Method call: loadGenome")
    """
    Loads the genome from a fasta file containing a single genome.
    """

    input = open(fileName, "r")
    result = ""

    for line in input:
        line.rstrip()
        match = re.match("([ACGT]+)", line.upper())
        if match:
            result += match.group(1)

    input.close()
    return result

# __loadGenome__

def isGenome(fileName):
    self._logger.info("Method call: isGenome")
    """
    Returns true if the file represented by fileName is a fasta file containing one genome.
    """

    if os.path.isdir(fileName):
        return False

    if not re.match(r'.*.fasta', fileName):
        return False

    for line in fileinput.input([fileName]):
        line = line.rstrip()
        if fileinput.isfirstline():
            if not re.match(">.+", line):
                fileinput.close()
                return False
        else:
            if not re.match("[ACGT]+", line.upper()):
                fileinput.close()
                return False

    fileinput.close()
    return True

# __isGenome__

def translate(input):
    self._logger.info("Method call: translate")
    """
    Returns a Neucleotide sequence translated into Proteins.
    """
    result = ""
    for i in range(0, len(input)-2, 3):
        result += translationDictionary[input[i:i+3]]
    return result

# __translate__

def reverseComplement(input):
    self._logger.info("Method call: reverseComplement")
    """
    Returns the reverse complement of a Neucleotide sequence.
    """

    result = map(lambda x: complementDictionary[x], input)
    list = []
    for item in result: list.append(item)
    list.reverse()
    return "".join(list)

# __reverseComplement__

def getHeader(self, fileName):
    self._logger.info("Method call: getHeader")
    """

    """

    self.input = open(fileName, "r")

    for self.line in input:
        self.match = re.match(">(.+)", self.line.upper())
        if self.match:
            self.input.close()
            return self.match.group(1)
    self.input.close()
    return None

# __getHeader__

def getGeneLocations(self, genes):
    self._logger.info("Method call: getGeneLocations")
    """
    Takes a a map with GeneStructs as values and returns a two Dictionaries.
    These Dictionies will contain as tuples the left and right ends of genes
    such that calling genomes.[left:right] will return the gene.  the first
    dictionary is for genes on the forward strand and the second for the
    reverse
    """

    self.forward = {}
    self.reverse = {}
    for k, v in genes.items():
        if v.location[0] < v.location[1]:
            self.forward[k] = [v.location[0]-1, v.location[1]]
        else:
            self.reverse[k] = [v.location[1]-1, v.location[0]]
    return self.forward, self.reverse

# __getGeneLocations__

class Iteration:
    """
    A structure for holding information about a gene's blast result.
    """

    def __init__(self):
    self._logger.info("Method call: Iteration.__init__")
        self.query =           None
        self.location =        []
        self.numHits =         0
        self.bitScore =        0
        self.eValue =          float("inf")
        self.identity =        0
        self.alignmentLength = 0
        self.id =              "None"
        self.title =           "None"
        self.organism =        "None"
        self.note =            ""
        self.color =           "0 255 255"
        self.intergenic =      False

    def __str__(self):
    self._logger.info("Method call: Iteration.__str__")
        result = "<"
        result += "Query = " + str(self.query) + ", "
        result += "Location = " + str(self.location) + ", "
        result += "NumHits = " + str(self.numHits) + ", "
        result += "BitScore = " + str(self.bitScore) + ", "
        result += "EValue = " + str(self.eValue) + ", "
        result += "Identity = " + str(self.identity) + ", "
        result += "AlignmentLength = " + str(self.alignmentLength) + ", "
        result += "ID = " + str(self.id) + ", "
        result += "Title = " + str(self.title) + ", "
        result += "Organism = " + str(self.organism) + ", "
        result += "Intergenic = " + str(self.intergenic)
        result += ">"
        return result

# __Iteration__

class Hit:
    """
    A structure for holding information about a hit.
    """

    def __init__(self):
    self._logger.info("Method call: Hit.__init__")
        self.eValue = float("inf")
        self.bitScore = 0
        self.identity = 0
        self.alignmentLength = 0
        self.id = None
        self.title = None
        self.organism = None

    def __str__(self):
    self._logger.info("Method call: Hit.__str__")
        result = "<"
        result += "BitScore = " + str(self.bitScore) + ", "
        result += "EValue = " + str(self.eValue) + ", "
        result += "Identity = " + str(self.identity) + ", "
        result += "AlignmentLength = " + str(self.alignmentLength) + ", "
        result += "ID = " + str(self.id) + ", "
        result += "Title = " + str(self.title) + ", "
        result += "Organism = " + str(self.organism)
        result += ">"
        return result

# __Hit__

class Hsp:
    """
    A structure for holding information about a Hsp.
    """

    def __init__(self):
    self._logger.info("Method call: Hsp.__init__")
        self.eValue = float("inf")
        self.bitScore = 0
        self.identity = 0
        self.alignmentLength = 0

# __Hsp__

class xmlAttribute(object):
    """

    """

    tag = None
    text = ""
    uri = ""

# __xmlAttribute__

class BlastHandler(xmls.handler.ContentHandler):
    """
    A SAX handler for parsing Blast XML output.
    """

    def __init__(self):
    self._logger.info("Method call: BlastHandler.__init__")
        self.iterations = []
        self.hits = []
        self.hsps = []
        self.text = ""
        self.prev = ""
        self.working_line = 0
        super(BlastHandler, self).__init__()

    def setDocumentLocator(self,locator):
    self._logger.info("Method call: setDocumentLocator")
        """

        """

        self.locator = locator

    # __setDocumentLocator__

    def startElement(self, name, attributes):
    self._logger.info("Method call: startElement")
        """
        Records the tag of the current node and generates a new
        object to store the information in the iteration,
        hit, and hsp nodes.
        """

        if name == "Iteration":
            self.iterations.append(Iteration())
        elif name == "Hit":
            self.hits.append(Hit())
        elif name == "Hsp":
            self.hsps.append(Hsp())

    # __startElement__

    def endElement(self, name):
    self._logger.info("Method call: endElement")
        """
        Calculates the contents of a Hit structure once the end of a Hit node has been reached,
        and calculates the contents of a Iteration structure once the end of an Iteration node
        has been reached.
        """

        if name == "Iteration" and self.hits:
            bestHit = min(self.hits, key = lambda hit:hit.eValue)
            self.iterations[-1].eValue = bestHit.eValue
            self.iterations[-1].bitScore = bestHit.bitScore
            self.iterations[-1].identity = bestHit.identity
            self.iterations[-1].alignmentLength = bestHit.alignmentLength
            self.iterations[-1].id = bestHit.id
            self.iterations[-1].title = bestHit.title
            self.iterations[-1].organism = bestHit.organism
            self.iterations[-1].numHits = len(self.hits)
            self.hits = []
        elif name == "Hit":
            bestHsp = min(self.hsps, key = lambda hsp:hsp.eValue)
            self.hits[-1].eValue = bestHsp.eValue
            self.hits[-1].bitScore = bestHsp.bitScore
            self.hits[-1].identity = bestHsp.identity
            self.hits[-1].alignmentLength = bestHsp.alignmentLength
            self.hsps = []
        elif name == "Iteration_query-def":
            self.iterations[-1].query, location = self.text.split(":")
            self.iterations[-1].location = [int(l) for l in location.split("-")]
        elif name == "Hit_id":
            self.hits[-1].id = self.text
        elif name == "Hit_def":
            match = re.search(r"([^\[]+)\[([^\]]+)", self.text)
            if match:
                self.hits[-1].title, self.hits[-1].organism = match.group(1).strip(), match.group(2).strip()
            else:
                self.hits[-1].title, self.hits[-1].organism = self.text.strip(), ""
        elif name == "Hsp_bit-score":
            self.hsps[-1].bitScore = float(self.text)
        elif name == "Hsp_evalue":
            self.hsps[-1].eValue = float(self.text)
        elif name == "Hsp_identity":
            self.hsps[-1].identity = float(self.text)
        elif name == "Hsp_align-len":
            self.hsps[-1].alignmentLength = int(self.text)

    # __endElement__

    def characters(self, data):
    self._logger.info("Method call: characters")
        """
        Pulls the character information from the current node depending on the
        tag of the parent.
        """

        self.line = self.locator.getLineNumber()

        if self.working_line == self.line and self.text != "":
            self.text += data

        else:
            self.text = data
            self.working_line = self.line

    # __characters__

    def resolveEntity(self, publicId, systemId):
    self._logger.info("Method call: resolveEntity")
        """

        """

        return xmls.InputSource("dtds/" + os.path.split(systemId)[1])

    # __resolveEntity__

# __BlastHandler__

def parseBlast(self, fileName):
    self._logger.info("Method call: parseBlast")
    """
    A function for parsing XML blast output.
    """

    reader = xmls.make_parser()
    blastHandler = BlastHandler()
    reader.setContentHandler(blastHandler)
    reader.parse(fileName)

    try:
        itr = reader.getContentHandler().iterations
        return dict(map(lambda iteration: (iteration.query, iteration), itr))
    except Exception as e:
        self._logger.exception("Exception: " + str(e))
        raise ValueError

# __parseBlast__

def cachedBlast(fileName, blastLocation, database, eValue, query, pipeline, remote = False, force = False):
    self._logger.info("Method call: cachedBlast")
    """
    Performs a blast search using the blastp executable and database in blastLocation on
    the query with the eValue.  The result is an XML file saved to fileName.  If fileName
    already exists the search is skipped.  If remote is true then the search is done remotely.
    """

    if not os.stat(query).st_size > 0:
        print("Fatal Error: Query file ", query, " is empty. Please check Genemark for output")
        raise Exceptions.GenemarkError

    if not os.path.isfile(fileName) or os.stat(fileName)[6] == 0 or force:

        try:
            output = open(fileName, "w+")
            command = [blastLocation + "/bin/blastp", "-evalue", str(eValue), "-outfmt", "5", "-query", query]
        except FileNotFoundError as e:
            self._logger.exception("\nFile not found: " str(e))
            raise Exceptions.GenemarkError

        if remote:
            command += ["-remote", "-db", database]
        else:
            command += ["-num_threads", str(multiprocessing.cpu_count() + 1),  "-db", database]

        try:

            blastProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if blastProcess is None:
                print("Error: subprocess pipe could not be opened for BLAST+")
                raise Exceptions.GenemarkError

            err = str(blastProcess.stderr.read(), 'ascii')
            if err:
                print("BLAST+: " + err)
                raise Exceptions.GenemarkError

        except Exception:
            self._logger.exception("Exception in BLAST subprocess spawning")
            raise Exceptions.GenemarkError

        while blastProcess.poll() is None:

            if pipeline.stopped():
                blastProcess.kill()
                return

            data = str(blastProcess.stdout.read(), 'ascii')
            err = str(blastProcess.stderr.read(), 'ascii')
            if err: print("BLAST+: " + err)
            output.write(data)

        remaining = blastProcess.stdout.read()

        while remaining:
            output.write(remaining)
            remaining = blastProcess.stdout.read()

        output.close()

    try:
        return parseBlast(pipeline, fileName)
    except xmls.SAXParseException as e:
        self._logger.exception("Unable to run xmls.SAXParseException" + str(e))
        raise Exceptions.GenemarkError

# __cachedBlast__

def getGCContent(genome):
    self._logger.info("Method call: getGCContent")
    """
    A function for calculating the GC content of a genome.
    """

    return functools.reduce(lambda x, y: x + int(y in ("G", "C")), genome, 0) / float(len(genome)) * 100

# __getGCContent__

def isNaN(number):
    self._logger.info("Method call: isNaN")
    """
    Returns true if number actually is a number.
    """

    return number != number

# __isNaN__

def which(program):
    self._logger.info("Method call: which")
    """

    """

    import os

    def is_exe(fpath):
    self._logger.info("Method call: is_exe")
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# __which__
