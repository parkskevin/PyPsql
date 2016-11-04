import npyscreen
from psycopg2 import ProgrammingError
from psycopg2 import Error
from connection import Connection
from curses import ascii
from curses import KEY_DOWN

class QueryResultsForm(npyscreen.ActionFormMinimal):
    OK_BUTTON_TEXT = 'BACK'
    """
    Class that displays results from a query
    """

    def activate(self):
        """
        Need to override activate here in order to do checking of the Connection
        ** NOTE ** : you must call before/edit/after editing on your own if you override activate
        :return:
        """
        if self.value is None or self.SQL is None:
            npyscreen.notify_confirm('Error: No query data provided')
            self.parentApp.switchForm('MAIN')
        elif self.value == ';':
            npyscreen.notify_confirm('Error: Empty query provided')
            self.parentApp.switchForm("MAIN")
        elif Connection.Instance().getconnection() is None:
            npyscreen.notify_confirm('Error: No connection present')
            self.parentApp.switchForm('LOGIN')
        else:
            if self.mode == 'QUERY':
                self.cell = [0,0]
                self.submenucmd = None
            """
            there are times when we need to open a form indicated from submenu selection and in order to do so
            we need to branch before reaching the edit of this form
            """
            try:
                if self.beforeEditing():
                    self.edit()
                else:
                    self.editing = False
            except Exception as e:
                npyscreen.notify_confirm(e.message, editw=1)
                self.editing = False
                self.parentApp.switchFormPrevious()

    def beforeEditing(self):
        """
        Update the results lists based on the command received from the structuresubmenu
        In the case this form is being used by the query, we expected the submenucmd to be None
        :return:
        """
        if self.submenucmd is None:
            npyscreen.blank_terminal()
            self.updateresults()
            return True
        elif self.submenucmd == 'BACK':
            return True
        elif self.submenucmd == 'BROWSE':
            self.submenu_browse()
            return True
        elif self.submenucmd == 'STRUCTURE':
            self.submenu_structure()
            return True
        elif self.submenucmd == 'INSERT':
            self.submenu_insert()
            return False
        elif self.submenucmd == 'EMPTY':
            self.submenu_empty()
            return True
        elif self.submenucmd == 'DROP':
            self.submenu_drop()
            return True
        elif self.submenucmd == 'EDIT':
            self.submenu_edit()
            return False
        elif self.submenucmd == 'DELETE':
            self.submenu_delete()
            return True
        else:
            return True

    def submenu_browse(self):
        self.querystack.append((self.SQL, self.value, self.grid.edit_cell, self.table))
        self.cell = [0, 0]
        self.table = self.cleaneddata[self.grid.edit_cell[0]][self.grid.edit_cell[1]]
        self.SQL = "select * from \"%s\" order by 1 ASC;" % self.table
        self.value = ()
        try:
            self.updateresults()
        except Exception as e:
            npyscreen.notify_confirm(e.message, editw=1)
            self.submenucmd = None
            self.backonequery()

    def submenu_structure(self):
        self.querystack.append((self.SQL, self.value, self.grid.edit_cell, self.table))
        self.cell = [0, 0]
        self.table = self.cleaneddata[self.grid.edit_cell[0]][self.grid.edit_cell[1]]
        # http://stackoverflow.com/questions/16653828/joining-2-select-queries-on-2-different-tables-in-postgresql
        self.SQL = "select column_name as \"Column\", udt_name as \"Type\", is_nullable as \"Null\" from information_schema.columns where table_name = (%s) order by 1 ASC;"
        self.value = (self.table, )
        try:
            self.updateresults()
        except Exception as e:
            npyscreen.notify_confirm(e.message, editw=1)
            self.editing = False
            self.parentApp.switchFormPrevious()

    def submenu_insert(self):
        # need the table to insert into
        table = self.cleaneddata[self.grid.edit_cell[0]][self.grid.edit_cell[1]]
        # helpful to show the structure of data to insert
        SQL = "select column_name as \"Column\", udt_name as \"Type\", is_nullable as \"Null\" from information_schema.columns where table_name = (%s) order by 1 ASC;"
        value = (table, )
        # execute the query to gather table column data
        conn = Connection.Instance().getconnection()
        cursor = conn.cursor()
        cursor.execute(SQL, value)
        data = cursor.fetchall()
        # http://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
        headers = [desc[0] for desc in cursor.description]
        headers.append('Value')
        cleaneddata = self.cleanUpListForOutput(data)
        # need to append a new entry to each list
        for i in cleaneddata:
            i.append('')
        editform = self.parentApp.getForm('EDITFORM')
        editform.headers = headers
        editform.data = cleaneddata
        editform.table = table
        editform.function = 'INSERT'
        # reset to None so results get updated when we're done
        self.submenucmd = None
        self.parentApp.switchForm('EDITFORM')

    def submenu_edit(self):
        # helpful to show the structure of data to insert
        SQL = "select column_name as \"Column\", udt_name as \"Type\", is_nullable as \"Null\" from information_schema.columns where table_name = (%s) order by 1 ASC;"
        value = (self.table, )
        # execute the query to gather table column data
        conn = Connection.Instance().getconnection()
        cursor = conn.cursor()
        cursor.execute(SQL, value)
        data = cursor.fetchall()
        # http://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
        headers = [desc[0] for desc in cursor.description]
        headers.append('Value')
        cleaneddata = self.cleanUpListForOutput(data)
        # need to append a new entry to each list
        curvalues = self.grid.selected_row()
        count = 0
        for i in cleaneddata:
            i.append(curvalues[count])
            count += 1
        # set up the editing form
        editform = self.parentApp.getForm('EDITFORM')
        editform.headers = headers
        editform.wherevalues = curvalues
        editform.data = cleaneddata
        editform.table = self.table
        editform.function = 'EDIT'
        # reset to None so results get updated when we're done
        self.submenucmd = None
        self.parentApp.switchForm('EDITFORM')

    def submenu_delete(self):
        # get current row's value to form query with headers
        curvalues = self.grid.selected_row()
        # prompt user to be sure, then just execute delete query from here
        retval = npyscreen.notify_yes_no('Are you sure you wish to delete this row?', editw=1)
        if retval:
            # do the delete
            wheretext = ''
            for idx, i in enumerate(self.headers):
                wheretext += '\"' + i + '\" = (%s) AND '
            # trim that last and and 2 spaces
            wheretext = wheretext[:-5]
            SQL = 'delete from \"{0}\" where {1};'.format(self.table, wheretext)
            try:
                value = tuple(curvalues)
                conn = Connection.Instance().getconnection()
                cursor = conn.cursor()
                cursor.execute(SQL, value)
                npyscreen.notify_confirm('{0} rows affected'.format(cursor.rowcount), editw=1)
                self.cell = [0,0]
            except Exception as e:
                npyscreen.notify_confirm(e.message, editw=1)
            # reflect the change immediately
            try:
                self.updateresults()
            except Exception as e:
                npyscreen.notify_confirm(e.message, editw=1)
                self.backonequery()

    def submenu_empty(self):
        """
        Truncate the selected table if possible
        :return:
        """
        # need the table to truncate
        table = self.cleaneddata[self.grid.edit_cell[0]][self.grid.edit_cell[1]]
        # determine if user wants to cascade or not
        cascadeval = npyscreen.notify_yes_no('Would you like to cascade to tables having foreign-key references?', editw=1)
        if cascadeval:
            SQL = 'truncate \"{0}\" CASCADE;'.format(table)
        else:
            SQL = 'truncate \"{0}\";'.format(table)
        retval = npyscreen.notify_yes_no('Are you sure you wish to empty this table?', editw=1)
        if retval:
            value = ()
            try:
                conn = Connection.Instance().getconnection()
                cursor = conn.cursor()
                cursor.execute(SQL, value)
                npyscreen.notify_confirm('Table {0} emptied'.format(table), editw=1)
            except Exception as e:
                npyscreen.notify_confirm(e.message)

    def submenu_drop(self):
        """
        Drop the selected table
        :return:
        """
        # need the table to drop
        table = self.cleaneddata[self.grid.edit_cell[0]][self.grid.edit_cell[1]]
        # determine if user wants to cascade or not
        cascadeval = npyscreen.notify_yes_no('Would you like to cascade to tables having foreign-key references?', editw=1)
        if cascadeval:
            SQL = 'drop table \"{0}\" CASCADE;'.format(table)
        else:
            SQL = 'drop table \"{0}\";'.format(table)
        retval = npyscreen.notify_yes_no('Are you sure you wish to drop this table?', editw=1)
        if retval:
            value = ()
            try:
                conn = Connection.Instance().getconnection()
                cursor = conn.cursor()
                cursor.execute(SQL, value)
                npyscreen.notify_confirm('Table {0} dropped'.format(table), editw=1)
            except Error as e:
                npyscreen.notify_confirm(e.message, editw=1)
            try:
                self.cell = [0,0]
                self.updateresults()
            except Exception as e:
                self.submenucmd = None
                self.parentApp.setNextForm('MAIN')
                raise

    def updateresults(self):
        """
        Actual data gathering of results
        :return:
        """
        conn = Connection.Instance().getconnection()
        cursor = conn.cursor()
        try:
            cursor.execute(self.SQL, self.value)
            count = cursor.rowcount
            if count > 0:
                try:
                    self.data = cursor.fetchall()
                except ProgrammingError as p:
                    raise Exception('{0} row affected'.format(count))
                # http://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
                self.headers = [desc[0] for desc in cursor.description]
                self.cleaneddata = self.cleanUpListForOutput(self.data)
                self.grid.col_titles = self.headers
                self.grid.columns = len(cursor.description)
                self.grid.values = self.cleaneddata
                self.grid.edit_cell = self.cell
                self.grid.make_contained_widgets()
                self.grid.ensure_cursor_on_display_up()
                self.grid.ensure_cursor_on_display_down_right()
            elif count == 0:
                if cursor.statusmessage.split()[1] == '0':
                    raise Exception('No results to display')
                else:
                    raise Exception('Query successful: {0}'.format(cursor.statusmessage))
            else:
                raise Exception('Query successful: {0}'.format(cursor.statusmessage))
        except Exception as e:
            raise e

    def create(self):
        """
        Creation of the widgets being used.
        :return:
        """
        self.querystack = []
        self.value = None
        self.SQL = None
        self.cell = [0, 0]
        self.table = None
        self.mode = 'STRUCTURE'
        self.submenucmd = None
        self.headers = None
        self.bypass = None
        self.grid = self.add(npyscreen.GridColTitles, name='Results', select_whole_line=True, columns=3)
        self.grid.add_handlers({ascii.NL: self.cb_handler, ascii.ESC: self.cb_handler, KEY_DOWN: self.cb_handler})

    def cb_handler(self, key):
        """
        Callback from the form when highlighted item gets enter key. Does a dummy select * type query for now,
        so obviously only works on selections from tables
        :param key: key pressed to invoke action
        :return: None
        """
        if key == ascii.NL:
            if self.grid.edit_cell is not None:
                # only bring up options when in structured mode
                if self.mode == 'STRUCTURE':
                    # don't show the submenu when it's a structure command
                    if self.submenucmd != 'STRUCTURE':
                        # need to set the menu appropriately based on how deep into process we are
                        self.parentApp.getForm('STRUCTURESUBMENU').state = len(self.querystack)
                        self.parentApp.switchForm('STRUCTURESUBMENU')
        elif key == ascii.ESC:
            if self.mode == 'STRUCTURE':
                self.submenucmd = None
            self.backonequery()
        elif key == KEY_DOWN:
            if self.grid.edit_cell[0] == len(self.grid.values) - 1:
                self.grid.h_exit(ascii.TAB)
            else:
                self.grid.h_move_line_down(key)

    def backonequery(self):
        """
        Uses the internal stack (list) to repopulate the last query in order to step 'back' through structure query
        :return:
        """
        if len(self.querystack) == 0:
            # reset the queryresultsform cell since we're done using it
            self.cell = [0,0]
            if self.mode == 'QUERY':
                # relaunch the query form since we can't 'back up'
                self.parentApp.switchForm('QUERYFORM')
            else:
                self.exit()
        else:
            # pop the last query so we can execute it again and update results
            self.SQL, self.value, self.cell, self.table = self.querystack.pop()
            try:
                self.updateresults()
            except Exception as e:
                npyscreen.notify_confirm(e.message, editw=1)
                self.editing = False
                self.parentApp.switchFormPrevious()

    def exit(self):
        """
        Exiting the form
        :return:
        """
        self.parentApp.switchForm('MAIN')

    def cleanUpListForOutput(self, data):
        """
        Cleans up the values from a query into a pretty 2D matrix for grid display
        :param data: raw PSQL query data
        :return: a cleaned up list in terms of PSQL syntax for display in a Grid widget
        """
        newlist = []
        for i in data:
            sublist = []
            for j in i:
                sublist.append(j)
            newlist.append(sublist)
        return newlist

    def on_ok(self):
        if self.mode == 'QUERY':
            self.editing = False
            self.backonequery()
        elif len(self.querystack) == 0:
            self.parentApp.switchForm('MAIN')
        else:
            self.editing = False
            self.submenucmd = None
            self.backonequery()
