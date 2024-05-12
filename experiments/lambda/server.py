import os, sys, json, argparse, importlib, traceback
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.netutil
import subprocess
import socket
import time
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
import json
# Note: SOCK doesn't use this anymore (it uses sock2.py instead), but
# this is still here because we haven't updated docker.go yet.
UDP_IP = "127.0.0.1"
UDP_PORT = 4009
MAX_WORKERS = 1000
sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP

def send_message(context):
    sock.sendto(bytes(context,encoding="utf-8"), (UDP_IP, UDP_PORT))


HOST_DIR = '/host'
PKGS_DIR = '/packages'
HANDLER_DIR = '/handler'

sys.path.append(PKGS_DIR)
sys.path.append(HANDLER_DIR)

FS_PATH = os.path.join(HOST_DIR, 'fs.sock')
SOCK_PATH = os.path.join(HOST_DIR, 'ol.sock')
STDOUT_PATH = os.path.join(HOST_DIR, 'stdout')
STDERR_PATH = os.path.join(HOST_DIR, 'stderr')
SERVER_PIPE_PATH = os.path.join(HOST_DIR, 'server_pipe')

PROCESSES_DEFAULT = 10
initialized = False

parser = argparse.ArgumentParser(description='Listen and serve cache requests or lambda invocations.')
parser.add_argument('--cache', action='store_true', default=False, help='Begin as a cache entry.')

# run after forking into sandbox
def init():
    global initialized, f
    if initialized:
        return

    # assume submitted .py file is /handler/f.py
    import f

    initialized = True

log_file = open("logs.txt","w")
def WriteOwnLogs(text):
    log_file.write(text+"\n")
    log_file.flush()

class SockFileHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def async_f(self, event, st):
        process = subprocess.Popen(["python3","/handler/f.py", str(event["n"])],stdout=subprocess.PIPE)
        #process = subprocess.Popen(["schedtool", "-N","-e","python3","/handler/f.py", str(event["n"])],stdout=subprocess.PIPE)
        pid = process.pid
        event["pid"] = str(pid)
        #self.write("pid "+str(pid)+"\n")
        #send_message(json.dumps(event))
        process.wait()
        #send_message(json.dumps(event))
        out, err = process.communicate()
        #self.write(out)
        #self.write("out "+str(out)+"\n")
        job_id = event["id"]
        job_type = event["job"]
        n = event["n"]
        et = time.time()
        self.write("{} {} {} {} {} {}\n".format(job_id, st, et-st, pid, n, job_type))
        #self.write("exec "+str(et-st)+"\n")
        return out, et-st

    @gen.coroutine
    def post(self):
        try:
            st = time.time()
            data = self.request.body
            WriteOwnLogs("Logs request "+str(self.request))
            self.write("data"+str(data)+"\n")
            try :
                event = json.loads(data)
            except:
                self.set_status(400)
                self.write('bad POST data: "%s"'%str(data))
                return
            #self.write(json.dumps(f.f(event)))
            res = yield self.async_f(event, st)
        except Exception:
            self.set_status(500) # internal error
            self.write(traceback.format_exc())

tornado_app = tornado.web.Application([
    (r".*", SockFileHandler),
])

# listen on sock file with Tornado
def lambda_server():
    global HOST_PIPE
    init()
    server = tornado.httpserver.HTTPServer(tornado_app)
    socket = tornado.netutil.bind_unix_socket(SOCK_PATH)
    server.add_socket(socket)
    # notify worker server that we are ready through stdout
    # flush is necessary, and don't put it after tornado start; won't work
    with open(SERVER_PIPE_PATH, 'w') as pipe:
        pipe.write('ready')
    tornado.ioloop.IOLoop.instance().start()
    server.start(PROCESSES_DEFAULT)

# listen for fds to forkenter
def cache_loop():
    import ns

    signal = "cache"
    r = -1
    count = 0
    # only child meant to serve ever escapes the loop
    while r != 0 or signal == "cache":
        if r == 0:
            print('RESET')
            flush()
            ns.reset()

        print('LISTENING')
        flush()
        data = ns.fdlisten(FS_PATH).split()
        flush()

        mods = data[:-1]
        signal = data[-1]

        r = ns.forkenter()
        sys.stdout.flush()
        if r == 0:
            redirect()
            # import modules
            for mod in mods:
                print('importing: %s' % mod)
                try:
                    globals()[mod] = importlib.import_module(mod)
                except Exception as e:
                    print('failed to import %s with: %s' % (mod, e))

            print('signal: %s' % signal)
            flush()

        print('')
        flush()

        count += 1

    print('SERVING HANDLERS')
    flush()
    lambda_server()

def flush():
    sys.stdout.flush()
    sys.stderr.flush()

def redirect():
    sys.stdout.close()
    sys.stderr.close()
    sys.stdout = open(STDOUT_PATH, 'w')
    sys.stderr = open(STDERR_PATH, 'w')

if __name__ == '__main__':
    args = parser.parse_args()
    redirect()
    WriteOwnLogs("Logs start ")
    if args.cache:
        cache_loop()
    else:
        lambda_server()
