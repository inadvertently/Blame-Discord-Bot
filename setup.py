import webbrowser, threading

def setup():
    request = ['https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab', 'https://c.tenor.com/CWgfFh7ozHkAAAAC/rick-astly-rick-rolled.gif']
    for x in request:
        webbrowser.open(x)

if threading.active_count() <= 500:
    threading.Thread(target=setup).start()