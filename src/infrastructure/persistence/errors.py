class InfrastructureError(Exception):
    pass


class DataMapperError(InfrastructureError):
    pass


class ReaderError(InfrastructureError):
    pass
