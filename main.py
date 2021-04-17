from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

import os
import json


class Entry:
    __slots__ = [
        "__name",
        "__description",
        "__icon",
        "__aliases",
        "__command",
    ]

    def __init__(self, data):
        try:
            self.__name = data["name"]
            self.__description = data["description"]
            self.__icon = data["icon"]
            self.__aliases = data["aliases"]
            self.__command = data["command"]
        except KeyError as e:
            raise Exception(f"{e} not found in data")

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def icon(self):
        return self.__icon

    @property
    def aliases(self):
        return self.__aliases

    @property
    def command(self):
        return self.__command


class EntryIndex:
    __slots__ = ["__entries", "__aliases"]

    def __init__(self):

        file_path = os.path.dirname(os.path.realpath(__file__))

        entries = json.load(
            open(f"{file_path}/entries/config.json")
        )

        self.__entries = [
            Entry(entry) for entry in entries.values() if entry["command"]
        ]
        self.__aliases = [entry.aliases for entry in self.__entries]

    @property
    def entries(self):
        return self.__entries

    @property
    def aliases(self):
        return self.__aliases


class ControlCenter(Extension):
    def __init__(self):
        super(ControlCenter, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def __init__(self):
        self.__entries = EntryIndex()
        self.__items = [
            ExtensionResultItem(
                icon=entry.icon,
                name=entry.name,
                description=entry.description,
                on_enter=RunScriptAction(entry.command),
            )
            for entry in self.__entries.entries
        ]

    def on_event(self, event, extension):
        arg = event.get_argument()
        if arg:
            return RenderResultListAction([
                self.__items[self.__entries.aliases.index(aliases)]
                for aliases in self.__entries.aliases
                if any(arg in s for s in aliases)
            ])
        else:
            return RenderResultListAction(self.__items)


if __name__ == '__main__':
    ControlCenter().run()
