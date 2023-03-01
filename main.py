from AppController import AppController
import TraktAPI.APIStatusCodes as APIStatusCodes

def main():
    controller = AppController()
    codeStatus = controller.authorizeTraktUser()
    if (codeStatus == APIStatusCodes.SUCCESS):
        controller.backupWatchedHistory()
    else:
        print (APIStatusCodes.statusMessages[codeStatus])
main()