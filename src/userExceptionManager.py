# -*- coding: utf-8 -*-
# 
import re #TODO: Are you using this? 
import json
from os.path import join, exists
from shutil import copyfile #TODO: Are you using this?
from typing import Union 

from aqt.addcards import AddCards  #TODO: Are you using this? 
from aqt.qt import QSortFilterProxyModel, QAbstractItemModel, QAbstractTableModel, QModelIndex, QLabel, QWidget, QProgressBar, QIcon, Qt
from aqt.editor import Editor
from anki.find import Finder
from anki.utils import is_mac

from . import Pyperclip #TODO: Are you using this? 
from .addgui import Ui_Form
from .miutils import miInfo, miAsk

class OgOvFilter(QSortFilterProxyModel):
    """
    Provides filtering and sorting functionality for a source model.
    
    Methods:
    - set_filter_by_column(self, str_to_compare): Sets the filter string for the column to be filtered.
    - ascending_order(self): Sorts the rows in ascending order based on the length of the original and overwrite values.
    - test_data(self, text): Filters the rows based on the filter string and updates the source model's data.
    - save_list(self, path): Saves the filtered and sorted data to a file.
    """

    def __init__(self, model: QAbstractItemModel, parent=None):
        super().__init__(parent)
        self.setSourceModel(model)
        self.insertRows = model.insertRows
        self.str_to_compare = ''

    def set_filter_by_column(self, str_to_compare: str):
        self.str_to_compare = str_to_compare
        self.invalidateFilter()

    def ascending_order(self):
        self.sourceModel().ue_list = sorted(self.sourceModel().ue_list)

    def test_data(self, text: str):
        """
        Filters the rows based on the filter string and updates the source model's data.

        Args:
        - text: The filter string to be used for filtering.
        """
        text = text.lower()
        found_original = []
        found_overwrite = []
        not_found = []

        for original, overwrite in self.sourceModel().ue_list:
            if text in original.lower():
                found_original.append([original, overwrite])
            elif text in overwrite.lower():
                found_overwrite.append([original, overwrite])
            else:
                not_found.append([original, overwrite])

        found_original.sort(key=lambda x: len(x[0]))
        found_overwrite.sort(key=lambda x: len(x[1]))

        self.sourceModel().ue_list = found_original + found_overwrite + not_found

    def save_list(self, path: str):
        ue_list = self.sourceModel().ue_list
        self.sourceModel().mng.ue_list = ue_list

        with open(path, "w", encoding="utf-8") as outfile:
            json.dump(ue_list, outfile, ensure_ascii=False)


class RulesModel(QAbstractTableModel):
    """
    Main functionalities:
    - Provides the data for a table view with two columns: "Original" and "Overwrite".
    - Controls the display of the table view.
    - Allows filtering and sorting of the data.
    - Saves the filtered and sorted data to a file.

    Methods:
    - rowCount(self, index=QModelIndex()): Returns the number of rows in the model.
    - data(self, index, role=Qt.ItemDataRole.DisplayRole): Returns the data for a given index and role.
    - removeRows(self, position, rows=1, index=QModelIndex()): Removes rows at the specified position. Returns True if successful, False otherwise.
    - setData(self, index, value, role=Qt.ItemDataRole.EditRole, over__write_rule__=False, ruleDict=None): Sets the data in the cell at the specified index with the given value. Returns True if successful, False otherwise.

    Fields:
    - ue_list: The list of data to be displayed in the table view.
    - mng: The manager object associated with the model.
    - gui: The GUI object associated with the model.
    """

    def __init__(self, ue_list, manager, gui, parent=None):
        super().__init__(parent)
        self.ue_list = ue_list
        self.mng = manager
        self.gui = gui
        
    def __rule_is_valid__(self, value: str, rule: str) -> bool:
        if value == rule:
            miInfo('The original text and overwrite text cannot be the same.')
            return False
        elif not value:
            miInfo('A rule must be at least one character long.')
            return False
        
        return True

    #TODO: Do we need index?
    def rowCount(self, index=QModelIndex()) -> int:
        return len(self.ue_list)
    
    #TODO: Do we need index?
    #TODO: No magic number
    def columnCount(self, index=QModelIndex()) -> int:
        return 2

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Union[str, None]:
        if not index.isValid() or index.row() >= len(self.ue_list) or role not in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            return None

        original, overwrite = self.ue_list[index.row()]
        return original if index.column() == 0 else overwrite

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> Union[str, int, None]:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return "Original"
            elif section == 1:
                return "Overwrite"
            
        return section + 1 if orientation == Qt.Orientation.Vertical else None

    #TODO: Do we need index?
    def insertRows(self, position=False, rows=1, index=QModelIndex(), original=False, overwrite=False) -> bool:
        if not position:
            position = self.row_count()
            
        self.beginInsertRows(QModelIndex(), position, position)
        
        for row in range(rows):       
            if original and overwrite:
                self.ue_list.insert(position + row, [original, overwrite])
                
        self.endInsertRows()
        self.mng.save_ue_list()
        return True

    #TODO: Do we need index?
    def removeRows(self, position: int, rows=1, index=QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.ue_list[position:position+rows]
        self.endRemoveRows()
        self.mng.save_ue_list()
        return True

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole, overwrite_rule=False, rule_dict=None) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        if overwrite_rule and rule_dict['row'] < len(self.ue_list):
            rule = self.ue_list[rule_dict['row']]
            rule[0] = rule_dict['og']
            rule[1] = rule_dict['ov']
            self.mng.save_ue_list()
            return True

        if not index.isValid() or index.row() >= len(self.ue_list):
            return False

        rule = self.ue_list[index.row()]
        column = index.column()

        if column == 0 and self.__rule_is_valid__(value, rule[1]) and value != rule[0] and not self.mng.rule_exists(value, True):
            rule[0] = value
        elif column == 1 and self.__rule_is_valid__(value, rule[0]) and value != rule[1]:
            rule[1] = value
        else:
            return False

        self.mng.save_ue_list()
        self.dataChanged.emit(index, index)
        self.gui.openApplyRuleInquiry([[rule[0], rule[1]]])
        return True
             
    def flags(self, index: QModelIndex) -> Union[Qt.ItemFlag, QAbstractTableModel]:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        
        return QAbstractTableModel.flags(self, index) | Qt.ItemFlag.ItemIsEditable


