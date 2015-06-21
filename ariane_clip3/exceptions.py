__author__ = 'mffrench'


class ArianeError(Exception):
    def __repr__(self):
        return "Unspecified Ariane Client Error has occured"


class ArianeConfError(ArianeError):
    def __repr__(self):
        return self.args[0] + " is not defined !"


class ArianeNotImplemented(ArianeError):
    def __repr__(self):
        return self.args[0] + " is not implemented !"

class ArianeCallParametersError(ArianeError):
    def __repr__(self):
        return self.args[0] + " are not defined !"