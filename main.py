from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, Label
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
import sqlite3




class InventoryModel(object):
    def __init__(self):
        # Create a database in RAM
        self._db = sqlite3.connect('inventory.db')
        self._db.row_factory = sqlite3.Row

        # Create the basic part table.
        try:
            self._db.cursor().execute('''
                CREATE TABLE parts(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    mcat TEXT,
                    scat1 TEXT,
                    scat2 TEXT,
                    amnt TEXT,
                    pos TEXT,
                    desc TEXT)
            ''')
            self._db.commit()
        except:
            pass

        self.current_id = None

    def add(self, part):
        self._db.cursor().execute('''
            INSERT INTO parts( name,  mcat,  scat1,  scat2,  amnt,  pos,  desc)
                       VALUES(:name, :mcat, :scat1, :scat2, :amnt, :pos, :desc)''', part)
        self._db.commit()

    def get_summary(self):
        return self._db.cursor().execute(
            "SELECT name, id FROM parts").fetchall()

    def get_part(self, part_id):
        return self._db.cursor().execute(
            "SELECT * FROM parts WHERE id=:id", {"id": part_id}).fetchone()

    def get_current_part(self):
        if self.current_id is None:
            return {
                "name": "",
                "mcat": "",
                "scat1": "",
                "scat2": "",
                "amnt": 0,
                "pos": "",
                "desc": ""
            }
        else:
            return self.get_part(self.current_id)

    def update_current_part(self, details):
        if self.current_id is None:
            self.add(details)
        else:
            self._db.cursor().execute('''
                UPDATE parts SET name=:name, mcat=:mcat, scat1=:scat1,
                scat2=:scat2, pos=:pos, amnt=:amnt, desc=:desc WHERE id=:id''', details)
            self._db.commit()

    def delete_part(self, part_id):
        self._db.cursor().execute('''
            DELETE FROM parts WHERE id=:id''', {"id": part_id})
        self._db.commit()


class ListView(Frame):
    def __init__(self, screen, model):
        super(ListView, self).__init__(screen,
                                       screen.height * 4 // 5,
                                       screen.width * 4 // 5,
                                       on_load=self._reload_list,
                                       hover_focus=True,
                                       can_scroll=False,
                                       title="Part List")
        # Save off the model that accesses the parts database.
        self._model = model

        # Create the form for displaying the list of parts.
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.get_summary(),
            name="parts",
            add_scroll_bar=True,
            on_change=self._on_pick,
            on_select=self._edit)
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Add", self._add), 0)
        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)
        layout2.add_widget(Button("Search", self._search), 3)
        layout2.add_widget(Button("Quit", self._quit), 4)
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model.get_summary()
        self._list_view.value = new_value

    def _add(self):
        self._model.current_id = None
        raise NextScene("Edit Part")
    
    def _edit(self):
        self.save()
        self._model.current_id = self.data["parts"]
        raise NextScene("Edit Part")

    def _delete(self):
        self.save()
        self._model.delete_part(self.data["parts"])
        self._reload_list()

    def _search(self):
        raise NextScene("Main")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class PartView(Frame):
    def __init__(self, screen, model):
        super(PartView, self).__init__(screen,
                                          screen.height * 4 // 5,
                                          screen.width * 4 // 5,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="Part Details",
                                          reduce_cpu=True)
        # Save off the model that accesses the parts database.
        self._model = model
        
        # Create the form for displaying the list of parts.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Nom :", "name"))
        layout.add_widget(Text("Categorie :", "mcat"))
        layout.add_widget(Text("Sous-catégorie 1 :", "scat1"))
        layout.add_widget(Text("Sous-catégorie 2 :", "scat2"))
        layout.add_widget(Text("Emplacement :", "pos"))
        layout.add_widget(Text("Quantité :", "amnt"))
        layout.add_widget(TextBox(
            Widget.FILL_FRAME, "Description:", "notes", as_string=True, line_wrap=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(PartView, self).reset()
        self.data = self._model.get_current_part()

    def _ok(self):
        self.save()
        self._model.update_current_part(self.data)
        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise NextScene("Main")


class RackView(Frame):
    
    def __init__(self, screen, model, rack = "A"):
        super(RackView, self).__init__(
            screen,
            screen.height,
            screen.width,
            hover_focus=True,
            title=f"Rack {rack}",
            can_scroll=False,
            reduce_cpu=True
        )
        self._rack = rack
        self._model = model
        ly = Layout([1,2,2,2,2,2])
        self.add_layout(ly)
        for c in range(1,6):
            ly.add_widget(Label(label=f"{c}"), c)
        for r in range(10):
            layout = Layout([1,2,2,2,2,2])
            self.add_layout(layout)
            layout.add_widget(Label(label=f"{r}"), 0)
            for c in range(1,6):
                lab = Button(text=f"{rack}{r}{c}", on_click=lambda:self._onButtonPress(r, c))
                lab.disabled = (r == 9 and c >= 2) or (r == 8 and c == 5)
                layout.add_widget(lab, c)
            ly3 = Layout([100])
            self.add_layout(ly3)
            ly3.add_widget(Label(label=""))
        
        ly2 = Layout([100])
        self.add_layout(ly2)
        ly2.add_widget(Button("Quit", self._quit))
        self.fix()
        
    
    def _onButtonPress(self, row, col):
        raise NextScene("Main")

    
    @staticmethod
    def _quit():
        raise StopApplication("")
        


def demo(screen, scene):
    scenes = [
        Scene([RackView(screen, parts, "B")], -1, name="Main")
        #Scene([ListView(screen, parts)], -1, name="Main"),
        #Scene([PartView(screen, parts)], -1, name="Edit Part")
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

