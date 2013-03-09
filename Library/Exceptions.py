"""

"""


class GraphicsException(Exception):
    """
    Catches Headless environment exception
    """

    def __init__(self, msg):
        self._message = "Graphics Error: Environment is headless\n" + msg
        Exception.__init__(self, msg)

    def toString(self):
        return self._message


class PipelineException(Exception):
    """
    Unhandled exception in processing thread
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Unhandled exception raised: Processor terminated enexpectedly\n" + msg)

    def toString(self):
        return self._message


class GenemarkError(Exception):
    """
    General exception raised by Genemark
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Genemark Error: Genemark processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class ExtendError(Exception):
    """
    General exception raised by Extend
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Extend Error: Extend processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class IntergenicError(Exception):
    """
    General exception raised by Intergenic
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Intergenic Error: Intergenic processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class ScaffoldsError(Exception):
    """
    General exception raised by Scaffolds
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Scaffolds Error: Scaffolds processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class PromotersError(Exception):
    """
    General exception raised by Promoters
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Promoters Error: Promoters processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class TerminatorsError(Exception):
    """
    General exception raised by Terminators
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Terminators Error: Terminators processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class SignalsError(Exception):
    """
    General exception raised by Signals
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Signals Error: Signals processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class RNAError(Exception):
    """
    General exception raised by RNA
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "tRNAscan-SE Error: tRNAscan-SE processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class ArtemisError(Exception):
    """
    General exception raised by Artemis
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Artemis Error: Artemis processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class ReportError(Exception):
    """
    General exception raised by Report
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Report Error: Report processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class tRNAError(Exception):
    """
    General exception raised by tRNAscan-SE
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "tRNAscan-SE Error: tRNAscan-SE processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class pReadError(Exception):
    """
    General exception raised by pRead
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "pRead Error: subprocessing processing terminated unexpectedly\n" + msg)

    def toString(self):
        return self._message


class LoggingError(Exception):
    """
    General exception raised by Log
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Loging Error: " + msg)

    def toString(self):
        return self._message