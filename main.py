from AppController import AppController
import TraktAPI.TraktAPIUtils as TraktAPIUtils

def main():
    controller = AppController()
    codeStatus = controller.authorizeTraktUser()
    if (codeStatus == TraktAPIUtils.SUCCESS):
        controller.backupWatchedHistory()
    else:
        print (TraktAPIUtils.statusMessages[codeStatus])
main()