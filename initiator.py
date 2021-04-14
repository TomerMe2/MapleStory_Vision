from multiprocessing import Process, Pipe, freeze_support

from drops_snapshoter import DropsSnapshoter
from gui import GUI
from pots_snapshoter import PotsSnapshoter


def doing_snapshoter_work(snapshoter):
    snapshoter.picture_loop()


if __name__ == "__main__":
    freeze_support()
    pipe_pots1, pipe_pots2 = Pipe()
    pipe_drops1, pipe_drops2 = Pipe()

    pots_snapshoter = PotsSnapshoter(pipe_pots1)
    drops_snapshoter = DropsSnapshoter(pipe_drops1)
    gui = GUI([pipe_pots2, pipe_drops2])

    snapshoter_proc = Process(target=doing_snapshoter_work, args=(pots_snapshoter,))
    snapshoter_proc.start()

    drops_snapshoter_proc = Process(target=doing_snapshoter_work, args=(drops_snapshoter,))
    drops_snapshoter_proc.start()

    gui.run_gui()
    snapshoter_proc.join()
    drops_snapshoter_proc.join()
