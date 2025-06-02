class Mux:
    def __init__(self):
        self.input0 = 0
        self.input1 = 0
        self.select = 0  # 0 selects input0; 1 selects input1
        self.output = 0

    def evaluate(self):
        # Recalculate the mux output based on the current values.
        self.output = self.input1 if self.select else self.input0