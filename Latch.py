from types import SimpleNamespace


class Latch:
    def __init__(self, bits): # Initialize Latch with given bits list with all zero values
        init_dict   = {name: 0 for name in bits}
        self.input  = SimpleNamespace(**init_dict)
        self.output = SimpleNamespace(**init_dict)
        self.EN = True

    def flush(self): # Write zeros to the output and the input on the edge
        for name in self.input.__dict__:
                setattr(self.input, name, 0)
                setattr(self.output, name, 0)

    def transfer(self): 
        if self.EN: # Copy the input to the output on the edge 
            for name, value in self.input.__dict__.items():
                setattr(self.output, name, value)
        else: 
            self.flush()

    def duplicate(self):
        if self.EN: # Copy the output to the input and flush output on the edge 
            for name, value in self.output.__dict__.items():
                setattr(self.input, name, value)
                setattr(self.output, name, 0)
        else: 
            self.flush()