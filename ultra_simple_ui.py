#!/usr/bin/env python3
"""
Ultra Simple Battery UI - Phase 3 (完成版)
最もシンプルで安全なバッテリー制御UI

Phase 3: バッテリー表示 + 充電制御ボタン + 自動制御ボタン
"""

import tkinter as tk
import subprocess
import re
import asyncio
from datetime import datetime
from battery_charge_controller import BatteryChargeController

class UltraSimpleBatteryUI:
    def __init__(self):
        """初期化 - 最小限の設定"""
        # 基本ウィンドウ作成
        self.root = tk.Tk()
        self.setup_window()
        
        # 状態管理 - 最小限
        self.battery_level = 0
        self.is_charging = False
        self.auto_mode = True  # 自動制御をONにする（重要なバグ修正）
        
        # 🛡️ 定期更新タイマー管理（重複防止）
        self.update_timer_id = None
        
        # バッテリー制御器初期化
        self.controller = BatteryChargeController()
        
        # UI作成
        self.create_ui()
        
        # 初回バッテリー情報取得
        self.update_battery_display()
        
        # 🚨 緊急修正: Tapoデバイス初期化
        self.initialize_tapo_device()
        
        # 定期更新開始
        self.start_periodic_update()
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("🔋 Battery Control")
        self.root.geometry("300x250")
        self.root.resizable(False, False)  # サイズ固定でレイアウト問題回避
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 150
        y = (self.root.winfo_screenheight() // 2) - 125
        self.root.geometry(f"300x250+{x}+{y}")
        
    def create_ui(self):
        """UI要素作成 - Phase 3: バッテリー表示 + 充電制御ボタン + 自動制御ボタン"""
        # メインフレーム
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # バッテリー表示ラベル
        self.battery_label = tk.Label(
            main_frame,
            text="🔋 Battery: ---%",
            font=('Arial', 16, 'bold'),
            justify='center'
        )
        self.battery_label.pack(pady=10)
        
        # 充電制御ボタン
        self.charge_button = tk.Button(
            main_frame,
            text="🔌 充電を開始",
            font=('Arial', 12),
            command=self.toggle_charging,
            width=15,
            height=1
        )
        self.charge_button.pack(pady=5)
        
        # 自動制御ボタン
        self.auto_button = tk.Button(
            main_frame,
            text="🤖 自動制御: ON",
            font=('Arial', 10),
            command=self.toggle_auto_mode,
            width=15,
            height=1,
            bg='lightgreen'
        )
        self.auto_button.pack(pady=5)
        
        # デバッグ情報表示（開発時のみ）
        self.debug_label = tk.Label(
            main_frame,
            text="Phase 3: Complete",
            font=('Arial', 10),
            fg='gray'
        )
        self.debug_label.pack(pady=5)
        
    def get_battery_info(self):
        """バッテリー情報取得 - エラーハンドリング強化"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                print(f"pmset error: {result.stderr}")
                return False
                
            output = result.stdout.lower()
            
            # バッテリーレベル抽出
            match = re.search(r'(\d+)%', output)
            if match:
                self.battery_level = int(match.group(1))
                
                # 充電状態確認（完全修正版）
                # 実際に'charging'状態かつ'AC Power'からの給電の場合のみ充電中と判定
                is_ac_power = 'now drawing from \'ac power\'' in output
                is_charging_status = 'charging' in output
                self.is_charging = is_ac_power and is_charging_status
                
                # デバッグログ追加
                print(f"🔍 Battery Debug: {self.battery_level}%, AC Power: {is_ac_power}, Charging: {is_charging_status}, Final: {self.is_charging}")
                
                return True
            else:
                print("Battery level not found in pmset output")
                return False
                
        except subprocess.TimeoutExpired:
            print("pmset command timeout")
            return False
        except Exception as e:
            print(f"Battery info error: {e}")
            return False
            
    def update_battery_display(self):
        """バッテリー表示更新"""
        try:
            if self.get_battery_info():
                # 正常取得時
                charge_icon = "⚡" if self.is_charging else "🔋"
                self.battery_label.config(text=f"{charge_icon} Battery: {self.battery_level}%")
                
                # 色分け（シンプル）
                if self.battery_level <= 20:
                    self.battery_label.config(fg='red')
                elif self.battery_level <= 50:
                    self.battery_label.config(fg='orange')
                else:
                    self.battery_label.config(fg='green')
                    
                # ボタンテキスト更新
                if self.is_charging:
                    self.charge_button.config(text="🔌 充電を停止")
                else:
                    self.charge_button.config(text="🔌 充電を開始")
                
                # 自動制御実行
                self.check_auto_control()
            else:
                # エラー時の表示
                self.battery_label.config(text="🔋 Battery: Error", fg='gray')
                
        except Exception as e:
            print(f"Display update error: {e}")
            self.battery_label.config(text="🔋 Battery: Error", fg='gray')
    
    def toggle_charging(self):
        """充電制御ボタンの処理"""
        try:
            if self.is_charging:
                # 充電停止
                self.charge_button.config(text="停止中...", state='disabled')
                self.stop_charging()
            else:
                # 充電開始
                self.charge_button.config(text="開始中...", state='disabled')
                self.start_charging()
                
        except Exception as e:
            print(f"Toggle charging error: {e}")
        finally:
            # ボタン再有効化
            self.charge_button.config(state='normal')
            # 状態更新
            self.root.after(2000, self.update_battery_display)
    
    def start_charging(self):
        """充電開始"""
        try:
            # 非同期処理をmain loopで実行
            asyncio.run(self.controller.turn_on_charger())
            print("🔌 充電を開始しました")
        except Exception as e:
            print(f"Start charging error: {e}")
    
    def stop_charging(self):
        """充電停止"""
        try:
            # 非同期処理をmain loopで実行
            asyncio.run(self.controller.turn_off_charger())
            print("🔌 充電を停止しました")
        except Exception as e:
            print(f"Stop charging error: {e}")
    
    def toggle_auto_mode(self):
        """自動制御モードの切り替え"""
        try:
            # 🛡️ ボタン一時無効化（重複クリック防止）
            self.auto_button.config(state='disabled')
            
            self.auto_mode = not self.auto_mode
            if self.auto_mode:
                self.auto_button.config(text="🤖 自動制御: ON", bg='lightgreen')
                print("🤖 自動制御を有効にしました")
                # 🛡️ 自動制御ON時は即座にチェック実行
                self.root.after(1000, self.check_auto_control)
            else:
                self.auto_button.config(text="🤖 自動制御: OFF", bg='lightcoral')
                print("🤖 自動制御を無効にしました")
            
            # 🛡️ 定期更新タイマーをリセット（安全のため）
            self.start_periodic_update()
            
        except Exception as e:
            print(f"Toggle auto mode error: {e}")
        finally:
            # ボタン再有効化
            self.auto_button.config(state='normal')
    
    def check_auto_control(self):
        """自動制御チェック（78%で停止、30%で開始）"""
        if not self.auto_mode:
            return
            
        try:
            # 充電停止条件: 78%以上で充電中
            if self.battery_level >= 78 and self.is_charging:
                print(f"🤖 自動制御: バッテリー{self.battery_level}%で充電停止")
                self.stop_charging()
                
            # 充電開始条件: 30%以下で放電中
            elif self.battery_level <= 30 and not self.is_charging:
                print(f"🤖 自動制御: バッテリー{self.battery_level}%で充電開始")
                self.start_charging()
                
        except Exception as e:
            print(f"Auto control error: {e}")
    
    def initialize_tapo_device(self):
        """🚨 緊急修正: Tapoデバイス初期化"""
        try:
            from config import TAPO_SETTINGS
            
            # 認証情報設定
            self.controller.tapo_username = TAPO_SETTINGS['username']
            self.controller.tapo_password = TAPO_SETTINGS['password'] 
            self.controller.device_ip = TAPO_SETTINGS['device_ip']
            
            # 非同期初期化を同期的に実行
            asyncio.run(self.controller.init_tapo_device())
            print("🔌 Tapo P110M初期化完了")
            
        except Exception as e:
            print(f"🚨 Tapo初期化エラー: {e}")
    
    def start_periodic_update(self):
        """定期更新開始（120秒間隔）+ 健全性チェック"""
        # 🛡️ 既存のタイマーをキャンセル（重複防止）
        if self.update_timer_id is not None:
            self.root.after_cancel(self.update_timer_id)
            self.update_timer_id = None
        
        # バッテリー情報更新
        self.update_battery_display()
        
        # 🛡️ 健全性チェック機能追加
        self.health_check()
        
        # 120秒後に再実行（タイマーID保存）
        self.update_timer_id = self.root.after(120000, self.start_periodic_update)
        print(f"🛡️ Periodic Update: Timer set (ID: {self.update_timer_id})")
    
    def health_check(self):
        """🛡️ プロセス健全性チェック"""
        try:
            import os
            import time
            
            # 現在時刻をログ
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # PIDファイル更新（生存確認用）
            pid_file = os.path.expanduser("~/.battery_ui_health.pid")
            with open(pid_file, 'w') as f:
                f.write(f"{os.getpid()}:{current_time}\n")
            
            # 自動制御の動作確認
            if self.auto_mode and self.battery_level <= 30 and not self.is_charging:
                print(f"🛡️ Health Check: Battery {self.battery_level}% - Auto charging should activate")
            elif self.auto_mode and self.battery_level >= 78 and self.is_charging:
                print(f"🛡️ Health Check: Battery {self.battery_level}% - Auto charging should stop")
            
            print(f"🛡️ Health Check: {current_time} - System OK")
            
        except Exception as e:
            print(f"🚨 Health Check Error: {e}")
            
    def run(self):
        """アプリケーション実行"""
        try:
            print("🔋 Ultra Simple Battery UI - Phase 3 起動（完成版）")
            print("Phase 3: バッテリー表示 + 充電制御ボタン + 自動制御ボタン")
            
            # 終了処理設定
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # メインループ開始
            self.root.mainloop()
            
        except Exception as e:
            print(f"Application error: {e}")
            
    def on_closing(self):
        """終了処理"""
        print("🔋 Ultra Simple Battery UI 終了")
        self.root.quit()
        self.root.destroy()

def main():
    """メイン関数"""
    try:
        app = UltraSimpleBatteryUI()
        app.run()
    except Exception as e:
        print(f"Main error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()