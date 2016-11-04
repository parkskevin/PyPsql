#!/usr/bin/env python

import npyscreen
from mainform import MainForm
from loginform import LoginForm
from queryresultsform import QueryResultsForm
from queryform import QueryForm
from structuresubform import StructureSubForm
from editform import EditForm
from getinputform import GetInputForm

class Psqlapp(npyscreen.NPSAppManaged):
    """
    Using npyscreen's recommended approach for handling a more complex application
    """
    def onStart(self):
        """
        Does form registration
        :return:
        """
        self.addForm('MAIN', MainForm)
        self.addForm('LOGIN', LoginForm)
        self.addForm('QUERYRESULTS', QueryResultsForm)
        self.addForm('QUERYFORM', QueryForm)
        self.addForm('STRUCTURESUBMENU', StructureSubForm)
        self.addForm('EDITFORM', EditForm)
        self.addForm('GETINPUTFORM', GetInputForm)


if __name__ == '__main__':
    APP = Psqlapp()
    APP.run()
