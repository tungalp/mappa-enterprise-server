class FallbackTriggeredException(Exception):
    def __init__(self, response):
        self.response = response