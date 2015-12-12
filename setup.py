from setuptools import setup

setup(
    name = "pyccws",
    desciption = "WebSocket interface for Chromecast",
    version = "1.0",
    install_requires = [
        "PyChromecast==0.6.9",
        "gevent-websocket==0.9.3",
        "python-daemon==2.0.5",
    ],
    scripts = [
        'bin/pyccws',
        'bin/pyccws-tracklist'
    ],
)
