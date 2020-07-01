import sys
from threading import Thread

from log import Logger
from pycrawler import Crawler
from storage_dup.sd_calback import call_back
from util.rabbitmqutil import connect
from util.running_params import data_q


class BaseStorageDup(Crawler):

    def simple(self):
        while True:
            task_url = data_q.get()
            print(task_url)
            single_over_signal = 1
            sys.exit(0)

    def run(self):
        try:
            Logger.logger.info("storage_dup 开始启动。。。")
            t1 = Thread(target=self.process)
            t1.start()
            Logger.logger.info("storage_dup 启动成功。。。")
            t1.join()
        except Exception as e:
            Logger.logger.info("storage_dup 启动失败：{}".format(e))

    def process(self):
        if not data_q.empty():
            self.simple()
        else:
            try:
                user = self.crawler_setting.get("mq").get("user")
                pwd = self.crawler_setting.get("mq").get("pwd")
                host = self.crawler_setting.get("mq").get("host")
                port = self.crawler_setting.get("mq").get("port")
                mq_queue = self.crawler_setting.get("mq_queue").get("storage_dup")
                if not mq_queue:
                    mq_queue = "storage_dup"
            except AttributeError:
                user = "pycrawler"
                pwd = "pycrawler"
                host = "127.0.0.1"
                port = 5672
                mq_queue = "storage_dup"

            mq_conn = connect(mq_queue, user, pwd, host, port)
            call_back(**{"no_ack": None, "channel": mq_conn, "routing_key": mq_queue})

