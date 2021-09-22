try:
    input = raw_input
except NameError:
    pass

import os
from io import StringIO

global import_fail
try:  # Check if the Matlab Engine is installed
    import matlab.engine
    from matlab.engine import RejectedExecutionError as MatlabTerminated
except ImportError:
    print("Matlab Engine for Python cannot be detected. Please install it for the extension to work")
    import_fail = True
else:
    import_fail = False


class MatlabInterface:
    global import_fail

    def __init__(self):
        # OS checks related work
        if os.name == 'nt':
            self.cls_str = 'cls'
        else:
            self.cls_str = 'clear'
        if not import_fail:
            print("Starting Matlab...")
            self.eng = matlab.engine.start_matlab()
        else:
            print("Could not start Matlab")

    def stop(self):
        print("stopping Matlab...")
        self.eng.quit()
        return "stopped OK"

    def run_command(self, command, verbose):
        if not import_fail:
            try:
                if verbose:
                    print("Running Command: {}".format(command))
                stream = StringIO()
                err_stream = StringIO()
                self.eng.eval(command, nargout=0,
                              stdout=stream, stderr=err_stream)
                return stream.getvalue().replace('ans =', '').strip()
            except MatlabTerminated:
                print(stream.getvalue(), err_stream.getvalue(), sep="\n")
                print("Matlab terminated. Restarting the engine...")
                self.eng = matlab.engine.start_matlab()
                return "Matlab restarted OK"
            except:  # The other exceptions are handled by Matlab
                errList = err_stream.getvalue().split('\n\n')
                newList = [error.replace('\n', '') for error in errList]
                return list(filter(None, newList))

