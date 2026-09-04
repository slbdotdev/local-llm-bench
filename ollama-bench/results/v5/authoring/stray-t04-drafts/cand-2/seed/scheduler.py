class Scheduler:
    def __init__(self, runner):
        self.runner = runner
        self.accepting = True
        self.pending = []

    def submit(self, job):
        if not self.accepting:
            return False
        self.pending.append(job)
        return True

    def begin_shutdown(self):
        self.accepting = False
        while self.pending:
            job = self.pending.pop(0)
            self.runner(job)
