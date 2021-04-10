from multiprocessing import Process, Pipe, freeze_support
from gui import GUI
from snapshoter import Snapshoter


def doing_snapshoter_work(snapshoter):
    snapshoter.find_maple_window()
    snapshoter.picture_loop()


if __name__ == "__main__":
    freeze_support()
    pipe_con1, pipe_con2 = Pipe()

    snapshoter = Snapshoter(pipe_con1)
    gui = GUI(pipe_con2)

    snapshoter_proc = Process(target=doing_snapshoter_work, args=(snapshoter,))
    snapshoter_proc.start()

    gui.run_gui()
    snapshoter_proc.join()

