from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import sys

from model import InventoryModel
from views import BoxListView, RackView, PartView#, MainView


def demo(screen, scene):
    scenes = [
        #Scene([MainView(screen, parts)], -1, name="Main"),
        Scene([RackView(screen, parts, "A")], -1, name="RackA"),
        Scene([RackView(screen, parts, "B")], -1, name="RackB"),
        Scene([RackView(screen, parts, "C")], -1, name="RackC"),
        Scene([RackView(screen, parts, "D")], -1, name="RackD"),
        Scene([RackView(screen, parts, "E")], -1, name="RackE"),
        Scene([BoxListView(screen, parts)], -1, name="Box"),
        #Scene([ListAllView(screen, parts)], -1, name="List"),
        Scene([PartView(screen, parts)], -1, name="Part")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

if __name__ == "__main__":
    parts = InventoryModel()
    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

