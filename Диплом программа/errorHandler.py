from datetime import datetime

class ErrorHandler():
    
    @classmethod
    def handle(self, errorMessage: str):
        with open('log.txt', 'a') as log:
            cur_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            log.write(f"{cur_date} || {errorMessage}")
            log.write('\n')
        #print(errorMessage)