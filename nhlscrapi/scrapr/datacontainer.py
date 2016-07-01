class DataContainer(object):
    """Container class for data sources that may belong to a game"""

    allowed_data = ['html', 'json']

    def __init__(self, **kwargs):
        # Initialize each data source, if provided, or set to None
        for source_type in self.allowed_data:
            if source_type in kwargs:
                setattr(self, source_type, kwargs[source_type])
            else:
                setattr(self, source_type, None)
