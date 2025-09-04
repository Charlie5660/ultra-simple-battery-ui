#!/usr/bin/env python3
"""
Battery Manager - CustomTkinter UI + Core Integration
Ultra Simple Battery Manager with Modern UI + Real Battery Control
Phase 3: コア機能統合版
"""

import customtkinter as ctk
import threading
import time
import subprocess
import re
import asyncio
import sys
from datetime import datetime

# 親ディレクトリからコア機能をインポート（読み取り専用）
sys.path.append('..')
try:
    from battery_controller_core import BatteryChargeController
    from app_config import TAPO_SETTINGS, CHARGE_SETTINGS, OTHER_SETTINGS
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"警告: コア機能インポートエラー: {e}")
    CORE_AVAILABLE = False

class BatteryManagerIntegratedUI:
    def __init__(self):
        """初期化 - CustomTkinter + Real Battery Control"""
        # CustomTkinter設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # 実データ初期化
        self.battery_level = 0
        self.is_charging = False
        self.auto_mode = True
        self.start_threshold = CHARGE_SETTINGS.get("start_threshold", 30)
        self.stop_threshold = CHARGE_SETTINGS.get("stop_threshold", 78)
        
        # 🛡️ コア機能初期化（安全性重視）
        self.controller = None
        if CORE_AVAILABLE:
            try:
                self.controller = BatteryChargeController()
                # 設定値を適用
                self.controller.charge_start_threshold = self.start_threshold
                self.controller.charge_stop_threshold = self.stop_threshold
                print("✅ Battery Controller Core 初期化完了")
            except Exception as e:
                print(f"🚨 Controller初期化エラー: {e}")
                self.controller = None
        
        # メインウィンドウ作成
        self.root = ctk.CTk()
        self.setup_window()
        self.create_ui()
        
        # 🛡️ Tapo初期化（最初はコメントアウト - 安全のため）
        # self.initialize_tapo_device()
        
    def setup_window(self):
        """ウィンドウ設定"""
        self.root.title("🔋 Ultra Simple Battery Manager - Integrated")
        self.root.geometry("800x500")
        self.root.resizable(False, False)
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 400
        y = (self.root.winfo_screenheight() // 2) - 250
        self.root.geometry(f"800x500+{x}+{y}")
    
    def create_ui(self):
        """UI作成 - Phase 3: 統合版"""
        # メインコンテナ
        main_container = ctk.CTkFrame(self.root, corner_radius=10)
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # === 上部：ステータス表示エリア ===
        self.create_status_section(main_container)
        
        # === 中央：コントロールエリア ===
        self.create_control_section(main_container)
        
        # === 下部：情報表示エリア ===
        self.create_info_section(main_container)
        
        # 初期更新
        self.update_ui()
        # 🛡️ 実データ取得開始
        self.start_real_battery_monitoring()
        
    def create_status_section(self, parent):
        """ステータス表示セクション作成"""
        status_frame = ctk.CTkFrame(parent, height=120, corner_radius=8)
        status_frame.pack(fill='x', padx=10, pady=(10, 5))
        status_frame.pack_propagate(False)
        
        # セクションタイトル
        title_label = ctk.CTkLabel(
            status_frame,
            text="📊 バッテリー状態",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # バッテリー情報コンテナ
        battery_info_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        battery_info_frame.pack(fill='x', padx=20)
        
        # バッテリー残量
        self.battery_label = ctk.CTkLabel(
            battery_info_frame,
            text="🔋 ---%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.battery_label.pack(side='left', padx=20)
        
        # 充電状態
        self.charging_label = ctk.CTkLabel(
            battery_info_frame,
            text="⚡ 確認中",
            font=ctk.CTkFont(size=16),
            text_color="#FFA726"
        )
        self.charging_label.pack(side='right', padx=20)
        
    def create_control_section(self, parent):
        """コントロールセクション作成"""
        control_frame = ctk.CTkFrame(parent, height=180, corner_radius=8)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)
        
        # セクションタイトル
        title_label = ctk.CTkLabel(
            control_frame,
            text="⚙️ 制御設定",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 20))
        
        # コントロールコンテナ
        controls_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        controls_container.pack(fill='x', padx=40)
        
        # 自動制御スイッチ
        auto_control_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        auto_control_frame.pack(fill='x', pady=10)
        
        ctk.CTkLabel(
            auto_control_frame,
            text="🤖 自動制御:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side='left')
        
        self.auto_switch = ctk.CTkSwitch(
            auto_control_frame,
            text="",
            command=self.toggle_auto_mode,
            width=60,
            height=28,
            button_length=40
        )
        self.auto_switch.pack(side='right')
        self.auto_switch.select()  # 初期状態ON
        
        # 状態表示
        self.status_label = ctk.CTkLabel(
            controls_container,
            text="✅ アクティブ - 自動制御中",
            font=ctk.CTkFont(size=14),
            text_color="#4CAF50"
        )
        self.status_label.pack(pady=(10, 0))
        
        # 手動制御ボタン
        manual_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        manual_frame.pack(fill='x', pady=(15, 0))
        
        self.charge_button = ctk.CTkButton(
            manual_frame,
            text="🔌 充電開始",
            command=self.toggle_charging,
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.charge_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ctk.CTkButton(
            manual_frame,
            text="🛑 充電停止",
            command=self.stop_charging,
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        self.stop_button.pack(side='right', padx=(10, 0))
        
    def create_info_section(self, parent):
        """情報表示セクション作成"""
        info_frame = ctk.CTkFrame(parent, height=140, corner_radius=8)
        info_frame.pack(fill='x', padx=10, pady=(5, 10))
        info_frame.pack_propagate(False)
        
        # セクションタイトル
        title_label = ctk.CTkLabel(
            info_frame,
            text="📈 システム情報",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # プログレスバーコンテナ
        progress_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        progress_container.pack(fill='x', padx=30, pady=10)
        
        # バッテリー残量プログレスバー
        ctk.CTkLabel(
            progress_container,
            text="バッテリー残量:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor='w')
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            width=400,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar.set(0.0)  # 初期値
        
        # 設定値表示
        self.settings_label = ctk.CTkLabel(
            progress_container,
            text=f"⚡ 制御範囲: {self.start_threshold}% ～ {self.stop_threshold}%",
            font=ctk.CTkFont(size=14),
            text_color="#81C784"
        )
        self.settings_label.pack()
    
    def get_real_battery_status(self):
        """🔋 実際のバッテリー情報取得"""
        try:
            if self.controller:
                # コア機能を使用して取得
                battery_level = self.controller.get_battery_percentage()
                is_charging = self.controller.is_charging()
                
                if battery_level is not None:
                    self.battery_level = battery_level
                    self.is_charging = is_charging
                    return True
            
            # フォールバック: 直接pmset実行
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return False
                
            output = result.stdout.lower()
            
            # バッテリーレベル抽出
            match = re.search(r'(\d+)%', output)
            if match:
                self.battery_level = int(match.group(1))
                
                # 充電状態確認（精密判定）
                is_ac_power = 'now drawing from \'ac power\'' in output
                is_charging_status = 'charging' in output
                self.is_charging = is_ac_power and is_charging_status
                
                return True
                
            return False
                
        except Exception as e:
            print(f"🚨 Battery Status Error: {e}")
            return False
    
    def start_real_battery_monitoring(self):
        """🛡️ 実バッテリー監視開始（120秒間隔）"""
        def monitor_loop():
            while True:
                try:
                    if self.get_real_battery_status():
                        # UIを安全に更新
                        self.root.after(0, self.update_ui)
                        
                        # 自動制御チェック
                        if self.auto_mode:
                            self.root.after(0, self.check_auto_control)
                    
                    time.sleep(120)  # 120秒間隔
                    
                except Exception as e:
                    print(f"🚨 Monitor Loop Error: {e}")
                    time.sleep(60)  # エラー時は60秒待機
        
        # バックグラウンドで監視開始
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("🛡️ Real Battery Monitoring Started (120s interval)")
    
    def toggle_auto_mode(self):
        """自動制御モード切り替え"""
        self.auto_mode = self.auto_switch.get()
        print(f"🤖 自動制御: {'ON' if self.auto_mode else 'OFF'}")
        self.update_status()
        
    def check_auto_control(self):
        """🤖 自動制御チェック（実機能統合）"""
        if not self.auto_mode or not self.controller:
            return
            
        try:
            # 充電停止条件: 78%以上で充電中
            if self.battery_level >= self.stop_threshold and self.is_charging:
                print(f"🤖 自動制御: バッテリー{self.battery_level}%で充電停止")
                # 🚨 Tapo制御は最初はコメントアウト（安全のため）
                # asyncio.run(self.controller.turn_off_charger())
                print("🚨 安全モード: 実際の充電停止はコメントアウト中")
                
            # 充電開始条件: 30%以下で放電中
            elif self.battery_level <= self.start_threshold and not self.is_charging:
                print(f"🤖 自動制御: バッテリー{self.battery_level}%で充電開始")
                # 🚨 Tapo制御は最初はコメントアウト（安全のため）
                # asyncio.run(self.controller.turn_on_charger())
                print("🚨 安全モード: 実際の充電開始はコメントアウト中")
                
        except Exception as e:
            print(f"🚨 Auto Control Error: {e}")
    
    def toggle_charging(self):
        """充電開始/停止切り替え（手動制御）"""
        if not self.controller:
            print("🚨 Controller未初期化 - シミュレーションモード")
            self.is_charging = not self.is_charging
            self.update_ui()
            return
            
        try:
            self.charge_button.configure(text="処理中...", state="disabled")
            
            if self.is_charging:
                # 🚨 実制御は最初はコメントアウト
                # asyncio.run(self.controller.turn_off_charger())
                print("🚨 安全モード: 手動充電停止はコメントアウト中")
            else:
                # 🚨 実制御は最初はコメントアウト
                # asyncio.run(self.controller.turn_on_charger())
                print("🚨 安全モード: 手動充電開始はコメントアウト中")
                
            # 2秒後にUI更新
            self.root.after(2000, self.update_ui)
            
        except Exception as e:
            print(f"🚨 Manual Control Error: {e}")
        finally:
            self.charge_button.configure(state="normal")
    
    def stop_charging(self):
        """充電停止（専用ボタン）"""
        if not self.controller:
            print("🚨 Controller未初期化 - シミュレーションモード")
            self.is_charging = False
            self.update_ui()
            return
            
        try:
            self.stop_button.configure(text="停止中...", state="disabled")
            
            # 🚨 実制御は最初はコメントアウト
            # asyncio.run(self.controller.turn_off_charger())
            print("🚨 安全モード: 充電停止はコメントアウト中")
            
            # 2秒後にUI更新
            self.root.after(2000, self.update_ui)
            
        except Exception as e:
            print(f"🚨 Stop Charging Error: {e}")
        finally:
            self.stop_button.configure(state="normal")
    
    def update_status(self):
        """ステータス表示更新"""
        if self.auto_mode:
            self.status_label.configure(
                text="✅ アクティブ - 自動制御中",
                text_color="#4CAF50"
            )
        else:
            self.status_label.configure(
                text="⏸️ 停止中 - 手動制御",
                text_color="#FF9800"
            )
    
    def update_ui(self):
        """UI全体更新 - 実データ反映"""
        try:
            # バッテリー残量更新
            if self.battery_level <= 20:
                icon = "🪫"
                color = "#F44336"
            elif self.battery_level <= 50:
                icon = "🔋"
                color = "#FF9800"
            else:
                icon = "🔋"
                color = "#4CAF50"
                
            self.battery_label.configure(
                text=f"{icon} {self.battery_level}%",
                text_color=color
            )
            
            # 充電状態更新
            if self.is_charging:
                self.charging_label.configure(
                    text="⚡ 充電中",
                    text_color="#4CAF50"
                )
                self.charge_button.configure(text="🔌 充電停止")
            else:
                self.charging_label.configure(
                    text="🔋 放電中",
                    text_color="#FFA726"
                )
                self.charge_button.configure(text="🔌 充電開始")
            
            # プログレスバー更新
            self.progress_bar.set(max(0.0, min(1.0, self.battery_level / 100)))
            
            # ステータス更新
            self.update_status()
            
            # デバッグ情報（コンソール出力）
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"🔍 [{timestamp}] UI Update: {self.battery_level}%, Charging: {self.is_charging}")
            
        except Exception as e:
            print(f"🚨 UI Update Error: {e}")
    
    def initialize_tapo_device(self):
        """🚨 Tapoデバイス初期化（最初は無効化）"""
        if not self.controller:
            print("🚨 Controller未初期化")
            return False
            
        try:
            # 設定から認証情報取得
            self.controller.tapo_username = TAPO_SETTINGS.get('username', '')
            self.controller.tapo_password = TAPO_SETTINGS.get('password', '')
            self.controller.device_ip = TAPO_SETTINGS.get('device_ip', '')
            
            # 🚨 実際の初期化は最初はコメントアウト
            # asyncio.run(self.controller.init_tapo_device())
            print("🚨 安全モード: Tapo初期化はコメントアウト中")
            return True
            
        except Exception as e:
            print(f"🚨 Tapo初期化エラー: {e}")
            return False
    
    def run(self):
        """アプリケーション実行"""
        print("🔋 Ultra Simple Battery Manager - Integrated 起動")
        print("Phase 3: コア機能統合版（安全モード）")
        print("🚨 実制御機能は初期はコメントアウト状態")
        
        # 初回バッテリー情報取得
        self.get_real_battery_status()
        self.update_ui()
        
        # 終了処理設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインループ開始
        self.root.mainloop()
        
    def on_closing(self):
        """終了処理"""
        print("🔋 Ultra Simple Battery Manager - Integrated 終了")
        self.root.quit()
        self.root.destroy()

def main():
    """メイン関数"""
    try:
        app = BatteryManagerIntegratedUI()
        app.run()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()