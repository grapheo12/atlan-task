from app.threadManager import ThreadManager

tm = ThreadManager()

class Data:
    counter : int

@tm.pausableTask(Data)
def count(ref):
    ref.output.counter = ref.args[0]
    while True:
        if ref.status == "RUN":
            ref.output.counter += 1
        elif ref.status == "TERM":
            break

def test():
    c = count(2)
    c.start()

    while True:
        x = input(">>> ")
        if x == "s":
            print(tm.refs[0].output.counter)
        elif x == "p":
            tm.refs[0].pause()
        elif x == "r":
            tm.refs[0].resume()
        elif x == "t":
            tm.refs[0].terminate()
        else:
            break

    print("Bye")