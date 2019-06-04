from threading import Event, Thread

class StopService(Exception):
    pass

class Service:
    running_services = []

    @classmethod
    def register(cls, service):
        cls.running_services.append(service)

    @classmethod
    def deregister(cls, service):
        cls.running_services.remove(service)

    @classmethod
    def stop_all(cls):
        for service in cls.running_services:
            service.stop()

    @classmethod
    def wait_all(cls):
        for service in cls.running_services:
            service.wait()

    def __init__(self):
        self.stopped = Event()
        self.init_done = Event()

    def interrupt(self):
        pass # Sublasses override to set events

    def stop(self):
        self.stopped.set()
        self.interrupt()

    def await_init_done(self):
        self.init_done.wait()

    def wait(self, *args):
        self.svc_thread.join(*args)

    def sleep(self, time):
        self.stopped.wait(time)
        if self.stopped.isSet():
            raise StopService('Service stopped')

    def init(self):
        # Some services might not need to do setup, so it's OK not to override
        pass

    def run(self):
        raise Exception("Service.run(): Implement this in subclass")

    def cleanup(self):
        # Some services might not need to clean up, so it's OK not to override
        pass

    def service_thread(self):
        Service.register(self)
        self.init()
        self.init_done.set()
        try:
            self.run()
        except StopService:
            # Graceful stop, don't re-raise
            pass
        except:
            # Other error, re-raise
            raise
        finally:
            # Always cleanup
            self.cleanup()
        Service.deregister(self)

    def start(self, synchronous_init=False):
        self.svc_thread = Thread(target=self.service_thread)
        self.svc_thread.start()
        if synchronous_init:
            self.await_init_done()

    def start_subservice(self, s):
        """ A service that starts other services should do so by calling
        this function, to avoid funky race conditions when stopping services
        that are about to launch other services """
        # If we've been stopped since we last woke up, don't actually start
        # this service.
        if self.stopped.isSet():
            raise StopService('Service Stopped')
        # Start the service knowing we aren't stopped.
        s.start()
        # Now that the service is registered to be stopped if stop_all is called
        # we check again, to see if we have been stopped since starting this
        # subservice, we need to do this because we might have been stopped since
        # we last checked, but before the sub service was registered.
        if self.stopped.isSet():
            s.stop()
            s.wait()
            raise StopService('Service Stopped')

