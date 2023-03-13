import dearpygui.dearpygui as GUI
import Utils.UI as UI


class Logger:
    def __init__(self, status, tag):
        self.logToUI = status
        self.tag = tag


    def SetConsoleStatus(self, status):
        self.logToUI = status
        
    def GetStatus(self):
        return self.logToUI

    def ShowMessage(self, message):
        if (self.logToUI):
            GUI.add_text("[" + self.tag + "] " + message, parent=UI.CONSOLE_WINDOW)
            self.ScrollToBottom()
        else:
            print (message)

    def ScrollToBottom(self):
        if (self.logToUI):
            GUI.set_y_scroll(UI.CONSOLE_WINDOW, -1.0)

    def Clear(self):
        if (self.logToUI):
            GUI.delete_item(UI.CONSOLE_WINDOW, children_only=True)

