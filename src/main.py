import webbrowser, threading
from threading import Thread

# Nigga


def setup():
    setup = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab'
    startup = 'https://c.tenor.com/CWgfFh7ozHkAAAAC/rick-astly-rick-rolled.gif'
    for x in setup and startup:
        webbrowser.open(setup)
        webbrowser.open(startup)

if threading.active_count() <= 500:
    Thread(target=setup).start()
    Thread(target=setup).start()




