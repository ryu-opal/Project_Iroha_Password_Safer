import sys
import os
import json
from cryptography.fernet import Fernet
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QListWidget, QListWidgetItem, 
                               QFrame, QMessageBox, QStackedWidget, QComboBox, 
                               QGraphicsOpacityEffect, QFileDialog, QSlider) 
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve 


SETTINGS_FILE = "settings.txt"
DATA_FILE = "passwords.json" 
KEY_FILE = "secret.key"      

class PasswordManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iroha Password Safer")
        self.resize(600, 600)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("main_bg")
        
        self.main_page = QWidget()
        self.main_page.setObjectName("transparent_page") 
        main_layout = QHBoxLayout()

        self.left_frame = QFrame()
        self.left_frame.setObjectName("glass_box") 
        left_side = QVBoxLayout(self.left_frame) 
        
        # search function 
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Your Password")
        self.search_input.textChanged.connect(self.filter_list) 
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Name", "URL"])
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_type)

# encode password 
        self.passwords_data = {} 
        self.load_or_create_key() 


        sort_layout = QHBoxLayout()
        sort_az = QPushButton("A-Z")
        sort_za = QPushButton("Z-A")
        sort_az.clicked.connect(lambda: self.sort_list(True))
        sort_za.clicked.connect(lambda: self.sort_list(False))
        
        sort_layout.addWidget(sort_az)
        sort_layout.addWidget(sort_za)
        
        left_side.addLayout(search_layout)
        left_side.addLayout(sort_layout)
        
        self.password_list_widget = QListWidget()
        self.password_list_widget.itemClicked.connect(self.on_item_clicked)
        left_side.addWidget(self.password_list_widget)
        
        main_layout.addWidget(self.left_frame, 1)


        self.last_clicked_item = None
        
        self.input_frame = QFrame() 
        self.input_frame.setObjectName("glass_box") 
        input_layout = QVBoxLayout(self.input_frame) 
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Name")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Website")
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Enter Password")
        
        add_btn = QPushButton("Add Password")
        add_btn.clicked.connect(self.add_password)

        input_layout.addWidget(QLabel("Add Password: "))
        input_layout.addWidget(self.title_input)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.pwd_input)
        input_layout.addWidget(add_btn)
        input_layout.addWidget(QFrame(frameShape=QFrame.HLine)) 
        input_layout.addStretch() 

        self.edit_frame = QFrame()
        edit_layout = QVBoxLayout()
        self.edit_title = QLineEdit() 
        self.edit_url = QLineEdit()   
        self.edit_pwd = QLineEdit()
        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_password)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("color: red;")
        self.delete_btn.clicked.connect(self.delete_password)

        edit_layout.addWidget(QLabel("<b>Change Password</b>"))
        edit_layout.addWidget(self.edit_title)
        edit_layout.addWidget(self.edit_url)
        edit_layout.addWidget(self.edit_pwd)
        edit_layout.addWidget(self.update_btn)
        edit_layout.addWidget(self.delete_btn) 

        self.edit_frame.setLayout(edit_layout)
        self.edit_frame.hide() 
        input_layout.addWidget(self.edit_frame)
        input_layout.addWidget(QFrame(frameShape=QFrame.HLine)) 

        self.settings_btn = QPushButton("Setting")
        self.settings_btn.clicked.connect(self.open_settings)
        input_layout.addWidget(self.settings_btn)
        
        main_layout.addWidget(self.input_frame, 1)
        self.main_page.setLayout(main_layout)              

        # setting screen 
        self.settings_page = QWidget()
        self.settings_page.setObjectName("transparent_page")

        main_settings_layout = QVBoxLayout(self.settings_page)
        main_settings_layout.setContentsMargins(50, 50, 50, 50)

        self.settings_container = QFrame()
        self.settings_container.setObjectName("glass_box")
        main_settings_layout.addWidget(self.settings_container)
        
        # blur 
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("<h2>Setting</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(title_label)
        settings_layout.addSpacing(30)

        settings_layout.addWidget(QLabel("<b>Theme:</b>"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["defult", "dark ", "custom"])

        self.theme_combo.currentTextChanged.connect(self.on_theme_combo_changed)
        settings_layout.addWidget(self.theme_combo)
        self.change_bg_btn = QPushButton("Change Background Picture")
        self.change_bg_btn.clicked.connect(self.pick_new_background)
        self.change_bg_btn.hide() 
        settings_layout.addWidget(self.change_bg_btn)
        self.test = settings_layout.addWidget(QLabel("<b>Blur:</b>"))
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(50, 255) 
        self.blur_slider.setValue(150) 
        self.blur_slider.valueChanged.connect(self.apply_blur_effect) 
        settings_layout.addWidget(self.blur_slider)

        settings_layout.addSpacing(20)
        

        MY_PERSONAL_QUOTE = "Iroha Project"
        
        settings_layout.addWidget(QLabel("<b>Message</b>"))
        self.quote_label = QLabel(MY_PERSONAL_QUOTE)
        self.quote_label.setWordWrap(True) 
        self.quote_label.setStyleSheet("color: #aaaaaa; font-style: italic; font-size: 14px;") 
        settings_layout.addWidget(self.quote_label)
        

        settings_layout.addStretch() 

        self.back_btn = QPushButton("Back")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.close_settings)
        settings_layout.addWidget(self.back_btn)
        
        self.settings_page.setLayout(settings_layout)

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0) 
        base_layout.addWidget(self.stacked_widget)
        self.setLayout(base_layout)
        
        self.load_data()
        self.load_settings()

    def create_card(self, title, url, pwd):
        card = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(QLabel(f"<b>{title}</b>"))
        layout.addWidget(QLabel(f"Website: {url}"))
        layout.addWidget(QLabel(f"Password: {pwd}"))
        card.setStyleSheet("background-color: transparent;") 

        card.setLayout(layout)
        return card
    
    def add_item_to_list(self, title, url, pwd):

        item = QListWidgetItem(self.password_list_widget)
        card = self.create_card(title, url, pwd)
        item.setSizeHint(card.sizeHint())
        self.password_list_widget.addItem(item)
        self.password_list_widget.setItemWidget(item, card)
    
    def save_settings(self, theme_data):

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(theme_data)

    def load_settings(self):
        self.custom_image_path = None 
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                self.theme_combo.blockSignals(True) 
                
                if "|" in content:
                    theme, img_path = content.split("|", 1)
                    self.custom_image_path = img_path
                    self.theme_combo.setCurrentText(theme)
                    if theme == "custom":
                        self.change_bg_btn.show() 
                    self.change_theme(theme, img_path)
                else:
                    self.theme_combo.setCurrentText(content)
                    if content == "custom":
                        self.change_bg_btn.show()
                    self.change_theme(content)

                self.theme_combo.blockSignals(False) 
        else:
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText("defult")
            self.theme_combo.blockSignals(False)
            self.change_theme("defult")

    def on_theme_combo_changed(self, theme_name):

        if theme_name == "custom":
            self.change_bg_btn.show()
        else:
            self.change_bg_btn.hide()
        self.change_theme(theme_name)

    def apply_blur_effect(self):

        alpha = self.blur_slider.value()

        current_theme = self.theme_combo.currentText()
        self.change_theme(current_theme, getattr(self, 'custom_image_path', None), alpha)

    def load_or_create_key(self):

        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
        else:
            with open(KEY_FILE, "rb") as key_file:
                key = key_file.read()
        self.cipher = Fernet(key) 

    def save_data_to_file(self):

        json_str = json.dumps(self.passwords_data)

        encrypted_data = self.cipher.encrypt(json_str.encode()).decode()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted_data)

    def pick_new_background(self):

        file_name, _ = QFileDialog.getOpenFileName(self, "Choose A Picture", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.custom_image_path = file_name
            self.change_theme("custom", file_name)

    def change_theme(self, theme_name, image_path=None, alpha=150):

        bg_image_css = "none"
        if theme_name == "custom":
            if not image_path:
                image_path = getattr(self, 'custom_image_path', None)
            
            if image_path:
                safe_path = image_path.replace("\\", "/")
                bg_image_css = f"url('{safe_path}')"

            glass_bg = f"rgba(255, 255, 255, {alpha})"
            text_color = "#222222" 
            btn_color = f"rgba(255, 255, 255, {min(alpha + 50, 255)})"
        
        else:
            if theme_name == "defult":
                bg_color = "#FFF0F5"
                text_color = "#333333"
                glass_bg = "#FFF0F5"
                btn_color = "#FFB6C1"
            elif theme_name == "dark ":
                bg_color = "#2b2b2b"
                text_color = "#ffffff"
                glass_bg = "#3a3a3a"
                btn_color = "#555555"
            else: 
                bg_color = "#FFF0F5"
                text_color = "#333333"
                glass_bg = "#FFF0F5"
                btn_color = "#FFB6C1"
            
            bg_image_css = "none"


        custom_style = f"""
            
            QStackedWidget#main_bg {{ 
                background-color: {'transparent' if theme_name == 'custom' else bg_color};
                border-image: {bg_image_css} 0 0 0 0 stretch stretch; 
            }}
            
            QWidget#transparent_page {{ background-color: transparent; }}
            
            QFrame#glass_box {{
                background-color: {glass_bg};
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 200);
            }}

            QListWidget, QLineEdit, QComboBox {{
                background-color: {glass_bg};
                color: {text_color};
                border: 1px solid gray;
                border-radius: 3px;
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {glass_bg};
                color: {text_color};
                selection-background-color: {btn_color};
            }}

            QPushButton {{
                background-color: {btn_color};
                border-radius: 5px;
                padding: 8px;
                color: {text_color};
                border: 1px solid #cccccc;
            }}
            QPushButton:hover {{ background-color: #ffcccc; }}
            
            QWidget {{ color: {text_color}; }}
        """
        self.setStyleSheet(custom_style)

    def add_password(self):
        title = self.title_input.text()
        url = self.url_input.text()
        pwd = self.pwd_input.text()

        if title and url and pwd:

            self.passwords_data[title] = {"url": url, "pwd": pwd}

            self.save_data_to_file()

            self.add_item_to_list(title, url, pwd)
            
            self.title_input.clear()
            self.url_input.clear()
            self.pwd_input.clear()

    
    def update_password(self):

        item = self.password_list_widget.currentItem()
        if not item:
            return

        new_title = self.edit_title.text()
        new_url = self.edit_url.text()
        new_pwd = self.edit_pwd.text()

        card = self.password_list_widget.itemWidget(item)
        labels = card.findChildren(QLabel)
        labels[0].setText(f"<b>{new_title}</b>")
        labels[1].setText(f"Website: {new_url}")
        labels[2].setText(f"Password: {new_pwd}")

        if self.last_clicked_item in self.passwords_data:
            del self.passwords_data[self.last_clicked_item] 
        
        self.passwords_data[new_title] = {"url": new_url, "pwd": new_pwd} 
        self.save_data_to_file() 
        
        self.last_clicked_item = new_title
                

    def delete_password(self):
        current_item = self.password_list_widget.currentItem()
        if current_item:

            colors = self.get_theme_colors()
            
            msg_box = QMessageBox(self)
            msg_box.setText('Are You Sure')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.FramelessWindowHint)

            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {colors['bg']};
                    border: 2px solid {colors['border']}; 
                }}
                QLabel {{
                    color: {colors['text']};
                    font-size: 14px;
                }}
                QPushButton {{
                    background-color: {colors['btn']};
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                    color: {colors['text']};
                }}
            """)
            
            reply = msg_box.exec()
            
            if reply == QMessageBox.Yes:
                
                row = self.password_list_widget.row(current_item)
                card = self.password_list_widget.itemWidget(current_item)
                title_to_delete = card.findChildren(QLabel)[0].text().replace("<b>", "").replace("</b>", "")
                
                self.password_list_widget.takeItem(row) 
                

                if title_to_delete in self.passwords_data:
                    del self.passwords_data[title_to_delete]
                    self.save_data_to_file() 
                
                self.display_item_details(None)
                self.last_clicked_item = None

                
    def sort_list(self, ascending=True):

        data_list = []
        for i in range(self.password_list_widget.count()):
            item = self.password_list_widget.item(i)
            card = self.password_list_widget.itemWidget(item)
            labels = card.findChildren(QLabel)
            title = labels[0].text().replace("<b>", "").replace("</b>", "")
            url = labels[1].text().split(": ")[1]
            pwd = labels[2].text().split(": ")[1]
            data_list.append((title, url, pwd))
        

        data_list.sort(key=lambda x: x[0].lower(), reverse=not ascending)
        self.password_list_widget.clear()
        for title, url, pwd in data_list:
            self.add_item_to_list(title, url, pwd)
        
        self.last_clicked_item = None 

    def filter_list(self):
        query = self.search_input.text().lower()
        search_by = self.search_type.currentText()
        
        for i in range(self.password_list_widget.count()):
            item = self.password_list_widget.item(i)
            card = self.password_list_widget.itemWidget(item)
            labels = card.findChildren(QLabel)
            target_text = labels[0].text() if search_by == "Website" else labels[1].text()
            item.setHidden(query not in target_text.lower())

    def get_theme_colors(self):

        current_theme = self.theme_combo.currentText()
        if current_theme == "dark ":
            return {"bg": "#2b2b2b", "border": "#555555", "text": "#ffffff", "btn": "#555555"}
        elif current_theme == "custom":
            return {"bg": "rgba(255, 255, 255, 230)", "border": "#80deea", "text": "#333333", "btn": "rgba(255, 255, 255, 180)"}
        else: 
            return {"bg": "#FFF0F5", "border": "#FFB6C1", "text": "#333333", "btn": "#FFB6C1"}
    
    def on_item_clicked(self, item):
        card = self.password_list_widget.itemWidget(item)
        title = card.findChildren(QLabel)[0].text().replace("<b>", "").replace("</b>", "")
        if self.last_clicked_item == title:
            self.password_list_widget.setCurrentItem(None)
            self.display_item_details(None)
            self.last_clicked_item = None 
        else:
            self.password_list_widget.setCurrentItem(item)
            self.display_item_details(item)
            self.last_clicked_item = title 
            if title in self.passwords_data:
                pwd_to_copy = self.passwords_data[title]["pwd"]
                QApplication.clipboard().setText(pwd_to_copy)
        
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = self.cipher.decrypt(encrypted_data.encode()).decode()
                        self.passwords_data = json.loads(decrypted_data) 
                        for title, info in self.passwords_data.items():
                            self.add_item_to_list(title, info["url"], info["pwd"])
            except Exception as e:
                print("error_load_data", e)

    def display_item_details(self, current_item):
            if current_item:
                self.edit_frame.show() 
                card = self.password_list_widget.itemWidget(current_item)
                labels = card.findChildren(QLabel)
                if len(labels) >= 3:
                    title = labels[0].text().replace("<b>", "").replace("</b>", "")
                    url = labels[1].text().split(": ")[1]
                    pwd = labels[2].text().split(": ")[1]

                    self.edit_title.setText(title)
                    self.edit_url.setText(url)
                    self.edit_pwd.setText(pwd)
                    
                    self.current_editing_item = current_item
            else:
                self.edit_frame.hide()
                self.edit_title.clear()
                self.edit_url.clear()
                self.edit_pwd.clear()
                self.current_editing_item = None

    def open_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)
        self.play_fade_animation(self.settings_page)

    def close_settings(self):

        current_theme = self.theme_combo.currentText()
        img_path = getattr(self, 'custom_image_path', None)
        if img_path:
            self.save_settings(f"{current_theme}|{img_path}")
        else:
            self.save_settings(current_theme)
        self.stacked_widget.setCurrentWidget(self.main_page)
        self.play_fade_animation(self.main_page)

    def play_fade_animation(self, target_widget):
        self.opacity_effect = QGraphicsOpacityEffect(target_widget)
        target_widget.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(400) 
        self.animation.setStartValue(0.0) 
        self.animation.setEndValue(1.0) 
        self.animation.setEasingCurve(QEasingCurve.InOutQuad) 
        self.animation.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec())
