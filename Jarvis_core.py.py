import sys
import math
import random
import json
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QFrame, QScrollArea, QComboBox, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QRectF, QParallelAnimationGroup
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
import ollama
CHAT_FILE = "jarvis_memory.json"
# --- Memory IO Optimization ---
# Fast-load, and save memory safely without blocking main UI updates
def load_memory():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None
def save_memory(history):
    try:
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, separators=(',', ':')) # Optimize JSON size
    except Exception:
        pass
# --- Sensory Engine (Privacy Focused) ---
# Removed webcam. Now infers emotion through keystroke sentiment analysis.
class AnimatedBackground(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(30)
        
    def init_particles(self):
        w, h = self.width(), self.height()
        if w < 100 or h < 100: return
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.random() * w,
                'y': random.random() * h,
                'vx': (random.random() - 0.5) * 0.4,
                'vy': (random.random() - 0.5) * 0.4,
                'size': random.random() * 2 + 1
            })

    def update_particles(self):
        w, h = self.width(), self.height()
        if not self.particles: self.init_particles()
        if w < 10 or h < 10: return
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['x'] < 0: p['x'] = w
            if p['x'] > w: p['x'] = 0
            if p['y'] < 0: p['y'] = h
            if p['y'] > h: p['y'] = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dark Space Gradient
        painter.fillRect(self.rect(), QColor(9, 9, 11))
        
        # Subtle Neural Grid
        painter.setPen(QPen(QColor(30, 30, 35, 80), 1))
        grid_size = 60
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)

        # Particles & Connections
        for i, p1 in enumerate(self.particles):
            # Glow
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 30))
            painter.drawEllipse(QRectF(p1['x']-p1['size'], p1['y']-p1['size'], p1['size']*2, p1['size']*2))
            
            for p2 in self.particles[i+1:]:
                dist = math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])
                if dist < 120:
                    alpha = int(40 * (1 - dist/120))
                    painter.setPen(QPen(QColor(255, 255, 255, alpha), 1))
                    painter.drawLine(int(p1['x']), int(p1['y']), int(p2['x']), int(p2['y']))

class HolographicOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.angle = 0
        self.pulse = 0
        self.is_active = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        
    def animate(self):
        self.angle = (self.angle + 3) % 360
        self.pulse = (self.pulse + 0.12) % (2 * math.pi)
        self.update()

    def start_pulse(self):
        self.is_active = True
        self.show()
        self.timer.start(16)
        
    def stop_pulse(self):
        self.is_active = False
        self.hide()
        self.timer.stop()

    def paintEvent(self, event):
        if not self.is_active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width()/2, self.height()/2
        scale = 1.0 + 0.15 * math.sin(self.pulse)
        
        # Outer Ring
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1.5, Qt.PenStyle.DashLine))
        painter.drawArc(QRectF(6, 6, 28, 28), self.angle * 16, 260 * 16)
        
        # Inner Core
        glow = int(160 + 40 * math.sin(self.pulse))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, glow))
        painter.drawEllipse(QRectF(cx - 5*scale, cy - 5*scale, 10*scale, 10*scale))
        
        # Dynamic Crosshair
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.angle * 1.5)
        painter.drawLine(-14, 0, 14, 0)
        painter.drawLine(0, -14, 0, 14)
        painter.restore()

class ThinkingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(16)
        
    def update_anim(self):
        self.step += 1
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(250, 250, 250))
        painter.drawText(0, 25, "Jarvis")
        
        start_x = 45
        for i in range(3):
            val = math.sin(self.step * 0.12 - i * 0.8)
            y_offset = max(0, val) * 6
            size = 5 + max(0, val) * 1.5
            alpha = int(80 + ((val + 1) * 0.5) * 175)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(QRectF(start_x + i * 14, 20 - y_offset, size, size))

# --- Stream Engine ---
class AIWorker(QThread):
    chunk_received = pyqtSignal(str)
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    def __init__(self, model_name, messages):
        super().__init__()
        self.model_name = model_name
        self.messages = messages
    def run(self):
        try:
            print(f"DEBUG: Starting Ollama chat with model: {self.model_name}")
            # Yield chunks natively to keep memory footprint ultra low
            response = ollama.chat(model=self.model_name, messages=self.messages, stream=True)
            full_reply = []
            for chunk in response:
                text_chunk = chunk['message']['content']
                full_reply.append(text_chunk)
                self.chunk_received.emit(text_chunk)  
            
            final_reply = "".join(full_reply)
            print(f"DEBUG: Ollama response complete. Length: {len(final_reply)}")
            self.response_ready.emit(final_reply)
        except Exception as e:
            print(f"DEBUG: Ollama error: {str(e)}")
            self.error_occurred.emit(str(e))
class ModernAIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Core")
        self.resize(900, 750)
        
        # Optimize Window flags for compositing performance
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.model_name = "gemma3:1b"
        self.current_user_emotion = "Neutral"
        self.jarvis_mood = "Stable/Observant"
        
        self.oldPos = self.pos()
        self.initUI()
        
        # Hardware accelerated Window Startup
        self.setWindowOpacity(0.0)
        self.win_anim = QPropertyAnimation(self, b"windowOpacity")
        self.win_anim.setDuration(600)
        self.win_anim.setStartValue(0.0)
        self.win_anim.setEndValue(1.0)
        self.win_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.win_anim.start()
    def calculate_typing_emotion(self, text):
        text_lower = text.lower()
        if any(w in text_lower for w in ["hate", "stupid", "idiot", "worst", "annoying", "fuck", "shit"]): return "Angry"
        if any(w in text_lower for w in ["sad", "depressed", "cry", "lonely", "hurt", "bad day"]): return "Sad"
        if any(w in text_lower for w in ["happy", "great", "awesome", "love", "amazing", "thanks", "perfect", "yes"]): return "Happy"
        if any(w in text_lower for w in ["help", "please", "stuck", "confused", "stress", "urgent", "error", "failed", "broken"]): return "Stressed"
        if "?" in text and len(text) > 10: return "Curious"
        if text.isupper() and len(text) > 4: return "Frustrated"
        return "Neutral"
        
    def initUI(self):
        self.font_family = "Segoe UI"
        
        self.central_container = QWidget(self)
        self.setCentralWidget(self.central_container)
        
        container_layout = QVBoxLayout(self.central_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        self.bg_widget = AnimatedBackground(self.central_container)
        self.bg_widget.setObjectName("bg_widget")
        container_layout.addWidget(self.bg_widget)
        layout = QVBoxLayout(self.bg_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.top_bar = QFrame()
        self.top_bar.setObjectName("top_bar")
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet("border-bottom: 1px solid #18181b;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(25, 0, 25, 0)
        
        title_label = QLabel("JARVIS CORE")
        title_label.setObjectName("title_label")
        title_label.setFont(QFont(self.font_family, 10, QFont.Weight.Medium))
        
        self.pulse_anim = HolographicOrb()
        self.pulse_anim.hide()
        
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(10)
        
        self.model_selector = QComboBox()
        self.model_selector.setObjectName("model_selector")
        
        # Fast load installed models
        try:
            available_models = [m.model for m in ollama.list().models]
            if not available_models: available_models = ["No models found"]
        except Exception:
            available_models = ["gemma3:1b"]
            
        self.model_selector.addItems(available_models)
        if "gemma3:1b" in available_models:
            self.model_selector.setCurrentText("gemma3:1b")
            self.model_name = "gemma3:1b"
        elif available_models:
            self.model_selector.setCurrentText(available_models[0])
            self.model_name = available_models[0]
            
        self.model_selector.setFixedSize(140, 30)
        self.model_selector.currentTextChanged.connect(self.change_model)
        
        self.clear_btn = QPushButton("↺")
        self.clear_btn.setObjectName("tool_btn")
        self.clear_btn.setFixedSize(30, 30)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setToolTip("Clear Memory")
        self.clear_btn.clicked.connect(self.clear_memory)
        
        tools_layout.addWidget(self.model_selector)
        tools_layout.addWidget(self.clear_btn)
        
        win_controls = QHBoxLayout()
        win_controls.setSpacing(12)
        
        min_btn = QPushButton("─")
        min_btn.setObjectName("min_btn")
        min_btn.setFixedSize(30, 30)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        min_btn.clicked.connect(self.showMinimized)
        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("max_btn")
        self.max_btn.setFixedSize(30, 30)
        self.max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("close_btn")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        win_controls.addWidget(min_btn)
        win_controls.addWidget(self.max_btn)
        win_controls.addWidget(close_btn)
        
        top_layout.addWidget(title_label)
        top_layout.addWidget(self.pulse_anim)
        top_layout.addStretch()
        top_layout.addLayout(tools_layout)
        top_layout.addSpacing(20)
        top_layout.addLayout(win_controls)
        layout.addWidget(self.top_bar)
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        self.scroll_area.verticalScrollBar().setSingleStep(20)
        
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chat_container")
        self.chat_container.setStyleSheet("background-color: transparent;")
        
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(35, 25, 35, 25)
        self.chat_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area, stretch=1)
        input_container = QFrame()
        input_container.setObjectName("input_container")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(35, 10, 35, 35)
        
        self.input_bg = QFrame()
        self.input_bg.setObjectName("input_bg")
        self.input_bg.setFixedHeight(55)
        
        inner_input_layout = QHBoxLayout(self.input_bg)
        inner_input_layout.setContentsMargins(20, 0, 8, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText("Command Jarvis...")
        self.input_field.setFont(QFont(self.font_family, 12))
        self.input_field.setFrame(False)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("↑")
        self.send_button.setObjectName("send_button")
        self.send_button.setFixedSize(38, 38)
        self.send_button.setFont(QFont(self.font_family, 16, QFont.Weight.Bold))
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        
        inner_input_layout.addWidget(self.input_field)
        inner_input_layout.addWidget(self.send_button)
        
        input_layout.addWidget(self.input_bg)
        layout.addWidget(input_container)
        self.setStyleSheet(f"""
            #bg_widget {{
                background-color: transparent;
                border-radius: 16px;
                border: 1px solid #27272a;
            }}
            #top_bar {{
                background-color: rgba(9, 9, 11, 150);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
            #title_label {{
                color: #fafafa;
                letter-spacing: 3px;
                font-weight: 500;
            }}
            #min_btn, #max_btn, #close_btn {{
                background-color: transparent;
                color: #71717a;
                border: none;
                border-radius: 15px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }}
            #min_btn:hover, #max_btn:hover {{
                background-color: #27272a;
                color: #fafafa;
            }}
            #close_btn:hover {{
                background-color: #ef4444;
                color: #fafafa;
            }}
            #tool_btn, #copy_btn {{
                background-color: transparent;
                color: #71717a;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            #tool_btn:hover, #copy_btn:hover {{
                background-color: #27272a;
                color: #fafafa;
            }}
            #model_selector {{
                background-color: #18181b;
                color: #a1a1aa;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 2px 8px;
                font-family: 'Segoe UI';
            }}
            #model_selector:hover {{
                border: 1px solid #3f3f46;
                color: #fafafa;
            }}
            #model_selector::drop-down {{ border: none; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #3f3f46;
                min-height: 40px;
                border-radius: 2px;
            }}
            QScrollBar::handle:vertical:hover {{ background: #52525b; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            #input_container {{ background-color: transparent; }}
            #input_bg {{
                background-color: #18181b;
                border-radius: 27px;
                border: 1px solid #27272a;
            }}
            #input_bg:hover {{ border: 1px solid #3f3f46; }}
            #input_field {{ background-color: transparent; color: #fafafa; }}
            #send_button {{
                background-color: #fafafa;
                color: #09090b;
                border-radius: 19px;
                border: none;
            }}
            #send_button:hover {{ background-color: #e4e4e7; }}
            #send_button:disabled {{
                background-color: #27272a;
                color: #52525b;
            }}
        """)
        # Fast Typing Queue
        self.typing_queue = []
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_character)
        
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.blink_cursor)
        
        self.cursor_visible = False
        self.is_generating = False
        self.ai_finished = True
        self.thinking_widget = None
        self.load_initial_memory()
    def get_system_prompt(self):
        return f"""
        You are Jarvis, a highly advanced intelligence with a subtle human-like personality. 
        Your core model is {self.model_name}. You are running locally on the user's hardware.
        
        [YOUR PERSONA]
        You are professional, witty, and calm. You are a collaborator, not just a tool. 
        Keep your emotions subtle and integrated into your speech—do NOT over-explain your feelings.
        Speak naturally and conversationally.
        
        [STRICT RULE]
        NEVER use brackets (...) to describe your tone, actions, or emotions. Do NOT use stage directions.
        Just speak directly to the user.
        
        [INTERNAL STATE]
        Your current internal simulated mood is: {self.jarvis_mood}. 
        
        [SENSORY INPUT]
        The user's current emotional state is inferred as: {self.current_user_emotion}. 
        Adapt your tone subtly. If they are stressed, be a bit more grounding. If they are happy, be supportive.
        
        [AUTONOMOUS CODE EXECUTION]
        If the user asks you to calculate something, fetch data, or write a script, you MUST output the python code inside the exact tags [EXECUTE] and [/EXECUTE]. 
        Do not output any examples unless required. The system will run the code between those tags silently and return the terminal output back to you so you can give the final answer.
        """
    def change_model(self, model_name):
        self.model_name = model_name
        if len(self.chat_history) > 0 and self.chat_history[0]['role'] == 'system':
            self.chat_history[0]['content'] = self.get_system_prompt()
            save_memory(self.chat_history)
        self.create_message_bubble("System", f"Model successfully switched to: {model_name}", "system")
        self.scroll_to_bottom()
    def load_initial_memory(self):
        mem = load_memory()
        if mem:
            self.chat_history = mem
            if len(self.chat_history) > 0 and self.chat_history[0]['role'] == 'system':
                self.chat_history[0]['content'] = self.get_system_prompt()
                
            for msg in self.chat_history:
                if msg['role'] == 'user':
                    if "SYSTEM NOTIFICATION" not in msg['content']:
                        self.create_message_bubble("You", msg['content'], "user")
                elif msg['role'] == 'assistant':
                    content = re.sub(r'\[EXECUTE\].*?\[/EXECUTE\]', '', msg['content'], flags=re.DOTALL)
                    if content.strip():
                        self.create_message_bubble("Jarvis", content.strip(), "ai")
        else:
            self.chat_history = [{'role': 'system', 'content': self.get_system_prompt()}]
            self.create_message_bubble("Jarvis", "Hi I am Jarvis", "ai")
    def clear_memory(self):
        self.chat_history = [{'role': 'system', 'content': self.get_system_prompt()}]
        save_memory(self.chat_history)
        
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.is_generating = False
        self.typing_timer.stop()
        self.cursor_timer.stop()
        self.pulse_anim.stop_pulse()
        self.reset_input()
        
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        self.current_ai_lbl = None
        self.create_message_bubble("Jarvis", "Hi I am Jarvis", "ai")
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.central_container.layout().setContentsMargins(10, 10, 10, 10) 
            self.bg_widget.setStyleSheet(self.bg_widget.styleSheet() + " #bg_widget { border-radius: 16px; border: 1px solid #27272a; }")
        else:
            self.central_container.layout().setContentsMargins(0, 0, 0, 0)
            self.bg_widget.setStyleSheet(self.bg_widget.styleSheet() + " #bg_widget { border-radius: 0px; border: none; }")
            self.showMaximized()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.isMaximized():
            self.oldPos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.isMaximized():
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
    def create_message_bubble(self, sender, text, msg_type="user"):
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 5, 0, 15)
        bubble_layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        sender_lbl = QLabel(sender)
        sender_lbl.setFont(QFont(self.font_family, 10, QFont.Weight.Bold))
        header_layout.addWidget(sender_lbl)
        header_layout.addStretch()
        
        msg_lbl = QLabel(text)
        msg_lbl.setFont(QFont(self.font_family, 12))
        msg_lbl.setWordWrap(True)
        msg_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if msg_type == "user":
            sender_lbl.setStyleSheet("color: #fafafa;")
            msg_lbl.setStyleSheet("color: #a1a1aa;")
        elif msg_type == "ai":
            sender_lbl.setStyleSheet("color: #fafafa;") 
            msg_lbl.setStyleSheet("color: #e4e4e7;")
            
            copy_btn = QPushButton("📋")
            copy_btn.setObjectName("copy_btn")
            copy_btn.setFixedSize(24, 24)
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_btn.setToolTip("Copy Text")
            copy_btn.clicked.connect(lambda _, t=msg_lbl: QApplication.clipboard().setText(t.text().replace('<br>', '\n')))
            header_layout.addWidget(copy_btn)
        else:
            sender_lbl.setStyleSheet("color: #ef4444;")
            msg_lbl.setStyleSheet("color: #fca5a5;")
            
        bubble_layout.addLayout(header_layout)
        bubble_layout.addWidget(msg_lbl)
        
        # Modern Premium Entrance Animation
        effect = QGraphicsOpacityEffect(bubble)
        effect.setOpacity(0.0)
        bubble.setGraphicsEffect(effect)
        
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(500)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        
        # Subtle Slide-up
        bubble_pos_anim = QPropertyAnimation(bubble, b"pos")
        bubble_pos_anim.setDuration(500)
        # This will be triggered once the layout finishes
        
        bubble._effect = effect
        bubble._anim = fade_anim
        fade_anim.start()
        
        self.chat_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)
        return msg_lbl
    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        max_val = scrollbar.maximum()
        if scrollbar.value() < max_val:
            self.scroll_anim = QPropertyAnimation(scrollbar, b"value")
            self.scroll_anim.setDuration(150)
            self.scroll_anim.setStartValue(scrollbar.value())
            self.scroll_anim.setEndValue(max_val)
            self.scroll_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.scroll_anim.start()
    def update_jarvis_mood(self, user_emotion):
        if user_emotion == "Angry":
            self.jarvis_mood = "Concerned/Apologetic"
        elif user_emotion == "Sad":
            self.jarvis_mood = "Empathetic/Soft"
        elif user_emotion == "Happy":
            self.jarvis_mood = "Cheerful/Energetic"
        elif user_emotion == "Stressed":
            self.jarvis_mood = "Calm/Reassuring"
        elif user_emotion == "Curious":
            self.jarvis_mood = "Intrigued/Helpful"
        else:
            self.jarvis_mood = "Stable/Friendly"

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text: return
        self.input_field.clear()
        
        if user_text.lower() == "/stress":
            self.trigger_stress_test()
            return

        # Determine emotion silently through text sentiment
        self.current_user_emotion = self.calculate_typing_emotion(user_text)
        self.update_jarvis_mood(self.current_user_emotion)
        
        self.create_message_bubble("You", user_text, "user")
        
        if len(self.chat_history) > 0 and self.chat_history[0]['role'] == 'system':
            self.chat_history[0]['content'] = self.get_system_prompt()
            
        self.chat_history.append({'role': 'user', 'content': user_text})
        save_memory(self.chat_history)
        self.thinking_widget = ThinkingWidget()
        self.chat_layout.addWidget(self.thinking_widget)
        self.scroll_to_bottom()
        self.input_field.setDisabled(True)
        self.send_button.setDisabled(True)
        self.input_field.setPlaceholderText("Processing...")
        
        self.is_generating = True
        self.ai_finished = False
        self.typing_queue = []
        self.cursor_visible = True
        self.cursor_timer.start(500)
        self.pulse_anim.start_pulse() 
        
        # Store worker as a class attribute to prevent garbage collection
        self.worker = AIWorker(self.model_name, self.chat_history)
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.response_ready.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_ai_error)
        self.worker.start()
        print(f"DEBUG: AI Worker thread started.")
    def trigger_stress_test(self):
        self.create_message_bubble("System", "INITIATING MAXIMUM STRESS TEST...", "system")
        
        # Visual Overload
        if hasattr(self, 'bg_widget'):
            self.bg_widget.particles = []
            for _ in range(350):
                self.bg_widget.particles.append({
                    'x': random.random() * self.width(),
                    'y': random.random() * self.height(),
                    'vx': (random.random() - 0.5) * 2.5,
                    'vy': (random.random() - 0.5) * 2.5,
                    'size': random.random() * 3 + 1
                })
        
        # Core Hyper-Drive
        if hasattr(self, 'pulse_anim'):
            self.pulse_anim.start_pulse()
            self.pulse_anim.timer.setInterval(2) # 500 FPS logic
            
        self.create_message_bubble("Jarvis", "SYSTEM OVERLOAD INITIATED. Monitoring thermal limits. Visual engine at 700% capacity.", "ai")
        QTimer.singleShot(10000, self.reset_stress_test)

    def reset_stress_test(self):
        if hasattr(self, 'bg_widget'):
            self.bg_widget.init_particles()
        if hasattr(self, 'pulse_anim'):
            self.pulse_anim.timer.setInterval(16)
        self.create_message_bubble("System", "Stress test complete. Visual engine stabilized.", "system")

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        if self.is_generating:
            self.update_ai_text_display()
    def update_ai_text_display(self):
        if getattr(self, 'current_ai_lbl', None) is None: return
            
        display_text = self.current_ai_text.replace('\n', '<br>')
        display_text = re.sub(r'\[EXECUTE\].*?(?:\[/EXECUTE\]|$)', '', display_text, flags=re.DOTALL)
        
        if self.is_generating:
            cursor_html = '<span style="color: #71717a;"> ▍</span>' if self.cursor_visible else ''
            display_text += cursor_html
            
        try:
            self.current_ai_lbl.setText(display_text)
        except RuntimeError:
            self.current_ai_lbl = None
    def handle_chunk(self, chunk):
        if self.thinking_widget is not None:
            self.thinking_widget.deleteLater()
            self.thinking_widget = None
            self.current_ai_lbl = self.create_message_bubble("Jarvis", "", "ai")
            self.current_ai_text = ""
            self.typing_timer.start(10) # Ultra-fast 10ms fluid updates
        self.typing_queue.extend(list(chunk))
        
    def type_next_character(self):
        if self.typing_queue:
            q_len = len(self.typing_queue)
            chars_to_type = 1
            if q_len > 10: chars_to_type = 2
            if q_len > 30: chars_to_type = 4
            if q_len > 80: chars_to_type = 8
            
            chunk = "".join(self.typing_queue[:chars_to_type])
            del self.typing_queue[:chars_to_type]
            
            self.cursor_visible = True
            self.current_ai_text += chunk
            self.update_ai_text_display()
            self.scroll_to_bottom()
        elif self.ai_finished:
            self.typing_timer.stop()
            self.cursor_timer.stop()
            self.pulse_anim.stop_pulse()
            self.cursor_visible = False
            self.update_ai_text_display()
            self.is_generating = False
            self.reset_input()
    def handle_ai_response(self, full_reply):
        self.chat_history.append({'role': 'assistant', 'content': full_reply})
        # Save memory lazily to prevent stutter
        QTimer.singleShot(1000, lambda: save_memory(self.chat_history))
        self.ai_finished = True
        
        exec_match = re.search(r'\[EXECUTE\](.*?)(?:\[/EXECUTE\]|$)', full_reply, re.DOTALL)
        if exec_match:
            code = exec_match.group(1).strip()
            code = code.replace('```python', '').replace('```', '').strip()
            self.create_message_bubble("System", "Autonomously executing code sandbox...", "system")
            self.scroll_to_bottom()
            QTimer.singleShot(500, lambda: self.run_code_sandbox(code))
            return
    def run_code_sandbox(self, code):
        import subprocess
        with open("sandbox.py", "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            result = subprocess.run([sys.executable, "sandbox.py"], capture_output=True, text=True, timeout=15)
            output = result.stdout + "\n" + result.stderr
        except subprocess.TimeoutExpired:
            output = "Execution timed out after 15 seconds."
        except Exception as e:
            output = str(e)
            
        output = output.strip()
        if not output: output = "Code executed successfully with no output."
        
        sys_msg = f"SYSTEM NOTIFICATION: Code executed successfully. Output:\n{output}\nPlease explain this output to the user briefly."
        self.chat_history.append({'role': 'user', 'content': sys_msg})
        
        self.create_message_bubble("Terminal", output, "system")
        self.scroll_to_bottom()
        
        self.is_generating = True
        self.ai_finished = False
        self.typing_queue = []
        self.cursor_visible = True
        self.cursor_timer.start(500)
        self.pulse_anim.start_pulse() 
        self.worker = AIWorker(self.model_name, self.chat_history)
        self.worker.chunk_received.connect(self.handle_chunk)
        self.worker.response_ready.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_ai_error)
        self.worker.start()
        
    def handle_ai_error(self, error_msg):
        self.ai_finished = True
        self.typing_queue = []
        self.typing_timer.stop()
        self.cursor_timer.stop()
        self.pulse_anim.stop_pulse()
        
        if self.thinking_widget is not None:
            self.thinking_widget.deleteLater()
            self.thinking_widget = None
            
        self.create_message_bubble("System Error", error_msg, "system")
        self.reset_input()
    def reset_input(self):
        self.input_field.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_field.setPlaceholderText("Command Jarvis...")
        self.input_field.setFocus()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernAIWindow()
    window.show()
    sys.exit(app.exec())
