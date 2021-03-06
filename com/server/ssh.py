import os
import tempfile
from paramiko import *
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for ssh")

class Connection(object):
    """Connects and logs into the specified hostname.
    Arguments that are not given are guessed from the environment."""

    def __init__(self, host, username = None, private_key = None, password = None, port = 22 ):
        self._logger.info("Method call: Connection.__init__")
        self._sftp_live = False
        self._sftp = None
        if not username:
            username = os.environ['LOGNAME']

        # Log to a temporary file.
        templog = tempfile.mkstemp('.txt', 'ssh-')[1]
        util.log_to_file(templog)

        # Begin the SSH transport.
        self._transport = Transport((host, port))
        self._tranport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            self._transport.connect(username = username, password = password)
        else:
            # Use Private Key.
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    private_key = '~/.ssh/id_dsa'
                else:
                    raise TypeError("You have not specified a password or key.")

            private_key_file = os.path.expanduser(private_key)
            rsa_key = RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username = username, pkey = rsa_key)

    def _sftp_connect(self):
        self._logger.info("Method call: Connection._sftp_connect")
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def get(self, remotepath, localpath = None):
        self._logger.info("Method call: get")
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath = None):
        self._logger.info("Method call: put")
        """Copies a file between the local host and the remote host."""
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        self._sftp_connect()
        self._sftp.put(localpath, remotepath)

    def execute(self, command):
        self._logger.info("Method call: execute")
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        channel.exec_command(command)
        output = channel.makefile('rb', -1).readlines()
        if output:
            return output
        else:
            return channel.makefile_stderr('rb', -1).readlines()

    def close(self):
        self._logger.info("Method call: close")
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
            # Close the SSH Transport.
        if self._tranport_live:
            self._transport.close()
            self._tranport_live = False

    def __del__(self):
        self._logger.info("Method call: Connection.__del__")
        """Attempt to clean up if not explicitly closed."""
        self.close()

