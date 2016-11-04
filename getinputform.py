import npyscreen

class GetInputForm(npyscreen.ActionPopup):

    def activate(self):
        self.beforeEditing()
        self.edit()

    def beforeEditing(self):
        self.inputwidget.name = self.name
        self.inputwidget.value = self.value
        self.inputwidget.make_contained_widgets()

    def create(self):
        self.name = 'Default Text'
        self.value = 'Default Value'
        self.savedvalue = ''
        self.inputwidget = self.add(npyscreen.TitleText)
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.on_cancel

    def on_ok(self):
        self.savedvalue = self.inputwidget.value
        self.parentApp.getForm('EDITFORM').updatedatafromexternal(self.savedvalue)
        self.parentApp.switchForm('EDITFORM')

    def on_cancel(self):
        self.parentApp.switchForm('EDITFORM')

