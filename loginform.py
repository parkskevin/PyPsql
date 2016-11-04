import npyscreen
from connection import Connection


class LoginForm(npyscreen.ActionPopup):
    """
    A form that gathers input from user for psql database connection string.
    """
    def create(self):
        """
        Does setup of widgets required for login to occur
        :return:
        """
        self.center_on_display()
        self.name = 'Setup Connection'
        self.db = self.add(npyscreen.TitleText, w_id='w_database', name='Database:')
        self.user = self.add(npyscreen.TitleText, w_id='w_user', name='User:')
        self.password = self.add(npyscreen.TitlePassword, w_id='w_password', name='Password:')
        self.host = self.add(npyscreen.TitleText, w_id='w_host', name='Host:')
        self.port = self.add(npyscreen.TitleText, w_id='w_port', name='Port:')

    def on_ok(self):
        """
        on_ok handler tries to make a connection
        :return:
        """
        connectargs = {'database': None if self.db.value is '' else self.db.value,
                       'user': None if self.user.value is '' else self.user.value,
                       'password': None if self.password.value is '' else self.password.value,
                       'host': None if self.host.value is '' else self.host.value,
                       'port': None if self.port.value is '' else self.port.value}
        conn = Connection.Instance()
        try:
            conn.connect(**connectargs)
            npyscreen.notify_confirm("Connected! DSN: {0}".format(conn.getconnection().dsn), editw=1)
            self.parentApp.switchForm("MAIN")
        except Exception as e:
            npyscreen.notify_confirm(e.message)

    def on_cancel(self):
        """
        on_cancel handler simply exits
        :return:
        """
        self.parentApp.setNextForm(None)
