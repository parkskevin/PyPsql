import npyscreen
from structuresubmenu import StructureSubMenu

class StructureSubForm(npyscreen.ActionFormMinimal):
    OK_BUTTON_TEXT = 'BACK'
    DEFAULT_COLUMNS = 20
    DEFAULT_LINES = 10

    def activate(self):
        self.color = 'IMPORTANT'
        self.beforeEditing()
        self.edit()
        self.afterEditing()

    def beforeEditing(self):
        self.menu.values = self.makeactionkeys(self.actions[self.state])

    def create(self):
        """
        Does setup of widgets required for a selection
        :return:
        """
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit
        self.center_on_display()
        self.name = "Actions"
        self.state = 0
        self.actions = [
            [
                {'Browse': self.browse},
                {'Structure': self.structure},
                {'Insert': self.insert},
                {'Empty': self.empty},
                {'Drop': self.drop}
            ],
            [
                {'Edit': self.editopt},
                {'Delete': self.delete}
            ]
        ]
        self.menu = self.add(StructureSubMenu, w_id='menu', scroll_exit=True)


    def browse(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'BROWSE'
        self.parentApp.switchForm('QUERYRESULTS')

    def structure(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'STRUCTURE'
        self.parentApp.switchForm('QUERYRESULTS')

    def insert(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'INSERT'
        self.parentApp.switchForm('QUERYRESULTS')

    def empty(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'EMPTY'
        self.parentApp.switchForm('QUERYRESULTS')

    def drop(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'DROP'
        self.parentApp.switchForm('QUERYRESULTS')

    def editopt(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'EDIT'
        self.parentApp.switchForm('QUERYRESULTS')

    def delete(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'DELETE'
        self.parentApp.switchForm('QUERYRESULTS')

    def on_ok(self):
        """
        :return:
        """
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'BACK'
        self.parentApp.switchFormPrevious()

    def exit(self):
        self.parentApp.getForm('QUERYRESULTS').submenucmd = 'BACK'
        self.parentApp.switchFormPrevious()

    def afterEditing(self):
        self.menu.cursor_line = 0

    def makeactionkeys(self, actions):
        """
        Flattens the dictionary of actions in order desired (top to bottom in declare) and puts into keys list
        :return: list of keys within the list of dictionaries in order declared
        """
        actionkeys = []
        for i in actions:
            for key in i.iterkeys():
                actionkeys.append(key)
        return actionkeys