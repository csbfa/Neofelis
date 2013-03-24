import smtplib
import email.mime.text as email
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for class Event")

class Event:
    """
    Event Class for Observer Pattern
    """

    def __init__(self, email = None, smtpUser = None, smtpPassword = None, smtpServer = None):
        self._logger.info("Method call: __init__")
        self._observers = []
        self._notify = False
        self._email = email
        self._smtpUser = smtpUser
        self._smtpPassword = smtpPassword
        self._smtpServer = smtpServer

    def subscribe(self, observer):
        self._logger.info("Method call: subscribe")
        """

        """

        if not observer in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        self._logger.info("Method call: unsubscribe")
        """

        """

        try:
            self._observers.remove(observer)
        except ValueError:
            self._logger.warning("Warning: attempted to unsubscribe an observer that didn't exist")
            pass

    def fire(self, subject, modifier=None, message="progress"):
        self._logger.info("Method call: fire")
        """

        """

        for observer in self._observers:

            if modifier != observer:
                if message == "progress":
                    self.update(subject, observer)
                    return
                if message == "completed":
                    self.completed(subject, observer)
                    return
                if message == "failed":
                    self.failed(subject, observer)
                    return

    def update(self, subject, observer):
        self._logger.info("Method call: update")
        """
        Update subject thread status in threadstat
        """

        try:
            subject.lock.acquire()
        finally:
            observer.updateStatus(subject.name, subject.progress)
            subject.lock.release()

    def failed(self, subject, observer):
        self._logger.info("Method call: failed")
        """

        """

        try:
            subject.lock.acquire()
        finally:
            observer.incrementFailed()
            observer.removeStatus(subject.name)
            subject.lock.release()

    def completed(self, subject, observer):
        self._logger.info("Method call: completed")
        """

        """

        try:
            subject.lock.acquire()
        finally:
            if self._email is not None:
                self._message = email.MIMEText("Your genome has been annotated.")
                self._message["Subject"] = "Annotation complete"
                self._message["From"] = "Neofelis"
                self._message["To"] = self._email

                self._smtp = smtplib.SMTP(self._smtpServer, 587)
                self._smtp.ehlo()
                self._smtp.starttls()
                self._smtp.ehlo()
                self._smtp.login(self._smtpUser, self._smtpPassword)
                self._smtp.sendmail("Neofelis", self._email, self._message.as_string())
                self._smtp.close()

            observer.incrementCompleted()
            observer.removeStatus(subject.name)
            subject.lock.release()

    def acquire(self):
        self._logger.info("Method call: acquire")
        self._notify = False

    def notify(self):
        self._logger.info("Method call: notify")
        self._notify = True

    def wait(self):
        self._logger.info("Method call: wait")
        while not self._notify:
            continue

        return

# __Event__
