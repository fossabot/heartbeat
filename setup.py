#!/usr/bin/env python

from distutils.core import setup
import sys

install_requires = ['pymlconf', 'pyyaml']
suggested = {
    'Pushbullet': ["pushbullet.py >= 0.5"],
    'Blinkstick': ["blinkstick >= 1.1.6"]
        }

if (sys.version_info < (3, 4)):
    install_requires.append('enum34')

setup(name='Heartbeat',
    version='2.4.0',
    description='Heartbeat monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    requires=install_requires,
    package_dir={'':'src'},
    packages=[
        'heartbeat',
        'heartbeat.modules',
        'heartbeat.network',
        'heartbeat.monitoring',
        'heartbeat.notifications',
        'heartbeat.platform',
        'heartbeat.multiprocessing'
        ],
    data_files=[
        ('etc/heartbeat', ['dist/_etc/heartbeat/heartbeat.conf']),
        ('etc/heartbeat', ['dist/_etc/heartbeat/monitoring.conf']),
        ('etc/heartbeat', ['dist/_etc/heartbeat/notifying.conf'])
        ]
    )

