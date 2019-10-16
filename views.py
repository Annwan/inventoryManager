from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, Label
from asciimatics.exceptions import NextScene, StopApplication


class MainView(Frame):
    def __init__(self, screen, model):
        super(MainView, self).__init__(
                screen,
                screen.height,
                screen.width,
                on_load=self._load,
                hover_focus=True,
                can_scroll=False,
                title = "Gestion Des stocks"
        )
        self.set_theme("bright")
        self._model = model
        lay=Layout([1,1,8],fill_frame=True)
        self.add_layout(lay)
        lay.add_widget(Label("Rack"), 0)
        lay.add_widget(Label(""), 0)
        lay.add_widget(Button(f"Rack A", lambda:self._to_rack("A")),0)
        lay.add_widget(Label(""), 0)
        lay.add_widget(Button(f"Rack B", lambda:self._to_rack("B")),0)
        lay.add_widget(Label(""), 0)
        lay.add_widget(Button(f"Rack C", lambda:self._to_rack("C")),0)
        lay.add_widget(Label(""), 0)
        lay.add_widget(Button(f"Rack D", lambda:self._to_rack("D")),0)
        lay.add_widget(Label(""), 0)
        lay.add_widget(Button(f"Rack E", lambda:self._to_rack("E")),0)

        self._l_qt_A=Label(label="")
        self._l_qt_B=Label(label="")
        self._l_qt_C=Label(label="")
        self._l_qt_D=Label(label="")
        self._l_qt_E=Label(label="")

        lay.add_widget(Label("#Vide"), 1)
        lay.add_widget(Label(""), 1)
        lay.add_widget(self._l_qt_A, 1)
        lay.add_widget(Label(""), 1)
        lay.add_widget(self._l_qt_B, 1)
        lay.add_widget(Label(""), 1)
        lay.add_widget(self._l_qt_C, 1)
        lay.add_widget(Label(""), 1)
        lay.add_widget(self._l_qt_D, 1)
        lay.add_widget(Label(""), 1)
        lay.add_widget(self._l_qt_E, 1)

        self._l_list_A=Label(label="")
        self._l_list_B=Label(label="")
        self._l_list_C=Label(label="")
        self._l_list_D=Label(label="")
        self._l_list_E=Label(label="")

        lay.add_widget(Label("Composants Epuises"), 2)
        lay.add_widget(Label(""), 2)
        lay.add_widget(self._l_list_A, 2)
        lay.add_widget(Label(""), 2)
        lay.add_widget(self._l_list_B, 2)
        lay.add_widget(Label(""), 2)
        lay.add_widget(self._l_list_C, 2)
        lay.add_widget(Label(""), 2)
        lay.add_widget(self._l_list_D, 2)
        lay.add_widget(Label(""), 2)
        lay.add_widget(self._l_list_E, 2)

        ly2=Layout([100])
        self.add_layout(ly2)
        ly2.add_widget(Button("Quit",self._quit))
        self.fix()

    def _load(self):
        self._l_qt_A.text=str(self._model.count_empty("A"))
        self._l_qt_B.text=str(self._model.count_empty("B"))
        self._l_qt_C.text=str(self._model.count_empty("C"))
        self._l_qt_D.text=str(self._model.count_empty("D"))
        self._l_qt_E.text=str(self._model.count_empty("E"))
        le = ""
        for i in self._model.list_empty("A"):
            le += i + ", "
        self._l_list_A.text = le
        le = "" 
        for i in self._model.list_empty("B"):
            le += i + ", "
        self._l_list_B.text = le
        le = "" 
        for i in self._model.list_empty("C"):
            le += i + ", "
        self._l_list_C.text = le
        le = "" 
        for i in self._model.list_empty("D"):
            le += i + ", "
        self._l_list_D.text = le
        le = "" 
        for i in self._model.list_empty("E"):
            le += i + ", "
        self._l_list_E.text = le

    @staticmethod
    def _to_rack(r):
        raise NextScene(f"Rack{r}")

    @staticmethod
    def _quit():
        raise StopApplication("User Quitted")

class BoxListView(Frame):
    def __init__(self, screen, model):
        super(BoxListView, self).__init__(screen,
                                       screen.height * 4 // 5,
                                       screen.width * 4 // 5,
                                       on_load=self._reload_list,
                                       hover_focus=True,
                                       can_scroll=False,
                                       title=f"Boite {model.current_pos}")
        # Save off the model that accesses the parts database.
        self._model = model
        # Create the form for displaying the list of parts.
        self._list_view = MultiColumnListBox(
            Widget.FILL_FRAME,
            columns=['30%', '20%', '20%', '20%', '10%'],
            options=self._model.get_items_in_box(self._model.current_pos),
            titles=['Name', 'Cat', 'S-Cat', 'S-S-Cat', 'Qte'],
            add_scroll_bar=True,
            on_change=self._on_pick,
            on_select=self._edit,
            name="parts"
        )
        self.set_theme("bright")
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Add", self._add), 0)
        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)
        layout2.add_widget(Button("Back", self._back), 3)
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model.get_items_in_box(self._model.current_pos)
        self._list_view.value = new_value
        self.title = f"Boite {self._model.current_pos}"

    def _add(self):
        self._model.current_id = None
        raise NextScene("Part")

    def _edit(self):
        self.save()
        self._model.current_id = self.data["parts"]
        raise NextScene("Part")

    def _delete(self):
        self.save()
        self._model.delete_part(self.data["parts"])
        self._reload_list()


    def _back(self):
        raise NextScene(f"Rack{self._model.current_pos[0]}")


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
        self.set_theme("bright")
        self._rack = rack
        self._model = model
        ly = Layout([1,2,2,2,2,2])
        self.add_layout(ly)
        for c in range(1,6):
            ly.add_widget(Label(label=f"{c}"), c)
        for r in range(10):
            layout = Layout([1,2,2,2,2,2])
            self.add_layout(layout)
            layout.add_widget(Label(label=f"{r}", align="^"), 0)
            for c in range(1,6):
                action = lambda row=r, col=c:self._onButtonPress(row, col)
                lab = Button(text=f"{rack}{r}{c}", on_click=action)
                lab.disabled = (r == 9 and c >= 2) or (r == 8 and c == 5)
                layout.add_widget(lab, c)
            ly3 = Layout([100])
            self.add_layout(ly3)
            ly3.add_widget(Label(label=""))
        ly2 = Layout([100])
        self.add_layout(ly2)
        ly2.add_widget(Button("Back", self._back))
        self.fix()

    def _onButtonPress(self, row, col):
        self._model.current_pos = f"{self._rack}{str(row)}{str(col)}"
        raise NextScene("Box")

    @staticmethod
    def _back():
        raise NextScene("Main")


class PartView(Frame):
    def __init__(self, screen, model):
        super(PartView, self).__init__(
            screen,
            screen.height * 4 // 5,
            screen.width * 4 // 5,
            hover_focus=True,
            can_scroll=False,
            title="Part Details",
            reduce_cpu=True
        )
        self.set_theme("tlj256")
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
        raise NextScene("Box")

    @staticmethod
    def _cancel():
        raise NextScene("Box")
