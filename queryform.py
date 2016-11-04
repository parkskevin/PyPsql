import npyscreen
from connection import Connection


class QueryForm(npyscreen.ActionPopup):
    """
    A form that gathers input from user for to use as a string query.
    """

    def activate(self):
        npyscreen.blank_terminal()
        self.color = 'STANDOUT'
        self.edit()

    def create(self):
        """
        Does setup of widgets required for a query
        :return:
        """
        self.name = "Query Form"
        self.queryString = self.add(npyscreen.TitleText, name="Enter Query:")

    def on_ok(self):
        """
        on_ok handler gets query string from user
        :return:
        """
        if self.validate_string():
            self.parentApp.getForm('QUERYRESULTS').SQL = self.queryString.value
            self.parentApp.getForm('QUERYRESULTS').value = ()
            self.parentApp.getForm('QUERYRESULTS').mode = 'QUERY'
            self.parentApp.switchForm('QUERYRESULTS')
        else:
            self.parentApp.switchForm('MAIN')

    def validate_string(self):
        """
        validate_string removes "\n" and checks for ";"
        :return: false if input is empty, true with adjusted string otherwise
        """
        if self.queryString.value is "" or self.queryString.value is None:
            return False

        self.queryString.value = self.queryString.value.lstrip('\n')
        if not self.queryString.value.endswith(";"):
            self.queryString.value = self.queryString.value + ";"
        return True

    def on_cancel(self):
        """
        on_cancel handler simply exits window
        :return:
        """
        self.parentApp.switchForm("MAIN")
