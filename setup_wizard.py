#!/usr/bin/env python3
"""
Battery Manager App - Setup Wizard
初回セットアップウィザード（販売用）
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.current_step = 0
        self.steps = [
            self.welcome_step,
            self.tapo_setup_step,
            self.battery_settings_step,
            self.completion_step
        ]
        self.config_data = {}
        
    def setup_window(self):
        """ウィンドウ設定"""
        self.root.title("Battery Manager - Setup Wizard")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 250
        y = (self.root.winfo_screenheight() // 2) - 200
        self.root.geometry(f"500x400+{x}+{y}")
    
    def welcome_step(self):
        """Step 1: ようこそ画面"""
        self.clear_frame()
        
        welcome_frame = tk.Frame(self.main_frame)
        welcome_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # タイトル
        title = tk.Label(welcome_frame, text="🔋 Battery Manager", 
                        font=('Arial', 24, 'bold'), fg='#2E8B57')
        title.pack(pady=20)
        
        # 説明
        desc = tk.Label(welcome_frame, 
                       text="MacBookのバッテリー寿命を延ばす\nスマート充電管理アプリです。\n\nTapo P110Mスマートプラグと連携して\n自動的に充電を制御します。",
                       font=('Arial', 14), justify='center', fg='#444')
        desc.pack(pady=20)
        
        # 機能説明
        features = tk.Label(welcome_frame,
                           text="✓ 自動充電制御 (30%-78%)\n✓ リアルタイムバッテリー監視\n✓ 安全な充電管理",
                           font=('Arial', 12), justify='left', fg='#666')
        features.pack(pady=15)
        
        self.add_navigation(next_text="セットアップ開始")
    
    def tapo_setup_step(self):
        """Step 2: Tapo設定"""
        self.clear_frame()
        
        tapo_frame = tk.Frame(self.main_frame)
        tapo_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # タイトル
        title = tk.Label(tapo_frame, text="🔌 Tapo P110M設定", 
                        font=('Arial', 18, 'bold'))
        title.pack(pady=10)
        
        # 説明
        desc = tk.Label(tapo_frame, 
                       text="充電器に接続したTapo P110Mの情報を入力してください",
                       font=('Arial', 12), fg='#666')
        desc.pack(pady=10)
        
        # フォーム
        form_frame = tk.Frame(tapo_frame)
        form_frame.pack(pady=20)
        
        # Email
        tk.Label(form_frame, text="Tapoアカウント (Email):", font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=5)
        self.email_entry = tk.Entry(form_frame, width=30, font=('Arial', 11))
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Password
        tk.Label(form_frame, text="パスワード:", font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(form_frame, width=30, show='*', font=('Arial', 11))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Device IP
        tk.Label(form_frame, text="デバイスIP:", font=('Arial', 11)).grid(row=2, column=0, sticky='w', pady=5)
        self.ip_entry = tk.Entry(form_frame, width=30, font=('Arial', 11))
        self.ip_entry.grid(row=2, column=1, padx=10, pady=5)
        self.ip_entry.insert(0, "192.168.0.220")  # デフォルト値
        
        # 接続テストボタン
        test_button = tk.Button(form_frame, text="接続テスト", 
                               command=self.test_tapo_connection,
                               bg='#4CAF50', fg='white', font=('Arial', 10))
        test_button.grid(row=3, column=1, pady=15, sticky='e')
        
        self.add_navigation()
    
    def battery_settings_step(self):
        """Step 3: バッテリー設定"""
        self.clear_frame()
        
        battery_frame = tk.Frame(self.main_frame)
        battery_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # タイトル
        title = tk.Label(battery_frame, text="⚡ バッテリー設定", 
                        font=('Arial', 18, 'bold'))
        title.pack(pady=10)
        
        # 説明
        desc = tk.Label(battery_frame,
                       text="バッテリー寿命を最適化する充電範囲を設定してください",
                       font=('Arial', 12), fg='#666')
        desc.pack(pady=10)
        
        # 設定フレーム
        settings_frame = tk.Frame(battery_frame)
        settings_frame.pack(pady=30)
        
        # 充電開始閾値
        tk.Label(settings_frame, text="充電開始:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=10)
        self.start_var = tk.IntVar(value=30)
        start_scale = tk.Scale(settings_frame, from_=10, to=50, orient='horizontal',
                              variable=self.start_var, length=200)
        start_scale.grid(row=0, column=1, padx=10)
        tk.Label(settings_frame, text="%以下", font=('Arial', 10)).grid(row=0, column=2, sticky='w')
        
        # 充電停止閾値
        tk.Label(settings_frame, text="充電停止:", font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=10)
        self.stop_var = tk.IntVar(value=78)
        stop_scale = tk.Scale(settings_frame, from_=60, to=95, orient='horizontal',
                             variable=self.stop_var, length=200)
        stop_scale.grid(row=1, column=1, padx=10)
        tk.Label(settings_frame, text="%以上", font=('Arial', 10)).grid(row=1, column=2, sticky='w')
        
        # 推奨設定表示
        recommend = tk.Label(battery_frame,
                            text="推奨: 30%で充電開始、78%で充電停止\n（バッテリー寿命を最大化）",
                            font=('Arial', 10), fg='#4CAF50', justify='center')
        recommend.pack(pady=20)
        
        self.add_navigation()
    
    def completion_step(self):
        """Step 4: 完了画面"""
        self.clear_frame()
        
        complete_frame = tk.Frame(self.main_frame)
        complete_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # 完了アイコン
        title = tk.Label(complete_frame, text="✅ セットアップ完了!", 
                        font=('Arial', 20, 'bold'), fg='#4CAF50')
        title.pack(pady=20)
        
        # 設定確認
        summary = tk.Label(complete_frame,
                          text=f"Tapo IP: {self.config_data.get('device_ip', 'N/A')}\n" +
                               f"充電制御: {self.config_data.get('start_threshold', 30)}% ～ {self.config_data.get('stop_threshold', 78)}%",
                          font=('Arial', 12), justify='center')
        summary.pack(pady=15)
        
        # 次のステップ
        next_steps = tk.Label(complete_frame,
                             text="設定が保存されました。\nBattery Managerアプリを起動してご利用ください。",
                             font=('Arial', 11), justify='center', fg='#666')
        next_steps.pack(pady=20)
        
        # 完了ボタン
        finish_button = tk.Button(complete_frame, text="🚀 アプリを起動", 
                                 command=self.finish_setup,
                                 bg='#4CAF50', fg='white', font=('Arial', 14, 'bold'),
                                 width=15, height=2)
        finish_button.pack(pady=20)
    
    def clear_frame(self):
        """フレームクリア"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # メインフレーム作成
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)
    
    def add_navigation(self, next_text="次へ"):
        """ナビゲーションボタン追加"""
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(side='bottom', fill='x', padx=20, pady=20)
        
        # 戻るボタン
        if self.current_step > 0:
            back_button = tk.Button(nav_frame, text="戻る", 
                                   command=self.previous_step,
                                   font=('Arial', 11))
            back_button.pack(side='left')
        
        # 次へボタン
        if self.current_step < len(self.steps) - 1:
            next_button = tk.Button(nav_frame, text=next_text,
                                   command=self.next_step,
                                   bg='#2196F3', fg='white', font=('Arial', 11))
            next_button.pack(side='right')
    
    def next_step(self):
        """次のステップ"""
        if self.validate_current_step():
            self.current_step += 1
            self.steps[self.current_step]()
    
    def previous_step(self):
        """前のステップ"""
        self.current_step -= 1
        self.steps[self.current_step]()
    
    def validate_current_step(self):
        """現在のステップの検証"""
        if self.current_step == 1:  # Tapo設定
            email = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            ip = self.ip_entry.get().strip()
            
            if not all([email, password, ip]):
                messagebox.showerror("エラー", "すべての項目を入力してください")
                return False
                
            # 設定保存
            self.config_data.update({
                'username': email,
                'password': password,
                'device_ip': ip
            })
            
        elif self.current_step == 2:  # バッテリー設定
            start = self.start_var.get()
            stop = self.stop_var.get()
            
            if start >= stop:
                messagebox.showerror("エラー", "充電開始値は停止値より小さくしてください")
                return False
                
            self.config_data.update({
                'start_threshold': start,
                'stop_threshold': stop
            })
            
            # 設定ファイル作成
            self.save_config()
            
        return True
    
    def test_tapo_connection(self):
        """Tapo接続テスト"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        ip = self.ip_entry.get().strip()
        
        if not all([email, password, ip]):
            messagebox.showwarning("警告", "すべての項目を入力してからテストしてください")
            return
            
        # 簡易接続テスト（ping）
        import subprocess
        try:
            result = subprocess.run(['ping', '-c', '1', ip], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                messagebox.showinfo("成功", f"デバイス {ip} に接続できました！")
            else:
                messagebox.showerror("エラー", f"デバイス {ip} に接続できません")
        except Exception as e:
            messagebox.showerror("エラー", f"接続テストに失敗しました: {e}")
    
    def save_config(self):
        """設定ファイル保存"""
        config_content = f'''# Battery Manager App - 設定ファイル

TAPO_SETTINGS = {{
    "username": "{self.config_data['username']}",
    "password": "{self.config_data['password']}",
    "device_ip": "{self.config_data['device_ip']}",
}}

CHARGE_SETTINGS = {{
    "start_threshold": {self.config_data['start_threshold']},
    "stop_threshold": {self.config_data['stop_threshold']},
    "check_interval": 120,
}}

OTHER_SETTINGS = {{
    "debug_mode": False,
    "simulation_mode": False,
}}

ENCRYPTION_PASSWORD = ""
'''
        
        try:
            with open('app_config.py', 'w', encoding='utf-8') as f:
                f.write(config_content)
            print("設定ファイルが作成されました: app_config.py")
        except Exception as e:
            messagebox.showerror("エラー", f"設定ファイルの保存に失敗しました: {e}")
    
    def finish_setup(self):
        """セットアップ完了"""
        try:
            # Battery Manager起動
            import subprocess
            subprocess.Popen(['python3', 'battery_manager_app.py'])
            messagebox.showinfo("完了", "Battery Managerが起動されました！")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("エラー", f"アプリの起動に失敗しました: {e}")
    
    def run(self):
        """ウィザード実行"""
        self.steps[self.current_step]()
        self.root.mainloop()

def main():
    """メイン関数"""
    wizard = SetupWizard()
    wizard.run()

if __name__ == "__main__":
    main()