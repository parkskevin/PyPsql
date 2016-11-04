import psycopg2
from singleton import Singleton


@Singleton
class Connection:
    """
    A singleton instance, we only want 1 db connection running around. Check for instance with Connection.Instance()
    """
    def __init__(self):
        self.connection = None

    def connect(self, **kwargs):
        """
        Try to make a psycopg2 connection
        :param kwargs: expect all necessary args for the connection string to be here in keyword format
        :return:
        """
        try:
            self.connection = psycopg2.connect(**kwargs)
            self.connection.set_session(autocommit=True)
        except Exception as e:
            raise e

    def getconnection(self):
        """
        Return instance of connection for direct manipulation
        :return: connection
        """
        return self.connection

    def logout(self):
        """
        Closes the connection, doesn't destroy this instance though
        :return:
        """
        if self.connection:
            self.connection.close()
