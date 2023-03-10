from AppController import AppController
from Utils.Logger import Logger
import Utils.UI as UI
import dearpygui.dearpygui as GUI

# Trakt configuration functions

def AuthorizeUser(sender, app_data, user_data):
    controller.AuthorizeTraktUser()

def RefreshUserToken(sender, app_data, user_data):
    pass

def SaveTraktConfiguration(sender, app_data, user_data):
    controller.SaveTraktConfig()

# Application functions

def BackupHistory(sender, app_data, user_data):
    controller.BackupWatchedHistory()

def ClearConsole(sender, app_data, user_data):
    logger.Clear()

def ScrollDown(sender, app_data, user_data):
    logger.ScrollToBottom()

def ShowWindowPos(sender, app_data, user_data):
    logger.ShowMessage(str(GUI.get_viewport_pos()))
    logger.ShowMessage(str([GUI.get_viewport_client_height(), GUI.get_viewport_client_width()]))



GUI.create_context()
GUI.create_viewport(title='Backup Trakt for Me', width=UI.VIEWPORT_MIN_WIDTH, height=UI.VIEWPORT_MIN_HEIGHT)

with GUI.window(tag=UI.MAIN_WINDOW, no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
    with GUI.tab_bar():
        with GUI.tab(tag=UI.BACKUP_TAB, label="Backup/Restore"):
            GUI.add_text()
            with GUI.group(horizontal=True, horizontal_spacing=75):
                GUI.add_button(tag=UI.BACKUP_BUTTON, label="Backup history", callback=BackupHistory, width=GUI.get_viewport_min_width())
                GUI.add_text()

        with GUI.tab(label="Trakt API Settings"):
            GUI.add_text("API Key", show_label=True)
            GUI.add_input_text(tag=UI.CLIENT_ID, default_value="Your client ID")
            GUI.add_separator()
            GUI.add_text("Client Secret", show_label=True)
            GUI.add_input_text(tag=UI.CLIENT_SECRET, default_value="Your client secret")
            GUI.add_separator()
            GUI.add_text("Acces Token", show_label=True)
            GUI.add_input_text(tag=UI.ACCES_TOKEN, default_value="Your access token")
            GUI.add_separator()
            GUI.add_text("Refresh Token", show_label=True)
            GUI.add_input_text(tag=UI.REFRESH_TOKEN, default_value="Your refresh token")
            GUI.add_text()

            with GUI.group(horizontal=True):
                authorizeButton = GUI.add_button(tag=UI.AUTHORIZE_BUTTON, label="Authorize User", callback=AuthorizeUser)
                refreshButton = GUI.add_button(tag=UI.REFRESH_BUTTON, label="Refresh Token", callback=RefreshUserToken)
                saveCongig = GUI.add_button(tag=UI.SAVE_BUTTON, label="Save", callback=SaveTraktConfiguration)
         
    with GUI.group():
        GUI.add_text("Console", parent=UI.MAIN_WINDOW)
        GUI.add_separator(parent=UI.MAIN_WINDOW)

    with GUI.group(horizontal=True):
        GUI.add_button(tag=UI.SCROLL_BUTTON, label="Scroll to bottom", callback=ScrollDown)
        GUI.add_button(tag=UI.CLEAR_BUTTON, label="Clear", callback=ClearConsole)
        GUI.add_button(label="Show pos", callback=ShowWindowPos)

    with GUI.child_window(tag=UI.CONSOLE_WINDOW, label="Log"):
        pass

def LoadTraktSettings():
    GUI.set_value(UI.CLIENT_ID, controller.GetClientID())
    GUI.set_value(UI.CLIENT_SECRET, controller.GetClientSecret())
    GUI.set_value(UI.ACCES_TOKEN, controller.GetAccessToken())
    GUI.set_value(UI.REFRESH_TOKEN, controller.GetRefreshToken())
    logger.ShowMessage("Trakt settings UI updated")

logger = Logger(True, "UI")
controller = AppController()
LoadTraktSettings()

GUI.setup_dearpygui()
GUI.set_viewport_resizable(True)
GUI.set_viewport_min_width(UI.VIEWPORT_MIN_WIDTH)
GUI.set_viewport_min_height(UI.VIEWPORT_MIN_HEIGHT)
GUI.set_primary_window(UI.MAIN_WINDOW, True)
GUI.show_viewport()
GUI.start_dearpygui()
GUI.destroy_context()