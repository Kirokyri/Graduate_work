import sys
import yadisk 
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import QDesktopServices, QClipboard
from PyQt5.QtCore import QUrl

class Authenticate():
    token_file = 'data/token.txt'
    client_id = "236b60cb77e94e8b8aef1781bd53ea75"
    client_secret = "c7f803ee6a0243689c8efd9ea4f92e08"
    redirect_uri = "https://oauth.yandex.ru/verification_code"
    token = "y0_AgAAAABFAbmLAArAjwAAAADwrN9yWawqWRH8Sp2wcpW6h6sv_4QzKhs"

    @classmethod
    def authenticate(self):
        self.y = yadisk.YaDisk()
        _token = read_token_file(self.token_file)
        if not _token == '':
            self.y.token = _token
            if self.y.check_token():
                make_app_dir(self.y)
                #make_token_file(self.token_file, _token)
                return self.y
            else:
                self.y = yadisk.YaDisk()

        self.y, app = authenticate_with_oauth(self.client_id, self.client_secret)
        make_app_dir(self.y)
        make_token_file(self.token_file, self.y.token)
        app.quit()
        return self.y

def authenticate_with_oauth(client_id, client_secret):
    def loadLoginUi():
        Form, Window = uic.loadUiType("data/LoginScreenFinal.ui")
        app = QApplication(sys.argv)
        window = Window()
        form = Form()
        form.setupUi(window)
        window.show()
        window.resize(507, 100)

        form.proceedBtn.setText('Скопировать')
        form.openLinkBtn.clicked.connect(open_link_onClickBtn)
        form.okBtn.clicked.connect(enterCode_OnClickBtn)
        form.proceedBtn.clicked.connect(proceed_onClickBtn)
        return window, form, app
    
    def open_link_onClickBtn():#app, form, window):
        nonlocal auth_url
        QDesktopServices.openUrl(QUrl(auth_url))
        form.stackedWidget.setCurrentIndex(1)
        window.resize(235, 153)

    def proceed_onClickBtn():
        nonlocal auth_url
        form.stackedWidget.setCurrentIndex(1)
        window.resize(235, 153)
        clipboard = QApplication.clipboard()
        clipboard.setText(auth_url)
        QMessageBox.information(window, 'Оповещение', 'Ссылка скопирована в буфер.')

    def enterCode_OnClickBtn():#app, form, window):
        code = form.lineEdit.text()
        try:
            # Обмен кода авторизации на токен доступа
            y.token = y.get_token(code).access_token
        except Exception as e:
            print(f"Аутентификация не удалась: {e}")
            QMessageBox.information(window, 'Оповещение', 'Аутентификация не удалась.')
        window.close()
        #app.quit()

    
    y = yadisk.YaDisk(client_id, client_secret)#, token=token)
    auth_url = y.get_code_url()
    window, form, app = loadLoginUi()
    app.exec()

    if y.check_token():
        return y, app
    else:
        QMessageBox.information(window, 'Оповещение', 'Неверный код.')
        #print('Неверный код.')
        
def make_app_dir(y: yadisk.YaDisk):
    try:
        if not y.exists('/App'):
            y.mkdir('/App')
    except Exception as e:
        print(e)

def make_token_file(path: str, token: str):
    with open(path, 'w') as file:
        file.write(token)
        file.close()
    return

def read_token_file(path: str) -> str:
    try:
        with open(path, 'r') as file:
            token = file.read()
            file.close()
            return token
    except FileNotFoundError:
        return ''
    except Exception as e:
        print(f'Error: {e}')
        return ''


def main():
    #y = authenticate_with_oauth(client_id, client_secret)
    #make_app_dir(y)

    y = Authenticate.authenticate()

if __name__ == '__main__':
    main()