#!/usr/bin/env python3
"""
Battery Manager - CustomTkinter UI Version
Ultra Simple Battery Manager with Modern UI
Phase 2: 基本UIコンポーネント移行版
"""

import customtkinter as ctk
import threading
import time

class BatteryManagerCustomUI:
    def __init__(self):
        """初期化"""
        # CustomTkinter設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # 仮データ（実際の制御機能は後で接続）
        self.battery_level = 65  # 仮の残量
        self.is_charging = False
        self.auto_mode = True
        self.start_threshold = 30
        self.stop_threshold = 78
        
        # メインウィンドウ作成
        self.root = ctk.CTk()
        self.setup_window()
        self.create_ui()
        
    def setup_window(self):
        """ウィンドウ設定"""
        self.root.title("🔋 Ultra Simple Battery Manager")
        self.root.geometry("800x500")
        self.root.resizable(False, False)
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 400
        y = (self.root.winfo_screenheight() // 2) - 250
        self.root.geometry(f"800x500+{x}+{y}")
    
    def create_ui(self):
        """UI作成"""
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
            text="🔋 65%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.battery_label.pack(side='left', padx=20)
        
        # 充電状態
        self.charging_label = ctk.CTkLabel(
            battery_info_frame,
            text="⚡ 放電中",
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
        self.progress_bar.set(0.65)  # 65%
        
        # 設定値表示
        settings_label = ctk.CTkLabel(
            progress_container,
            text=f"⚡ 制御範囲: {self.start_threshold}% ～ {self.stop_threshold}%",
            font=ctk.CTkFont(size=14),
            text_color="#81C784"
        )
        settings_label.pack()
    
    def toggle_auto_mode(self):
        """自動制御モード切り替え"""
        self.auto_mode = self.auto_switch.get()
        print(f"自動制御: {'ON' if self.auto_mode else 'OFF'}")
        self.update_status()
        
    def toggle_charging(self):
        """充電開始/停止切り替え"""
        self.is_charging = not self.is_charging
        print(f"手動制御: 充電{'開始' if self.is_charging else '停止'}")
        self.update_ui()
        
    def stop_charging(self):
        """充電停止"""
        self.is_charging = False
        print("手動制御: 充電停止")
        self.update_ui()
        
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
        """UI全体更新"""
        # バッテリー残量更新
        color = "#4CAF50" if self.battery_level > 30 else "#F44336"
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
        self.progress_bar.set(self.battery_level / 100)
        
        # ステータス更新
        self.update_status()
    
    def simulate_battery_change(self):
        """バッテリー変化シミュレーション（デモ用）"""
        def battery_simulation():
            while True:
                if self.is_charging and self.battery_level < 100:
                    self.battery_level += 1
                elif not self.is_charging and self.battery_level > 0:
                    self.battery_level -= 1
                
                # 自動制御シミュレーション
                if self.auto_mode:
                    if self.battery_level >= self.stop_threshold and self.is_charging:
                        self.is_charging = False
                        print(f"🤖 自動制御: {self.stop_threshold}%で充電停止")
                    elif self.battery_level <= self.start_threshold and not self.is_charging:
                        self.is_charging = True
                        print(f"🤖 自動制御: {self.start_threshold}%で充電開始")
                
                # UI更新（メインスレッドで実行）
                self.root.after(0, self.update_ui)
                time.sleep(2)  # 2秒間隔で更新
        
        # バックグラウンドでシミュレーション実行
        simulation_thread = threading.Thread(target=battery_simulation, daemon=True)
        simulation_thread.start()
    
    def run(self):
        """アプリケーション実行"""
        print("🔋 Ultra Simple Battery Manager - CustomTkinter版 起動")
        print("Phase 2: 基本UIコンポーネント移行完了")
        
        # デモ用シミュレーション開始
        self.simulate_battery_change()
        
        # 終了処理設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインループ開始
        self.root.mainloop()
        
    def on_closing(self):
        """終了処理"""
        print("🔋 Ultra Simple Battery Manager 終了")
        self.root.quit()
        self.root.destroy()

def main():
    """メイン関数"""
    try:
        app = BatteryManagerCustomUI()
        app.run()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()