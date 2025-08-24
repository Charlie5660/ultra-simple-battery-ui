#!/usr/bin/env python3
"""
Ultra Simple Battery UI - Phase 2
最もシンプルで安全なバッテリー制御UI

Phase 2: バッテリー表示 + 充電制御ボタン
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
        
        # バッテリー制御器初期化
        self.controller = BatteryChargeController()
        
        # UI作成
        self.create_ui()
        
        # 初回バッテリー情報取得
        self.update_battery_display()
        
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("🔋 Battery Control")
        self.root.geometry("300x200")
        self.root.resizable(False, False)  # サイズ固定でレイアウト問題回避
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 150
        y = (self.root.winfo_screenheight() // 2) - 100
        self.root.geometry(f"300x200+{x}+{y}")
        
    def create_ui(self):
        """UI要素作成 - Phase 2: バッテリー表示 + 充電制御ボタン"""
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
        self.charge_button.pack(pady=10)
        
        # デバッグ情報表示（開発時のみ）
        self.debug_label = tk.Label(
            main_frame,
            text="Phase 2: Display + Control",
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
                
                # 充電状態確認
                self.is_charging = 'charging' in output or 'ac power' in output
                
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
            
    def run(self):
        """アプリケーション実行"""
        try:
            print("🔋 Ultra Simple Battery UI - Phase 2 起動")
            print("Phase 2: バッテリー表示 + 充電制御ボタン")
            
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