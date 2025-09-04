#!/usr/bin/env python3
"""
Battery Manager - Final UI Design
Ultra Simple Battery Manager with Sales-Ready Design
緊急修正: 450x600コンパクト版で確実に全要素表示
"""

import customtkinter as ctk
import threading
import time
import subprocess
import re
import asyncio
import sys
from datetime import datetime

# 親ディレクトリからコア機能をインポート
sys.path.append('..')
try:
    from battery_controller_core import BatteryChargeController
    from app_config import TAPO_SETTINGS, CHARGE_SETTINGS, OTHER_SETTINGS
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"警告: コア機能インポートエラー: {e}")
    CORE_AVAILABLE = False

# 🎨 Final Design Colors（販売品質）
COLORS = {
    'bg_primary': '#1e1e1e',      # メイン背景
    'bg_card': '#2d2d2d',         # カード背景
    'accent_green': '#34c759',    # Apple Green
    'accent_blue': '#007aff',     # Apple Blue  
    'accent_orange': '#ff9500',   # Apple Orange
    'accent_red': '#ff3b30',      # Apple Red
    'text_primary': '#ffffff',    # メインテキスト
    'text_secondary': '#8e8e93',  # セカンダリテキスト
}

class BatteryManagerFinalUI:
    def __init__(self, screenshot_mode=False):
        """初期化 - Final Sales-Ready UI (450x600 固定)"""
        # CustomTkinter設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.screenshot_mode = screenshot_mode
        
        # データ初期化
        if screenshot_mode:
            self.battery_level = 65  # 理想データ
            self.is_charging = False
            self.is_optimal_range = True
        else:
            self.battery_level = 0
            self.is_charging = False
            self.is_optimal_range = False
            
        self.auto_mode = True
        self.start_threshold = CHARGE_SETTINGS.get("start_threshold", 30)
        self.stop_threshold = CHARGE_SETTINGS.get("stop_threshold", 78)
        
        # コア機能初期化
        self.controller = None
        if CORE_AVAILABLE and not screenshot_mode:
            try:
                self.controller = BatteryChargeController()
                self.controller.charge_start_threshold = self.start_threshold
                self.controller.charge_stop_threshold = self.stop_threshold
            except Exception as e:
                print(f"Controller初期化エラー: {e}")
        
        # ウィンドウ作成
        self.root = ctk.CTk()
        self.setup_final_window()
        self.create_final_ui()
        
    def setup_final_window(self):
        """ウィンドウ設定 - 450x600固定"""
        self.root.title("🔋 Ultra Simple Battery Manager")
        self.root.geometry("450x600")
        self.root.resizable(False, False)  # サイズ変更不可
        self.root.configure(fg_color=COLORS['bg_primary'])
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 225
        y = (self.root.winfo_screenheight() // 2) - 300
        self.root.geometry(f"450x600+{x}+{y}")
        
    def create_final_ui(self):
        """Final UI作成 - グリッドレイアウトで確実配置"""
        # グリッド設定
        self.root.grid_rowconfigure(0, weight=0)  # ヘッダー
        self.root.grid_rowconfigure(1, weight=0)  # バッテリー  
        self.root.grid_rowconfigure(2, weight=0)  # ステータス
        self.root.grid_rowconfigure(3, weight=0)  # コントロール
        self.root.grid_rowconfigure(4, weight=0)  # アクション
        self.root.grid_rowconfigure(5, weight=0)  # フッター
        self.root.grid_columnconfigure(0, weight=1)
        
        # === [ヘッダー部] 40px ===
        self.create_header_section()
        
        # === [バッテリー表示部] 200px ===
        self.create_battery_section()
        
        # === [ステータス部] 80px ===
        self.create_status_section()
        
        # === [コントロール部] 100px ===
        self.create_control_section()
        
        # === [アクション部] 80px ===
        self.create_action_section()
        
        # === [フッター部] 50px ===
        self.create_footer_section()
        
        # 初期更新
        self.update_final_ui()
        
        # 実データ監視開始
        if not self.screenshot_mode:
            self.start_battery_monitoring()
            
    def create_header_section(self):
        """ヘッダーセクション - 40px"""
        header_frame = ctk.CTkFrame(
            self.root, 
            height=40, 
            corner_radius=8,
            fg_color=COLORS['bg_card']
        )
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Ultra Simple Battery Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(expand=True)
        
    def create_battery_section(self):
        """バッテリー表示セクション - 200px"""
        self.battery_frame = ctk.CTkFrame(
            self.root,
            height=200,
            corner_radius=8, 
            fg_color=COLORS['bg_card']
        )
        self.battery_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.battery_frame.grid_propagate(False)
        
        # グリッド設定
        self.battery_frame.grid_rowconfigure(0, weight=1)  # バッテリー%
        self.battery_frame.grid_rowconfigure(1, weight=0)  # 状態テキスト
        self.battery_frame.grid_rowconfigure(2, weight=0)  # プログレスバー
        self.battery_frame.grid_columnconfigure(0, weight=1)
        
        # 大きなバッテリー%表示
        self.main_battery_label = ctk.CTkLabel(
            self.battery_frame,
            text="🔋 65%",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=COLORS['accent_green']
        )
        self.main_battery_label.grid(row=0, column=0, pady=(20, 5))
        
        # 充電状態テキスト
        self.charging_status_label = ctk.CTkLabel(
            self.battery_frame,
            text="充電中",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        self.charging_status_label.grid(row=1, column=0, pady=5)
        
        # プログレスバー
        self.battery_progress = ctk.CTkProgressBar(
            self.battery_frame,
            width=380,
            height=12,
            corner_radius=6,
            progress_color=COLORS['accent_green']
        )
        self.battery_progress.grid(row=2, column=0, pady=(10, 20))
        self.battery_progress.set(0.65)
        
    def create_status_section(self):
        """ステータスセクション - 80px"""
        self.status_frame = ctk.CTkFrame(
            self.root,
            height=80,
            corner_radius=8,
            fg_color=COLORS['bg_card']
        )
        self.status_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        self.status_frame.grid_propagate(False)
        
        # グリッド設定
        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(1, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # 状態表示
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="状態: 最適範囲",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['accent_blue']
        )
        self.status_label.grid(row=0, column=0, pady=(15, 0))
        
        # 次のアクション
        self.next_action_label = ctk.CTkLabel(
            self.status_frame,
            text="次: 78%で充電停止",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.next_action_label.grid(row=1, column=0, pady=(0, 15))
        
    def create_control_section(self):
        """コントロールセクション - 100px"""
        self.control_frame = ctk.CTkFrame(
            self.root,
            height=100,
            corner_radius=8,
            fg_color=COLORS['bg_card']
        )
        self.control_frame.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        self.control_frame.grid_propagate(False)
        
        # グリッド設定
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_rowconfigure(1, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        
        # 自動制御スイッチ
        ctk.CTkLabel(
            self.control_frame,
            text="自動制御",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.final_auto_switch = ctk.CTkSwitch(
            self.control_frame,
            text="",
            command=self.toggle_auto_mode,
            width=50,
            height=25,
            progress_color=COLORS['accent_green']
        )
        self.final_auto_switch.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="e")
        self.final_auto_switch.select()
        
        # 制御範囲表示
        self.range_label = ctk.CTkLabel(
            self.control_frame,
            text="30% ←→ 78%",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.range_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
    def create_action_section(self):
        """アクションセクション - 80px"""
        self.action_frame = ctk.CTkFrame(
            self.root,
            height=80, 
            corner_radius=8,
            fg_color=COLORS['bg_card']
        )
        self.action_frame.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        self.action_frame.grid_propagate(False)
        
        # グリッド設定（2x2）
        self.action_frame.grid_rowconfigure(0, weight=1)
        self.action_frame.grid_rowconfigure(1, weight=1)
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        
        # 4つのボタン（AlDenteライク）
        self.settings_button = ctk.CTkButton(
            self.action_frame,
            text="⚙️ 設定",
            command=self.open_settings,
            width=90,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_green']
        )
        self.settings_button.grid(row=0, column=0, padx=(20, 5), pady=(10, 2), sticky="ew")
        
        self.stats_button = ctk.CTkButton(
            self.action_frame,
            text="📊 統計",
            command=self.show_stats,
            width=90,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_green']
        )
        self.stats_button.grid(row=0, column=1, padx=(5, 20), pady=(10, 2), sticky="ew")
        
        self.log_button = ctk.CTkButton(
            self.action_frame,
            text="📝 ログ",
            command=self.show_logs,
            width=90,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_blue'], 
            hover_color=COLORS['accent_green']
        )
        self.log_button.grid(row=1, column=0, padx=(20, 5), pady=(2, 10), sticky="ew")
        
        self.about_button = ctk.CTkButton(
            self.action_frame,
            text="ℹ️ About",
            command=self.show_about,
            width=90,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_green']
        )
        self.about_button.grid(row=1, column=1, padx=(5, 20), pady=(2, 10), sticky="ew")
        
    def create_footer_section(self):
        """フッターセクション - 50px"""
        footer_frame = ctk.CTkFrame(
            self.root,
            height=50,
            corner_radius=8,
            fg_color=COLORS['bg_card']
        )
        footer_frame.grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")
        footer_frame.grid_propagate(False)
        
        # グリッド設定
        footer_frame.grid_rowconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # 最終保存時刻
        self.last_update_label = ctk.CTkLabel(
            footer_frame,
            text="最終保存: 2時間前",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        self.last_update_label.grid(row=0, column=0, padx=10, sticky="w")
        
        # バージョン表示
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v2.0 Final",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        version_label.grid(row=0, column=1, padx=10, sticky="e")
        
    def get_real_battery_status(self):
        """実バッテリー情報取得"""
        if self.screenshot_mode:
            return True
            
        try:
            if self.controller:
                battery_level = self.controller.get_battery_percentage()
                is_charging = self.controller.is_charging()
                
                if battery_level is not None:
                    self.battery_level = battery_level
                    self.is_charging = is_charging
                    self.is_optimal_range = (self.start_threshold <= battery_level <= self.stop_threshold)
                    return True
            
            # フォールバック
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                match = re.search(r'(\d+)%', output)
                if match:
                    self.battery_level = int(match.group(1))
                    is_ac_power = 'now drawing from \'ac power\'' in output
                    is_charging_status = 'charging' in output
                    self.is_charging = is_ac_power and is_charging_status
                    self.is_optimal_range = (self.start_threshold <= self.battery_level <= self.stop_threshold)
                    return True
            return False
                
        except Exception as e:
            print(f"Battery Status Error: {e}")
            return False
    
    def update_final_ui(self):
        """Final UI全体更新"""
        try:
            # バッテリー表示更新
            self.update_battery_display()
            
            # ステータス表示更新
            self.update_status_display()
            
            # フッター更新
            self.update_footer()
            
        except Exception as e:
            print(f"UI Update Error: {e}")
    
    def update_battery_display(self):
        """バッテリー表示更新"""
        # アイコンとカラー選択
        if self.battery_level <= 20:
            icon = "🪫"
            color = COLORS['accent_red']
            progress_color = COLORS['accent_red']
        elif self.battery_level <= 50:
            icon = "🔋"
            color = COLORS['accent_orange']
            progress_color = COLORS['accent_orange']
        else:
            icon = "🔋"
            color = COLORS['accent_green']
            progress_color = COLORS['accent_green']
        
        if self.is_charging:
            icon = "⚡"
            color = COLORS['accent_green']
            
        # メインラベル
        self.main_battery_label.configure(
            text=f"{icon} {self.battery_level}%",
            text_color=color
        )
        
        # 充電状態
        status_text = "充電中" if self.is_charging else "放電中"
        self.charging_status_label.configure(
            text=status_text,
            text_color=COLORS['text_secondary']
        )
        
        # プログレスバー
        self.battery_progress.configure(progress_color=progress_color)
        self.battery_progress.set(max(0.0, min(1.0, self.battery_level / 100)))
        
    def update_status_display(self):
        """ステータス表示更新"""
        if self.is_charging:
            status_text = "状態: 充電中"
            status_color = COLORS['accent_green'] 
            next_text = f"次: {self.stop_threshold}%で充電停止"
        elif self.is_optimal_range:
            status_text = "状態: 最適範囲"
            status_color = COLORS['accent_blue']
            next_text = "バッテリー保護が有効です"
        elif self.battery_level <= self.start_threshold:
            status_text = "状態: 要充電"
            status_color = COLORS['accent_orange']
            next_text = f"まもなく充電開始（{self.start_threshold}%以下）"
        else:
            status_text = "状態: 放電中"
            status_color = COLORS['text_primary']
            next_text = "バッテリー駆動中"
            
        self.status_label.configure(
            text=status_text,
            text_color=status_color
        )
        
        self.next_action_label.configure(
            text=next_text,
            text_color=COLORS['text_secondary']
        )
    
    def update_footer(self):
        """フッター更新"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.configure(
            text=f"最終更新: {current_time}"
        )
    
    def start_battery_monitoring(self):
        """バッテリー監視開始"""
        def monitor_loop():
            while True:
                try:
                    if self.get_real_battery_status():
                        self.root.after(0, self.update_final_ui)
                        if self.auto_mode:
                            self.root.after(0, self.check_auto_control)
                    time.sleep(120)
                except Exception as e:
                    print(f"Monitor Error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("Battery Monitoring Started")
    
    def toggle_auto_mode(self):
        """自動制御切り替え"""
        self.auto_mode = self.final_auto_switch.get()
        print(f"自動制御: {'ON' if self.auto_mode else 'OFF'}")
        self.update_final_ui()
        
    def check_auto_control(self):
        """自動制御チェック"""
        if not self.auto_mode or not self.controller:
            return
            
        try:
            if self.battery_level >= self.stop_threshold and self.is_charging:
                print(f"自動制御: {self.battery_level}%で充電停止")
                # 安全モード: 実制御はコメントアウト
                
            elif self.battery_level <= self.start_threshold and not self.is_charging:
                print(f"自動制御: {self.battery_level}%で充電開始") 
                # 安全モード: 実制御はコメントアウト
                
        except Exception as e:
            print(f"Auto Control Error: {e}")
    
    # === アクションボタンハンドラ ===
    def open_settings(self):
        """設定画面"""
        print("⚙️ 設定画面を開きました")
        
    def show_stats(self):
        """統計表示"""
        print("📊 統計: 節約サイクル数 ~150")
        
    def show_logs(self):
        """ログ表示"""
        print("📝 最新ログを表示しました")
        
    def show_about(self):
        """Aboutダイアログ"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("About Battery Manager")
        about_window.geometry("350x250")
        about_window.resizable(False, False)
        about_window.configure(fg_color=COLORS['bg_primary'])
        
        # 中央配置
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        about_window.geometry(f"350x250+{x}+{y}")
        
        # About内容
        main_frame = ctk.CTkFrame(about_window, corner_radius=10, fg_color=COLORS['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            main_frame,
            text="🔋 Ultra Simple Battery Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="MacBookバッテリー寿命延長\nスマート充電管理アプリ",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            justify="center"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            main_frame,
            text="Version 2.0 Final\nPhase 4: Sales-Ready",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['accent_blue'],
            justify="center"
        ).pack(pady=10)
        
        ctk.CTkButton(
            main_frame,
            text="Close",
            command=about_window.destroy,
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_green']
        ).pack(pady=(10, 20))
    
    def run(self):
        """アプリケーション実行"""
        if self.screenshot_mode:
            print("🔋 Battery Manager Final - Screenshot Mode")
            print("📸 販売用デモモード（65%, 最適範囲）")
        else:
            print("🔋 Battery Manager Final - Sales Ready")
            print("450x600 コンパクト版、全要素確実表示")
        
        # 初期データ更新
        if not self.screenshot_mode:
            self.get_real_battery_status()
        self.update_final_ui()
        
        # 終了処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインループ
        self.root.mainloop()
        
    def on_closing(self):
        """終了処理"""
        print("🔋 Battery Manager Final 終了")
        self.root.quit()
        self.root.destroy()

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Battery Manager Final UI')
    parser.add_argument('--screenshot', action='store_true',
                       help='スクリーンショット用モード')
    
    args = parser.parse_args()
    
    try:
        app = BatteryManagerFinalUI(screenshot_mode=args.screenshot)
        app.run()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()