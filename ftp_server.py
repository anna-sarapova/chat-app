from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
print('1')
authorizer.add_user("user", "12345", ".", perm="elradfmw")
print('2')
handler = FTPHandler
print('3')
handler.authorizer = authorizer
print('4')
server = FTPServer(("127.0.0.1", 4001), handler)
print('5')
server.serve_forever()
