import npyscreen
from curses import ascii
from curses import KEY_DOWN
from connection import Connection

class EditForm(npyscreen.ActionPopup):

    def activate(self):
        self.beforeEditing()
        self.edit()

    def beforeEditing(self):
        self.updateresults()

    def updateresults(self):
        self.grid.col_titles = self.headers
        self.grid.columns = len(self.headers)
        self.grid.values = self.data
        if len(self.cursorstack) > 0:
            self.grid.edit_cell = self.cursorstack.pop()
        else:
            self.grid.edit_cell = [0, 0]
        self.grid.make_contained_widgets()
        self.grid.ensure_cursor_on_display_up()
        self.grid.ensure_cursor_on_display_down_right()

    def create(self):
        self.headers = ['Header1', 'Header2', 'Header3', 'Header4']
        self.data = ['Value1', 'Value2', 'Value3', 'Value4']
        self.grid = self.add(npyscreen.GridColTitles, name='Edit', select_whole_line=True, scroll_exit=False)
        self.grid.add_handlers({ascii.NL: self.cb_handler, KEY_DOWN: self.cb_handler})
        self.function = 'INSERT'
        self.table = None
        self.wherevalues = []
        self.cursorstack = []
        self.showagain = False

    def cb_handler(self, key):
        """
        Callback from the form when highlighted item gets key event
        :param key: key pressed to invoke action
        :return: None
        """
        if key == ascii.NL:
            if self.grid.edit_cell is not None:
                inputform = self.parentApp.getForm('GETINPUTFORM')
                inputform.name = self.grid.values[self.grid.edit_cell[0]][0]
                inputform.value = self.grid.values[self.grid.edit_cell[0]][len(self.grid.values[0]) - 1]
                self.cursorstack.append(self.grid.edit_cell)
                self.parentApp.switchForm('GETINPUTFORM')
        elif key == KEY_DOWN:
            if self.grid.edit_cell[0] == len(self.grid.values) - 1:
                self.grid.h_exit(ascii.TAB)
            else:
                self.grid.h_move_line_down(key)

    def updatedatafromexternal(self, value):
        self.data[self.grid.edit_cell[0]][len(self.grid.values[0]) - 1] = value

    def on_ok(self):
        if self.function == 'INSERT':
            # prep text for the columns
            colsqltext = '('
            valsqltext = '('
            valueslist = []
            for i in self.data:
                colsqltext += '\"' + i[0] + '\",'
                valsqltext += '%s,'
                valueslist.append(i[len(i) - 1])
            # trim that last comma
            colsqltext = colsqltext[:-1]
            colsqltext += ')'
            # trim that last comma
            valsqltext = valsqltext[:-1]
            valsqltext += ')'
            try:
                # execute the SQL
                SQL = 'insert into \"{0}\" {1} VALUES {2};'.format(self.table, colsqltext, valsqltext)
                value = tuple(valueslist)
                conn = Connection.Instance().getconnection()
                cursor = conn.cursor()
                cursor.execute(SQL, value)
                npyscreen.notify_confirm('{0} rows affected'.format(cursor.rowcount))
                self.showagain = False
            except Exception as e:
                npyscreen.notify_confirm('PSQL Error: {0}'.format(e.message))
                self.showagain = True
        elif self.function == 'EDIT':
            # prep text for the columns
            sqltext = ''
            wheretext = ''
            valueslist = []
            for idx, i in enumerate(self.data):
                sqltext += '\"' + i[0] + '\" = (%s), '
                valueslist.append(i[len(i) - 1])
                wheretext += '\"' + i[0] + '\" = \'' + str(self.wherevalues[idx]) + '\' AND '
            # trim that last comma and space
            sqltext = sqltext[:-2]
            # trim that last and and 2 spaces
            wheretext = wheretext[:-5]
            try:
                # execute the SQL
                SQL = 'update \"{0}\"  set {1} where {2};'.format(self.table, sqltext, wheretext)
                value = tuple(valueslist)
                conn = Connection.Instance().getconnection()
                cursor = conn.cursor()
                cursor.execute(SQL, value)
                npyscreen.notify_confirm('{0} rows affected'.format(cursor.rowcount))
                self.showagain = False
            except Exception as e:
                npyscreen.notify_confirm('PSQL Error: {0}'.format(e.message))
                self.showagain = True
        if not self.showagain:
            self.parentApp.switchForm('QUERYRESULTS')

    def on_cancel(self):
        self.parentApp.switchForm('QUERYRESULTS')
