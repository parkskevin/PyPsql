import npyscreen


class StructureSubMenu(npyscreen.MultiLineAction):
    """
    Help from here: http://npyscreen.readthedocs.org/example-addressbk.html
    """
    def __init__(self, *args, **keywords):
        super(StructureSubMenu, self).__init__(*args, **keywords)

    def actionHighlighted(self, act_on_this, key_press):
        """
        Overrides this method from super class to call from parent's action dictionary. It's a pain because we want
        items in the MainForm to display in a predetermined order, but dictionary doesn't offer any ordering guarantee.
        So we have to dereference both the index and key value in this return action
        :param act_on_this: string of item action taken on
        :param key_press: key pressed to get action. Base class takes care of enter and space for sure
        :return: None, executes the parent's function
        """
        self.parent.actions[self.parent.state][self.values.index(act_on_this)][act_on_this]()




