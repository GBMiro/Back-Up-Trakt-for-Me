from AppController import AppController
import TraktAPI.TraktAPIUtils as TraktAPIUtils
import dearpygui.dearpygui as GUI

   
#statusCode = controller.AuthorizeTraktUser()
#if (statusCode == TraktAPIUtils.SUCCESS):
#    statusCode = controller.BackupWatchedHistory()
    
#print (TraktAPIUtils.statusMessages[statusCode])


#def ShowWindow(sender, app_data, user_data):
#    window = user_data
#    if (GUI.does_item_exist(window) and GUI.is_item_visible(window)):
#        GUI.hide_item(window)
#    elif (GUI.does_item_exist(window) and not GUI.is_item_visible(window)):
#          GUI.show_item(window)


GUI.create_context()
GUI.create_viewport(title='Backup Trakt for Me', width=700, height=500)

controller = AppController()



def printMe(sender):
    GUI.add_text(sender, parent="Console")

with GUI.window(tag="Main", no_collapse=True, no_move=True, show=True, no_title_bar=True, width=GUI.get_viewport_width(), height=GUI.get_viewport_height()):
    with GUI.tab_bar():
        with GUI.tab(label="Backup/Restore"):
            backupButton = GUI.add_button(tag="Backup Button", label="Backup history")
        with GUI.tab(label="Trakt API Settings"):
            GUI.add_text("API Key", show_label=True)
            GUI.add_input_text(tag="APIKey", default_value=controller.GetClientID())
            GUI.add_separator()
            GUI.add_text("Client Secret", show_label=True)
            GUI.add_input_text(tag="clientSecret", default_value=controller.GetClientSecret())
            GUI.add_separator()
            GUI.add_text("Acces Token", show_label=True)
            GUI.add_input_text(tag="accessToken", default_value=controller.GetAccessToken())
            GUI.add_separator()
            GUI.add_text("Refresh Token", show_label=True)
            GUI.add_input_text(tag="refreshToken", default_value=controller.GetRefreshToken())
            GUI.add_text()

            with GUI.group(horizontal=True):
                authorizeButton = GUI.add_button(tag="Authorize Button", label="Authorize User")
                refreshButton = GUI.add_button(tag="Refresh Button", label="Refresh Token")
                saveCongig = GUI.add_button(tag="Save Config", label="Save", callback=printMe)
            
            GUI.add_text()

    with GUI.child_window(tag="Console", label="Log"):
        GUI.add_text("Test", show_label=True)

GUI.setup_dearpygui()
GUI.set_viewport_resizable(False)
GUI.set_primary_window("Main", True)
GUI.show_viewport()
GUI.start_dearpygui()
GUI.destroy_context()