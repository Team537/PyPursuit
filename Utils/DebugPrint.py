import time

class DebugPrint:
    debug_functions = []
    last_time = time.time()
    rate = 1

    def __init__(self, rate):
        DebugPrint.rate = rate
        DebugPrint.last_time = time.time()
        print(f"There are {len(self.debug_functions)} debug functions")

    @staticmethod
    def add_debug_function(debug_function):
        if isinstance(debug_function, str):
            DebugPrint.debug_functions.append(lambda: print(debug_function))
            return
        DebugPrint.debug_functions.append(debug_function)

    @staticmethod
    def update():
        if time.time() - DebugPrint.last_time > DebugPrint.rate:
            DebugPrint.last_time = time.time()
            print(f"===================={DebugPrint.last_time}====================")
            for debug_print in DebugPrint.debug_functions:
                debug_print()
            print(f"====================END====================")
        DebugPrint.debug_functions = []
