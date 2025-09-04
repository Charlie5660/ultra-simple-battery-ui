#!/usr/bin/env python3
"""
CustomTkinter Test App
Battery Manager UI改良のテストアプリ
"""

import customtkinter as ctk

class CustomTkinterTest:
    def __init__(self):
        """初期化"""
        # CustomTkinter設定
        ctk.set_appearance_mode("dark")  # ダークモード設定
        ctk.set_default_color_theme("green")  # テーマ設定
        
        # メインウィンドウ作成
        self.root = ctk.CTk()
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """ウィンドウ設定"""
        self.root.title("Battery Manager - UI Test")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 300
        y = (self.root.winfo_screenheight() // 2) - 200
        self.root.geometry(f"600x400+{x}+{y}")
    
    def create_ui(self):
        """UI要素作成"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # タイトルラベル
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔋 CustomTkinter Test",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 説明ラベル
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Battery Manager UI改良テスト\nCustomTkinterライブラリの動作確認",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # テスト用ボタン
        test_button = ctk.CTkButton(
            main_frame,
            text="🚀 テストボタン",
            command=self.button_clicked,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        test_button.pack(pady=20)
        
        # ステータス表示
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="テスト準備完了",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=10)
        
        # プログレスバー（テスト用）
        self.progress = ctk.CTkProgressBar(main_frame, width=300)
        self.progress.pack(pady=20)
        self.progress.set(0.7)  # 70%で表示
        
        # テスト用スイッチ
        self.switch_var = ctk.StringVar(value="on")
        test_switch = ctk.CTkSwitch(
            main_frame,
            text="自動モード",
            command=self.switch_toggled,
            variable=self.switch_var,
            onvalue="on",
            offvalue="off"
        )
        test_switch.pack(pady=10)
    
    def button_clicked(self):
        """ボタンクリック処理"""
        print("Button clicked")
        self.status_label.configure(text="✅ ボタンがクリックされました")
        # プログレスバーアニメーション
        self.animate_progress()
    
    def switch_toggled(self):
        """スイッチ切り替え処理"""
        state = self.switch_var.get()
        print(f"Switch toggled: {state}")
        self.status_label.configure(text=f"🔄 自動モード: {state.upper()}")
    
    def animate_progress(self):
        """プログレスバーアニメーション"""
        import threading
        import time
        
        def animate():
            for i in range(11):
                progress_value = i / 10
                self.progress.set(progress_value)
                time.sleep(0.1)
        
        # 別スレッドでアニメーション実行
        threading.Thread(target=animate, daemon=True).start()
    
    def run(self):
        """アプリケーション実行"""
        print("🔋 CustomTkinter Test App 起動")
        print("ダークモード + モダンUI テスト")
        self.root.mainloop()
        print("🔋 CustomTkinter Test App 終了")

def main():
    """メイン関数"""
    try:
        app = CustomTkinterTest()
        app.run()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()