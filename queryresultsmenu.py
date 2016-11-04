import npyscreen


class QueryResultsMenu(npyscreen.MultiLineAction):
    """
    Class that can populate a sub-menu after Enter pressed on one of its list items
    """
    def __init__(self, *args, **keywords):
        super(QueryResultsMenu, self).__init__(*args, **keywords)

    def actionHighlighted(self, act_on_this, key_press):
        """
        Overrides this method from super class to call from parent's action dictionary. It's a pain because we want
        items in the MainForm to display in a predetermined order, but dictionary doesn't offer any ordering guarantee.
        So we have to dereference both the index and key value in this return action
        :param act_on_this: string of item action taken on
        :param key_press: key pressed to get action. Base class takes care of enter and space for sure
        :return: None, calls the parent's callback to finish editing and set selected value
        """
        # simply return the thing selected to parent's callback function
        self.parent.cb_handler(act_on_this, key_press);




