from hardware import Component

class MockButton(Component):
    def connect(self):
        pass

    def press(self):
        self.callback(1)

    def release(self):
        self.callback(0)