class UserExceptionManager:
    """
    Main functionalities:
    - Adding, editing, and applying user-defined exception rules to flashcards
    - Importing and exporting lists of exception rules from/to files

    Methods:
    - open_add_menu(self, editor=False, text=False): Opens a menu for adding rules.
    - get_ue_list(self): Gets the User Exception (UE) list.
    - setup_model(self, gui): Sets up a model for displaying the User Exception (UE) List in a table view.
    - add_rule(self, original, overwrite, new_cards, learned_cards, parent_widget, add_menu=False): Adds a new rule to the User Exception (UE) List.
    - rule_exists(self, original, message=False): Check if a rule with the given original value already exists.
    - apply_rules(self, rule_list, new_cards, learned_cards, parent_widget, notes=False, message=False): Applies the exception rules to the flashcards based on the specified criteria.
    - apply_rules_to_text(self, text): Applies the rules in the ue_list to the given text.
    - save_ue_list(self): Saves the list of rules to a file. If a model is set, the list is saved using the model's saveList method. Otherwise, the list is saved to a file using the json.dump function.
    - import_ue_list(self, file_name, combine, overwrite_collides): Imports a list of exception rules from a file, optionally combining or overwriting existing rules.
    - export_ue_list(self, file_name): Exports the list of exception rules to a file.

    Fields:
    - mw: The main window object of Anki.
    - addon_path: The path to the addon.
    - list_path: The path to the file where the exception rules are stored.
    - active_fields: A dictionary containing the active fields for each note type.
    - model: The model used for filtering and sorting the exception rules.
    - ue_list: The list of user-defined exception rules.
    """

    def  __init__(self,mw, addon_path):
        self.mw = mw
        self.addon_path = addon_path
        self.list_path = False 
        self.active_fields = False
        self.model = False

    def __get_list_path__(self) -> str:
        return join(self.mw.col.media.dir(), '_userExceptionList.json')

    def __update_count__(self, counter: QLabel):
        counter.setText(f'Rule Count: {len(self.ue_list)}')
        
    def __set_add_menu_widget__(self, editor: bool) -> QWidget:
        if editor:
            return QWidget(editor.web) if isinstance(editor, Editor) else QWidget(editor)

        return QWidget(self.mw)
    
    def __add_rule_clear_text__(self):
        if self.add_rule(self.add_menu.ui.originalLE.text(), self.add_menu.ui.overwriteLE.text(), self.add_menu.ui.ncAddCB.isChecked(), self.add_menu.ui.lcAddCB.isChecked(), self.add_menu, True):
            self.add_menu.ui.originalLE.clear()
            self.add_menu.ui.overwriteLE.clear()
            
    def __load__ue_list_from_json__(self):
        with open(self.list_path, "r", encoding="utf-8") as list_file:
            return json.load(list_file)
        
    def __write_rule__(self, original: str, overwrite: str):
        if self.model:
            self.model.insertRows(original=original, overwrite=overwrite)
        else:
            self.ue_list.append([original, overwrite])
            
        self.save_ue_list()
        
    def __get_active_fields__(self) -> dict:
        active_fields_config = self.__get_config__()['Active_fields']
        active_fields = {}
        
        for af in active_fields_config:
            split_af = af.split(';')
            note_type = split_af[2]
            field = split_af[4]
            
            active_fields.setdefault(note_type, []).append(field)
                
        return active_fields
    
    def __get_all_notes__(self) -> list:
        return Finder(self.mw.col).findNotes('')
    
    def __card_meets_criteria__(self, cards: list, new_cards: bool, learned_cards: bool) -> bool:
        return any(
            (card.type == 0 and new_cards)
            or ((card.type in [1, 2]) and learned_cards)
            for card in cards
        )
        
    def __get_progress_widget__(self, parent_widget, title: str) -> tuple[QWidget, QProgressBar]:
        progress_widget = QWidget(parent_widget, Qt.WindowType.Window)
        progress_widget.setWindowTitle(title)
        progress_widget.setFixedSize(400, 70)
        progress_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        bar = QProgressBar(progress_widget)       
        bar.setFixedSize(380 if is_mac else 390, 50)            
        bar.move(10,10)
        
        per = QLabel(bar)
        per.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        progress_widget.show()
        return progress_widget, bar
    
    def __apply_rules_to_field__(self, notes: list, checkpointed: bool, new_cards: bool, learned_cards: bool, rule_list: list[tuple[str, str]], bar: QProgressBar) -> tuple[int, int]:
        altered = 0
        applied_rules = 0
        
        for it, nid in enumerate(notes, start=1):
            note = self.mw.col.get_note(nid)
            already_altered = False

            if not self.__card_meets_criteria__(note.cards(), new_cards, learned_cards):
                continue

            note_type = note.note_type()

            if note_type['name'] in self.active_fields:
                fields = self.mw.col.models.field_names(note.note_type())

                for field in fields:
                    if field not in self.active_fields[note_type['name']]:
                        continue
                    
                    for original, overwrite in rule_list:
                        if original not in note[field]:
                            continue
                        
                        if not already_altered:
                            altered += 1

                        if not checkpointed:
                            self.mw.checkpoint('Overwrite Rule Application')
                            checkpointed = True

                        already_altered = True
                        applied_rules += 1
                        note[field] = note[field].replace(original, overwrite)

            bar.setValue(it)
            self.mw.app.processEvents()
            
            return altered, applied_rules
        
    def __get_config__(self):
        return self.mw.addonManager.getConfig(__name__)   

    def open_add_menu(self, editor=False, text=False):
        self.add_menu = self.__set_add_menu_widget__(editor)            
        self.add_menu.setWindowIcon(QIcon(join(self.addon_path, 'icons', 'migaku.png')))
        self.add_menu.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.add_menu.ui = Ui_Form()
        self.add_menu.ui.setupUi(self.add_menu)
        self.__update_count__(self.add_menu.ui.listCount)
        
        if not text and editor:
            text = editor.web.selectedText()
            
        if text:
            self.add_menu.ui.originalLE.setText(text)
            self.add_menu.ui.overwriteLE.setFocus()
            
        self.add_menu.show()
        self.add_menu.ui.addRuleButton.clicked.connect(self.__add_rule_clear_text__)      

    def get_ue_list(self):
        self.list_path = self.__get_list_path__()
        self.active_fields = False
        self.ue_list = self.__load__ue_list_from_json__() if exists(self.list_path) else []

    def setup_model(self, gui):
        self.proxyFilter = OgOvFilter(RulesModel(self.ue_list, self, gui))
        self.model = self.proxyFilter
        self.proxyFilter.setFilterKeyColumn(0)

    def add_rule(self, original: str, overwrite: str, new_cards: bool, learned_cards: bool, parent_widget, add_menu=False) -> tuple[bool, Union[bool, int]]:
        """
        Adds a new rule to the User Exception (UE) List.

        Args:
            original (str): The original text for the rule.
            overwrite (str): The text to overwrite the original text.
            newCards (bool): Indicates whether the rule should be applied to new cards.
            learnedCards (bool): Indicates whether the rule should be applied to learned cards.
            parentWidget (object): The parent widget for displaying messages.
            add_menu (bool, optional): Indicates whether the rule should be added to a menu. Defaults to False.

        Returns:
            A tuple containing two elements:
                - bool: True if the rule was successfully added or updated, False otherwise.
                - bool or int: False if the original or overwrite fields are empty, or if the original and overwrite fields contain the same text. The ID of the existing rule if it was overwritten.
        """
        if not original or not overwrite:
            miInfo('The original and overwrite fields should not be empty.', level='not')
            return False, False
        
        if original == overwrite:
            miInfo('The original and overwrite fields should not contain the same text.', level='not')
            return False, False
        
        found_id = self.rule_exists(original)
        edit = False
        
        if found_id:
            if not miAsk(f'The rule "{original}" => "{self.ue_list[found_id][1]}" already overwrites the given text. Would you like to overwrite it with your new rule?'):
                return False, False

            edit = True
        
        if edit:
            self.model.setData(None, None, Qt.ItemDataRole.EditRole, True, {'row': found_id, 'og': original, 'ov': overwrite})
        else:
            self.__write_rule__(original, overwrite)
            
        if add_menu:
            self.__update_count__(self.add_menu.ui.listCount)

        if new_cards or learned_cards:
            self.apply_rules([[original, overwrite]],  new_cards, learned_cards, parent_widget) 

        return True, found_id

    def rule_exists(self, original: str, message=False) -> Union[int, bool]:
        """
        Check if a rule with the given original value already exists.

        Args:
            original (str): The original value of a rule.
            message (bool, optional): Whether to display an error message if the rule exists. Defaults to False.

        Returns:
            int or bool: The index of the rule if it exists, otherwise False.
        """
        for idx, ogOv in enumerate(self.ue_list):
            if original == ogOv[0]:
                if message:
                    miInfo(
                        f'A rule with this original value already exists ("{original}" => "{self.ue_list[idx][1]}""), please ensure that you are defining a unique value.',
                        level='err',
                    )
                return idx
            
        return False

    def apply_rules(self, rule_list: list[tuple[str, str]], new_cards: bool, learned_cards: bool, parent_widget, notes: [list] = None, message: [bool] = False):
        self.active_fields = self.__get_active_fields__()

        if notes is None:
            notes = self.__get_all_notes__()

        checkpointed = False
        prog_wid, bar = self.__get_progress_widget__(parent_widget, 'Applying Overwrite Rule(s)...')
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        
        altered, applied_rules = self.__apply_rules_to_field__(notes, checkpointed, new_cards, learned_cards, rule_list, bar)          

        self.mw.reset()
        prog_wid.hide()
        
        if message:
            miInfo(
                f'Rule(s) have been applied {str(applied_rules)} times.<br>{str(altered)} notes have been altered.',
                parent=parent_widget,
                level='not',
            )  
    
    def apply_rules_to_text(self, text: str) -> str:
        for original, overwrite in self.ue_list:
            if original in text:
                text = text.replace(original, overwrite)
                
        return text          

    def save_ue_list(self):
        if not self.model: 
            with open(self.list_path, "w", encoding="utf-8") as outfile:
                json.dump(self.ue_list, outfile, ensure_ascii=False) 
        else:
            self.model.save_list(self.list_path)

    def import_ue_list(self, file_name: str, combine: bool, overwrite_collides: bool) -> Union[list[int, int], bool]:
        """
        Imports a new list of rules from a file.

        The new list can be combined with the existing list, and colliding rules can be overwritten based on the combine and overwriteCollides flags.

        Args:
            fileName (str): The name of the file from which the new list of rules will be imported.
            combine (bool): A flag indicating whether the new list of rules should be combined with the existing list.
            overwriteCollides (bool): A flag indicating whether colliding rules should be overwritten.

        Returns:
            list: A list containing the total number of imported rules and the number of ignored or overwritten rules.
            False: If the overwrite rules list could not be imported.
        """
        try:
            with open(file_name, "r", encoding="utf-8") as imported_list:
                new_list = json.load(imported_list)

            if not combine:
                self.model.sourceModel().ue_list = new_list
                self.save_ue_list()

                return [len(self.ue_list), 0]

            temp_ue_list = self.model.sourceModel().ue_list.copy()
            dict_ue_list = dict(temp_ue_list)
            total_imported = 0
            ignored_or_overwritten = 0

            for original, overwrite in new_list:
                if not original or not overwrite or not isinstance(original, str) or not isinstance(overwrite, str):
                    miInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', level='err')
                    return False
                
                if original in dict_ue_list:
                    ignored_or_overwritten += 1
                    
                    if overwrite_collides:
                        temp_ue_list.remove([original, dict_ue_list[original]])
                        
                if overwrite_collides or original not in dict_ue_list:
                    temp_ue_list.append([original, overwrite])
                    total_imported += 1    
                    
            self.model.sourceModel().ue_list = temp_ue_list
            self.save_ue_list()

            return [total_imported, ignored_or_overwritten]       

        except Exception:
            miInfo('The overwrite rules list could not be imported. Please make sure the target file is a valid overwrite rules list and try again.', level='err')
            return False

    def export_ue_list(self, file_name: str):
        if not file_name.endswith('.json'):
            file_name += '.json'
            
        with open(file_name, 'w', encoding='utf-8') as outfile:
            json.dump(self.ue_list, outfile, ensure_ascii=False)
            
        miInfo(f'The overwrite rules list has been exported to "{file_name}"', level='not')
