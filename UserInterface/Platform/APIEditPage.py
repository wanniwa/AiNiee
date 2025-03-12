from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from qfluentwidgets import PlainTextEdit
from qfluentwidgets import MessageBoxBase
from qfluentwidgets import SingleDirectionScrollArea

from Base.Base import Base
from Widget.GroupCard import GroupCard
from Widget.ComboBoxCard import ComboBoxCard
from Widget.LineEditCard import LineEditCard
from Widget.SwitchButtonCard import SwitchButtonCard
from Widget.EditableComboBoxCard import EditableComboBoxCard

class APIEditPage(MessageBoxBase, Base):

    def __init__(self, window, key):
        super().__init__(window)

        # 初始化
        self.key = key

        # 设置框体
        self.widget.setFixedSize(960, 720)
        self.yesButton.setText(self.tra("关闭"))
        self.cancelButton.hide()

        # 载入配置文件
        config = self.load_config()

        # 设置主布局
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        # 设置滚动器
        self.scroller = SingleDirectionScrollArea(self, orient = Qt.Vertical)
        self.scroller.setWidgetResizable(True)
        self.scroller.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.viewLayout.addWidget(self.scroller)

        # 设置滚动控件
        self.vbox_parent = QWidget(self)
        self.vbox_parent.setStyleSheet("QWidget { background: transparent; }")
        self.vbox = QVBoxLayout(self.vbox_parent)
        self.vbox.setSpacing(8)
        self.vbox.setContentsMargins(24, 24, 24, 24) # 左、上、右、下
        self.scroller.setWidget(self.vbox_parent)

        # 接口地址
        if "api_url" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_url(self.vbox, config)

        # 接口地址自动补全
        if "auto_complete" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_auto_complete(self.vbox, config)

        # 接口密钥
        if "api_key" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_key(self.vbox, config)

        # 接口格式
        if "api_format" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_format(self.vbox, config)

        # 账户类型
        if "account" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_account(self.vbox, config)

        # 模型名称
        if "model" in config.get("platforms").get(self.key).get("key_in_settings"):
            self.add_widget_model(self.vbox, config)

        # 填充
        self.vbox.addStretch(1)

    # 接口地址
    def add_widget_url(self, parent, config):
        def init(widget):
            widget.set_text(config.get("platforms").get(self.key).get("api_url"))
            widget.set_fixed_width(256)
            info_cont = self.tra("请输入接口地址") + " ..."
            widget.set_placeholder_text(info_cont)

        def text_changed(widget, text: str):
            config = self.load_config()
            config["platforms"][self.key]["api_url"] = text.strip()
            self.save_config(config)

        parent.addWidget(
            LineEditCard(
                self.tra("接口地址"),
                self.tra("请输入接口地址，例如 https://api.deepseek.com"),
                init = init,
                text_changed = text_changed,
            )
        )

    # 接口地址自动补全
    def add_widget_auto_complete(self, parent, config):
        def init(widget):
            widget.set_checked(config.get("platforms").get(self.key).get("auto_complete"))

        def checked_changed(widget, checked: bool):
            config = self.load_config()
            config["platforms"][self.key]["auto_complete"] = checked
            self.save_config(config)

        parent.addWidget(
            SwitchButtonCard(
                self.tra("接口地址自动补全"),
                self.tra("将自动为你填写接口地址，例如 https://api.deepseek.com -> https://api.deepseek.com/v1"),
                init = init,
                checked_changed = checked_changed,
            )
        )

    # 接口密钥
    def add_widget_key(self, parent, config):

        def text_changed(widget):
            config = self.load_config()
            config["platforms"][self.key]["api_key"] = widget.toPlainText().strip()
            self.save_config(config)

        def init(widget):
            plain_text_edit = PlainTextEdit(self)
            plain_text_edit.setPlainText(config.get("platforms").get(self.key).get("api_key"))
            plain_text_edit.setPlaceholderText(self.tra("请输入接口密钥"))
            plain_text_edit.textChanged.connect(lambda: text_changed(plain_text_edit))
            widget.addWidget(plain_text_edit)

        parent.addWidget(
            GroupCard(
                self.tra("接口密钥"),
                self.tra("请输入接口密钥，例如 sk-d0daba12345678fd8eb7b8d31c123456，多个密钥之间请使用半角逗号（,）分隔"),
                init = init,
            )
        )

    # 接口格式
    def add_widget_format(self, parent, config):
        def init(widget):
            platform = config.get("platforms").get(self.key)

            widget.set_items(platform.get("format_datas"))
            widget.set_current_index(max(0, widget.find_text(platform.get("api_format"))))

        def current_text_changed(widget, text: str):
            config = self.load_config()
            config["platforms"][self.key]["api_format"] = text.strip()
            self.save_config(config)

        parent.addWidget(
            ComboBoxCard(
                self.tra("接口格式"),
                self.tra("请选择接口格式，大部分模型使用 OpenAI 格式，部分中转站的 Claude 模型则使用 Anthropic 格式"),
                [],
                init = init,
                current_text_changed = current_text_changed,
            )
        )

    # 账户类型
    def add_widget_account(self, parent, config):
        # 获取当前平台配置
        platform = config.get("platforms").get(self.key)
        
        # 提取账户类型原始键并生成翻译后的键值对 (显示文本, 存储值)
        account_datas = platform.get("account_datas", {})
        account_keys = list(account_datas.keys())
        translated_pairs = [(self.tra(key), key) for key in account_keys]  # 关键翻译步骤
        
        def init(widget) -> None:
            """初始化时根据存储的原始键设置当前选项"""
            current_value = platform.get("account", "")
            
            # 通过原始键查找对应索引
            index = next(
                (i for i, (_, key) in enumerate(translated_pairs) if key == current_value),
                0  # 默认第一个选项
            )
            widget.set_current_index(max(0, index))

        def current_text_changed(widget, text: str) -> None:
            """选项变化时存储对应的原始键"""
            # 通过显示文本查找原始键
            value = next(
                (key for display, key in translated_pairs if display == text),
                account_keys[0] if account_keys else ""  # 默认第一个键
            )
            
            config = self.load_config()
            config["platforms"][self.key]["account"] = value
            self.save_config(config)

        # 创建带翻译的选项列表
        options = [display for display, _ in translated_pairs]

        parent.addWidget(
            ComboBoxCard(
                self.tra("账户类型"),
                self.tra("请选择账户类型"),
                options,
                init=init,
                current_text_changed=current_text_changed
            )
        )


    # 模型名称
    def add_widget_model(self, parent, config):
        def init(widget):
            platforms = config.get("platforms").get(self.key)

            # 如果默认模型列表中不存在该条目，则添加
            items = platforms.get("model_datas")
            if platforms.get("model") != "" and platforms.get("model") not in platforms.get("model_datas"):
                items.append(platforms.get("model"))

            widget.set_items(items)
            widget.set_fixed_width(256)
            widget.set_current_index(max(0, widget.find_text(platforms.get("model"))))
            widget.set_placeholder_text(self.tra("请输入模型名称"))

        def current_text_changed(widget, text: str):
            config = self.load_config()
            config["platforms"][self.key]["model"] = text.strip()
            self.save_config(config)

        def items_changed(widget, items: list[str]): # 处理 items_changed 信号的槽函数
            config = self.load_config()
            config["platforms"][self.key]["model_datas"] = items # 更新 model_datas
            self.save_config(config) # 保存配置

        card = EditableComboBoxCard(
            self.tra("模型名称(可编辑)"),
            self.tra("请选择或者输入要使用的模型的名称"),
            [],
            init = init,
            current_text_changed = current_text_changed,
        )
        card.items_changed.connect(lambda items: items_changed(card, items)) # 连接信号
        parent.addWidget(card)
