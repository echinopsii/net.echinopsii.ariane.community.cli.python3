__author__ = 'mffrench'


class DriverResponse(object):
    def __init__(self, rc=None, error_message=None, response_properties=None, response_content=None):
        self.rc = rc
        self.error_message = error_message
        self.response_properties = response_properties
        self.response_content = response_content

    def get(self):
        '''
        mimic pykka future get method
        :return:
        '''
        return self