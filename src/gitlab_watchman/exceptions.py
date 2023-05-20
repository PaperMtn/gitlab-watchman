class ElasticsearchMissingError(Exception):
    """ Exception raised when Elasticsearch is not enabled on the instance.
    """

    def __init__(self, scope):
        self.scope = scope
        self.message = f'Elasticsearch is not configured, unable to use the search API for the scope: {self.scope}'
        super().__init__(self.message)


class MissingEnvVarError(Exception):
    """ Exception raised when an environment variable is missing.
    """

    def __init__(self, env_var):
        self.env_var = env_var
        self.message = f'Missing Environment Variable: {self.env_var}'
        super().__init__(self.message)
