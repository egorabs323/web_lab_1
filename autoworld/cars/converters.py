class VINConverter:
    regex = '[A-HJ-NPR-Z0-9]{17}'
    def to_python(self, value):
        return value.upper()
    def to_url(self, value):
        return value.upper()