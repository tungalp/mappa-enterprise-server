class CustomResponse:
    """HTTP yanıtını 'zeep' tarafından beklenen biçimde sarmalayan bir sınıf."""
    def __init__(self, response):
        self.status_code = response.status_code
        self.headers = response.headers
        self.content = response.content
        self.encoding = response.encoding if response.encoding else 'utf-8'
        