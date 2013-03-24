import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for post")

class Post:
    
    def __init__(self):
        self._logger.info("Method call: Post.__init__")
        pass
    
    
