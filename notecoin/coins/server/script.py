import os

from notebuild.core.core import command_line_parser
from notebuild.manage import BaseServer, ServerManage

# lsof -t -i:8444
# sudo kill -9 `sudo lsof -t -i:8444`
# nohup python notecoin_server.py  >>/notechats/logs/notecoin/strategy-$(date +%Y-%m-%d).log 2>&1 &


class CoinServer(BaseServer):
    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        super(CoinServer, self).__init__('notecoin_server', path)

    def init(self):
        manage = ServerManage()
        try:
            manage.init()
        except Exception as e:
            print(e)

        manage.add_job(server_name='notecoin_server',
                       directory=self.current_path,
                       command=f"python notecoin_server.py",
                       user='bingtao',
                       stdout_logfile="/notechats/logs/notecoin/strategy.log")
        manage.start()


def notecoin():
    args = command_line_parser()
    package = CoinServer()
    if args.command == 'init':
        package.init()
    elif args.command == 'stop':
        package.stop()
    elif args.command == 'start':
        package.start()
    elif args.command == 'restart':
        package.restart()
    elif args.command == 'help':
        info = """
init
stop
start
restart
        """
        print(info)
