from communication import SmsSender, MailSender


class TestSmsSender(SmsSender):
    def __init__(self):
        super().__init__()
        self._called = False

    def send(self, schedule):
        print("Test SMS Send!")
        self._called = True

    @property
    def called(self):
        return self._called

class TestEmailSender(MailSender):
    def __init__(self):
        super().__init__()
        self._called = False

    @property
    def called(self):
        return self._called

    def send_mail(self, schedule):
        print("Test Email Send!")
        self._called = True