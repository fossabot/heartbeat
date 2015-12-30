#!/bin/env python3
import sys, os

if (sys.version_info < (3, 3)):
    sys.path.append('/lib/python3.2/site-packages')

from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import NotificationHandler
from heartbeat.modules import EventServer
from heartbeat.network import SocketBroadcaster
from heartbeat.platform import Topics
from heartbeat.platform import get_config_manager, load_notifiers, load_monitors
import threading
import time
import logging, logging.handlers
import concurrent.futures


logger = logging.getLogger("heartbeat")
logger.setLevel(logging.DEBUG)
try:
    filehandler = logging.handlers.TimedRotatingFileHandler(
            filename='/var/log/heartbeat.log',
            when='W0'
            )
except Exception:
    print("No write permissions to log directory. Using current directory")
    filehandler = logging.handlers.TimedRotatingFileHandler(
            filename="./heartbeat.log",
            when="W0"
            )
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(name)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
termhandler = logging.StreamHandler(sys.stdout)
termhandler.setLevel(logging.INFO)
logger.addHandler(termhandler)

def main():
    threads = []

    logger.debug("Loading configuration")
    settings = get_config_manager()

    dispatcher = EventServer()

    logger.info("Bringing up notification/event handling")
    notifyPool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    notifiers = load_notifiers(settings.heartbeat.notifiers)

    notificationHandler = NotificationHandler(
            notifiers,
            notifyPool,
            )

    dispatcher.attach(
        Topics.INFO,
        notificationHandler.receive_event
        )
    dispatcher.attach(
        Topics.WARNING,
        notificationHandler.receive_event
        )
    dispatcher.attach(
        Topics.DEBUG,
        notificationHandler.receive_event
        )

    if (settings.heartbeat.enable_heartbeat):
        logger.info("Bringing up system heartbeat")
        broadcaster = SocketBroadcaster(
                settings.heartbeat.port,
                settings.heartbeat.monitor_server
                )
        server = Heartbeat(
            2,
            settings.heartbeat.secret_key,
            broadcaster,
            logger
            )
        server.start()
        threads.append(server)

    if (settings.heartbeat.enable_hwmonitor):
        logger.info("Bringing up monitoring subsystem")
        monitors = load_monitors(settings.heartbeat.monitors)
        monitorPool = concurrent.futures.ThreadPoolExecutor(
                max_workers=len(settings.heartbeat.monitors)
                    )
        hwmon = MonitorHandler(
                monitors,
                dispatcher.put_event,
                monitorPool,
                logger
                )
        hwmon.start()
        threads.append(hwmon)

    return threads


if __name__ == "__main__":
    threads = main()

    try:
        #threads = [t.join(1) for t in threads if t is not None and t.isAlive()]
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down heartbeat")
        for t in threads:
            t.shutdown = True

        print("Shutdown request sent, exiting in 5 seconds")
        time.sleep(5)
        os._exit(0)