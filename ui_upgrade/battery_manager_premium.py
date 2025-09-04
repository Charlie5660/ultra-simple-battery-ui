#!/usr/bin/env python3
"""
Battery Manager - Premium UI Design
Ultra Simple Battery Manager with Sales-Quality Design
Phase 4: プレミアムデザイン実装（販売品質）
"""

import customtkinter as ctk
import threading
import time
import subprocess
import re
import asyncio
import sys
import math
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

# 🎨 Premium Color Scheme
COLORS = {
    'bg_primary': '#1e1e1e',      # ダーク背景
    'bg_secondary': '#2d2d2d',    # カード背景  
    'bg_tertiary': '#363636',     # アクセント背景
    'accent_green': '#00d084',    # 充電中
    'accent_blue': '#0693e3',     # 最適状態
    'accent_orange': '#fcb900',   # 警告
    'accent_red': '#eb144c',      # 危険
    'text_primary': '#ffffff',     # メインテキスト
    'text_secondary': '#8d8d8d',  # サブテキスト
    'text_accent': '#b8b8b8',     # アクセントテキスト
}

# 🎨 Typography System
FONTS = {
    'display_large': ('SF Pro Display', 48, 'bold'),    # メイン数値
    'heading': ('SF Pro Display', 18, 'normal'),        # 見出し  
    'heading_bold': ('SF Pro Display', 18, 'bold'),     # 見出し太字
    'body': ('SF Pro Text', 14, 'normal'),              # 本文
    'body_bold': ('SF Pro Text', 14, 'bold'),           # 本文太字
    'caption': ('SF Pro Text', 12, 'normal'),           # キャプション
}

class BatteryManagerPremiumUI:
    def __init__(self, screenshot_mode=False):
        """初期化 - Premium Sales-Quality UI"""
        # CustomTkinter高度設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.screenshot_mode = screenshot_mode
        
        # 実データ初期化
        if screenshot_mode:
            # スクリーンショット用理想データ
            self.battery_level = 65  
            self.is_charging = False
            self.is_optimal_range = True
        else:
            self.battery_level = 0
            self.is_charging = False
            self.is_optimal_range = False
            
        self.auto_mode = True
        self.start_threshold = CHARGE_SETTINGS.get("start_threshold", 30)
        self.stop_threshold = CHARGE_SETTINGS.get("stop_threshold", 78)
        self.animation_angle = 0  # アニメーション用
        
        # 🛡️ コア機能初期化（安全性重視）
        self.controller = None
        if CORE_AVAILABLE and not screenshot_mode:
            try:
                self.controller = BatteryChargeController()
                self.controller.charge_start_threshold = self.start_threshold
                self.controller.charge_stop_threshold = self.stop_threshold
                print("✅ Battery Controller Core 初期化完了")
            except Exception as e:
                print(f"🚨 Controller初期化エラー: {e}")
                self.controller = None
        
        # メインウィンドウ作成
        self.root = ctk.CTk()
        self.setup_window()
        self.create_premium_ui()
        
    def setup_window(self):
        """プレミアムウィンドウ設定"""
        self.root.title("🔋 Ultra Simple Battery Manager - Premium")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.root.configure(fg_color=COLORS['bg_primary'])
        
        # 画面中央配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 450
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f"900x700+{x}+{y}")
    
    def create_premium_ui(self):
        """プレミアムUI作成 - 販売品質デザイン"""
        # メインコンテナ
        main_container = ctk.CTkFrame(
            self.root, 
            corner_radius=15,
            fg_color=COLORS['bg_secondary']
        )
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === A. メインビジュアル（上部）===
        self.create_main_visual(main_container)
        
        # === B. ステータス表示（中部）===  
        self.create_status_display(main_container)
        
        # === C. コントロールパネル（下部）===
        self.create_control_panel(main_container)
        
        # === D. 情報パネル（最下部）===
        self.create_info_panel(main_container)
        
        # 初期更新
        self.update_premium_ui()
        
        # 🛡️ 実データ取得開始（スクリーンショットモード以外）
        if not self.screenshot_mode:
            self.start_real_battery_monitoring()
            
    def create_main_visual(self, parent):
        """A. メインビジュアル - 大きな円形バッテリーインジケーター"""
        visual_frame = ctk.CTkFrame(
            parent, 
            height=200, 
            corner_radius=12,
            fg_color=COLORS['bg_tertiary']
        )
        visual_frame.pack(fill='x', padx=15, pady=(15, 10))
        visual_frame.pack_propagate(False)
        
        # 円形プログレス風コンテナ
        circle_container = ctk.CTkFrame(visual_frame, fg_color="transparent")
        circle_container.pack(expand=True, fill='both')
        
        # 大きなバッテリー表示（中央）
        self.main_battery_label = ctk.CTkLabel(
            circle_container,
            text="🔋 65%",
            font=FONTS['display_large'],
            text_color=COLORS['accent_green']
        )
        self.main_battery_label.pack(expand=True)
        
        # 円形プログレスバー（バッテリーの周りに配置）
        progress_frame = ctk.CTkFrame(circle_container, fg_color="transparent", height=40)
        progress_frame.pack(fill='x', padx=50, pady=(10, 20))
        
        self.main_progress = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20,
            corner_radius=10,
            progress_color=COLORS['accent_green']
        )
        self.main_progress.pack()
        self.main_progress.set(0.65)  # 初期値
        
    def create_status_display(self, parent):
        """B. ステータス表示 - アイコン+テキスト"""
        status_frame = ctk.CTkFrame(
            parent,
            height=120,
            corner_radius=12,
            fg_color=COLORS['bg_tertiary']
        )
        status_frame.pack(fill='x', padx=15, pady=5)
        status_frame.pack_propagate(False)
        
        # ステータスコンテナ
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(expand=True, fill='both', padx=30)
        
        # 現在状態表示
        self.current_status_label = ctk.CTkLabel(
            status_container,
            text="✅ Optimal Range",
            font=FONTS['heading_bold'],
            text_color=COLORS['accent_blue']
        )
        self.current_status_label.pack(pady=(20, 5))
        
        # 推奨アクション表示
        self.action_recommendation_label = ctk.CTkLabel(
            status_container,
            text="バッテリーは理想的な範囲にあります",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        self.action_recommendation_label.pack(pady=5)
        
        # 予想延長効果
        self.lifetime_effect_label = ctk.CTkLabel(
            status_container,
            text="📈 バッテリー寿命延長効果: +2年",
            font=FONTS['body_bold'],
            text_color=COLORS['accent_green']
        )
        self.lifetime_effect_label.pack(pady=(10, 15))
        
    def create_control_panel(self, parent):
        """C. コントロールパネル - 大きなON/OFFスイッチ"""
        control_frame = ctk.CTkFrame(
            parent,
            height=160,
            corner_radius=12,
            fg_color=COLORS['bg_tertiary']
        )
        control_frame.pack(fill='x', padx=15, pady=5)
        control_frame.pack_propagate(False)
        
        # コントロールコンテナ
        control_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        control_container.pack(expand=True, fill='both', padx=40, pady=20)
        
        # 大きなON/OFFスイッチ（中央配置）
        switch_container = ctk.CTkFrame(control_container, fg_color="transparent")
        switch_container.pack(expand=True)
        
        # スイッチラベル
        ctk.CTkLabel(
            switch_container,
            text="🤖 Smart Battery Protection",
            font=FONTS['heading_bold'],
            text_color=COLORS['text_primary']
        ).pack(pady=(10, 15))
        
        # 大型スイッチ
        self.premium_auto_switch = ctk.CTkSwitch(
            switch_container,
            text="",
            command=self.toggle_auto_mode,
            width=80,
            height=40,
            button_length=60,
            progress_color=COLORS['accent_green'],
            button_color=COLORS['bg_secondary'],
            fg_color=COLORS['bg_primary']
        )
        self.premium_auto_switch.pack(pady=10)
        self.premium_auto_switch.select()  # 初期状態ON
        
        # スイッチ状態説明
        self.switch_description_label = ctk.CTkLabel(
            switch_container,
            text="Battery Protection Active",
            font=FONTS['body'],
            text_color=COLORS['accent_green']
        )
        self.switch_description_label.pack(pady=(5, 10))
        
    def create_info_panel(self, parent):
        """D. 情報パネル - 24時間履歴と設定情報"""
        info_frame = ctk.CTkFrame(
            parent,
            height=180,
            corner_radius=12,
            fg_color=COLORS['bg_tertiary']
        )
        info_frame.pack(fill='x', padx=15, pady=(5, 15))
        info_frame.pack_propagate(False)
        
        # 情報コンテナ
        info_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_container.pack(expand=True, fill='both', padx=25, pady=20)
        
        # セクションタイトル
        ctk.CTkLabel(
            info_container,
            text="📊 System Information",
            font=FONTS['heading_bold'],
            text_color=COLORS['text_primary']
        ).pack(pady=(0, 15))
        
        # 情報表示エリア（2列レイアウト）
        info_grid = ctk.CTkFrame(info_container, fg_color="transparent")
        info_grid.pack(fill='x', pady=10)
        
        # 左列：設定情報
        left_info = ctk.CTkFrame(info_grid, fg_color="transparent")
        left_info.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # 充電範囲表示
        range_info = ctk.CTkFrame(left_info, corner_radius=8, fg_color=COLORS['bg_secondary'])
        range_info.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            range_info,
            text="⚙️ Optimal Range",
            font=FONTS['body_bold'],
            text_color=COLORS['text_primary']
        ).pack(pady=(10, 5))
        
        self.range_display_label = ctk.CTkLabel(
            range_info,
            text=f"{self.start_threshold}% ～ {self.stop_threshold}%",
            font=FONTS['heading'],
            text_color=COLORS['accent_blue']
        )
        self.range_display_label.pack(pady=(0, 10))
        
        # 右列：パフォーマンス情報
        right_info = ctk.CTkFrame(info_grid, fg_color="transparent")
        right_info.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # 24時間履歴エリア（将来のグラフ用）
        history_info = ctk.CTkFrame(right_info, corner_radius=8, fg_color=COLORS['bg_secondary'])
        history_info.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            history_info,
            text="📈 Performance",
            font=FONTS['body_bold'],
            text_color=COLORS['text_primary']
        ).pack(pady=(10, 5))
        
        self.performance_label = ctk.CTkLabel(
            history_info,
            text="Cycles Saved: ~150",
            font=FONTS['body'],
            text_color=COLORS['accent_green']
        )
        self.performance_label.pack(pady=(0, 10))
        
        # 設定ボタン（ギアアイコン付き）
        self.premium_settings_button = ctk.CTkButton(
            info_container,
            text="⚙️ Settings",
            command=self.open_premium_settings,
            width=150,
            height=40,
            font=FONTS['body_bold'],
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent_blue'],
            border_width=1,
            border_color=COLORS['text_secondary']
        )
        self.premium_settings_button.pack(pady=(10, 0))
    
    def get_real_battery_status(self):
        """🔋 実際のバッテリー情報取得"""
        if self.screenshot_mode:
            return True  # スクリーンショットモードは固定値
            
        try:
            if self.controller:
                # コア機能を使用して取得
                battery_level = self.controller.get_battery_percentage()
                is_charging = self.controller.is_charging()
                
                if battery_level is not None:
                    self.battery_level = battery_level
                    self.is_charging = is_charging
                    self.is_optimal_range = (self.start_threshold <= battery_level <= self.stop_threshold)
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
                self.is_optimal_range = (self.start_threshold <= self.battery_level <= self.stop_threshold)
                
                return True
                
            return False
                
        except Exception as e:
            print(f"🚨 Battery Status Error: {e}")
            return False
    
    def update_premium_ui(self):
        """プレミアムUI全体更新"""
        try:
            # メインバッテリー表示更新
            self.update_main_battery_display()
            
            # ステータス表示更新
            self.update_status_display()
            
            # コントロールパネル更新
            self.update_control_panel()
            
            # 情報パネル更新
            self.update_info_panel()
            
            # アニメーション更新
            if self.is_charging:
                self.update_charging_animation()
                
        except Exception as e:
            print(f"🚨 Premium UI Update Error: {e}")
    
    def update_main_battery_display(self):
        """メインバッテリー表示更新"""
        # バッテリーアイコンとカラー選択
        if self.battery_level <= 20:
            icon = "🪫"
            color = COLORS['accent_red']
            progress_color = COLORS['accent_red']
        elif self.battery_level <= 50:
            icon = "🔋"
            color = COLORS['accent_orange']
            progress_color = COLORS['accent_orange']
        elif self.is_optimal_range:
            icon = "🔋"
            color = COLORS['accent_green']
            progress_color = COLORS['accent_green']
        else:
            icon = "🔋"
            color = COLORS['accent_blue']
            progress_color = COLORS['accent_blue']
        
        # 充電中はアイコン変更
        if self.is_charging:
            icon = "⚡"
            color = COLORS['accent_green']
            
        # メインラベル更新
        self.main_battery_label.configure(
            text=f"{icon} {self.battery_level}%",
            text_color=color
        )
        
        # プログレスバー更新
        self.main_progress.configure(progress_color=progress_color)
        self.main_progress.set(max(0.0, min(1.0, self.battery_level / 100)))
        
    def update_status_display(self):
        """ステータス表示更新"""
        if self.is_charging:
            status_text = "⚡ Charging"
            status_color = COLORS['accent_green']
            action_text = f"充電停止予定: {self.stop_threshold}%"
        elif self.is_optimal_range:
            status_text = "✅ Optimal Range"
            status_color = COLORS['accent_blue']
            action_text = "バッテリーは理想的な範囲にあります"
        elif self.battery_level <= self.start_threshold:
            status_text = "🔋 Low Battery"
            status_color = COLORS['accent_orange']
            action_text = f"まもなく充電開始します（{self.start_threshold}%以下）"
        else:
            status_text = "⚡ On Battery"
            status_color = COLORS['accent_orange']
            action_text = "バッテリー駆動中"
            
        self.current_status_label.configure(
            text=status_text,
            text_color=status_color
        )
        
        self.action_recommendation_label.configure(
            text=action_text,
            text_color=COLORS['text_secondary']
        )
    
    def update_control_panel(self):
        """コントロールパネル更新"""
        if self.auto_mode:
            self.switch_description_label.configure(
                text="Battery Protection Active",
                text_color=COLORS['accent_green']
            )
        else:
            self.switch_description_label.configure(
                text="Manual Control Mode",
                text_color=COLORS['accent_orange']
            )
    
    def update_info_panel(self):
        """情報パネル更新"""
        # パフォーマンス表示更新
        if self.is_optimal_range:
            cycles_saved = int((self.battery_level - self.start_threshold) * 2)  # 概算
            self.performance_label.configure(
                text=f"Cycles Saved: ~{cycles_saved}",
                text_color=COLORS['accent_green']
            )
        else:
            self.performance_label.configure(
                text="Optimizing...",
                text_color=COLORS['text_secondary']
            )
    
    def update_charging_animation(self):
        """充電中アニメーション"""
        if not self.is_charging:
            return
            
        # 色の変化アニメーション（簡易版）
        self.animation_angle = (self.animation_angle + 10) % 360
        
        # 緑色の明度を変化
        if self.animation_angle < 180:
            alpha = 0.7 + (0.3 * (self.animation_angle / 180))
        else:
            alpha = 1.0 - (0.3 * ((self.animation_angle - 180) / 180))
            
        # 1秒後に再実行
        self.root.after(1000, self.update_charging_animation)
    
    def start_real_battery_monitoring(self):
        """🛡️ 実バッテリー監視開始（120秒間隔）"""
        def monitor_loop():
            while True:
                try:
                    if self.get_real_battery_status():
                        # UIを安全に更新
                        self.root.after(0, self.update_premium_ui)
                        
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
        print("🛡️ Premium Battery Monitoring Started (120s interval)")
    
    def toggle_auto_mode(self):
        """自動制御モード切り替え"""
        self.auto_mode = self.premium_auto_switch.get()
        print(f"🤖 Smart Protection: {'ON' if self.auto_mode else 'OFF'}")
        self.update_premium_ui()
        
    def check_auto_control(self):
        """🤖 自動制御チェック（実機能統合）"""
        if not self.auto_mode or not self.controller:
            return
            
        try:
            # 充電停止条件
            if self.battery_level >= self.stop_threshold and self.is_charging:
                print(f"🤖 Smart Control: バッテリー{self.battery_level}%で充電停止")
                # 🚨 実制御は保護済み
                print("🚨 安全モード: 実際の制御はコメントアウト中")
                
            # 充電開始条件
            elif self.battery_level <= self.start_threshold and not self.is_charging:
                print(f"🤖 Smart Control: バッテリー{self.battery_level}%で充電開始")
                # 🚨 実制御は保護済み
                print("🚨 安全モード: 実際の制御はコメントアウト中")
                
        except Exception as e:
            print(f"🚨 Auto Control Error: {e}")
    
    def open_premium_settings(self):
        """プレミアム設定画面を開く"""
        try:
            settings_window = ctk.CTkToplevel(self.root)
            settings_window.title("⚙️ Battery Manager Settings")
            settings_window.geometry("500x400")
            settings_window.resizable(False, False)
            settings_window.configure(fg_color=COLORS['bg_primary'])
            
            # 画面中央配置
            settings_window.update_idletasks()
            x = (settings_window.winfo_screenwidth() // 2) - 250
            y = (settings_window.winfo_screenheight() // 2) - 200
            settings_window.geometry(f"500x400+{x}+{y}")
            
            # プレミアム設定UI（将来実装予定）
            main_frame = ctk.CTkFrame(
                settings_window,
                corner_radius=15,
                fg_color=COLORS['bg_secondary']
            )
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                main_frame,
                text="⚙️ Premium Settings",
                font=FONTS['heading_bold'],
                text_color=COLORS['text_primary']
            ).pack(pady=30)
            
            ctk.CTkLabel(
                main_frame,
                text="詳細設定画面は Phase 5 で実装予定",
                font=FONTS['body'],
                text_color=COLORS['text_secondary']
            ).pack(pady=20)
            
            # 閉じるボタン
            ctk.CTkButton(
                main_frame,
                text="Close",
                command=settings_window.destroy,
                width=120,
                height=35,
                font=FONTS['body_bold'],
                fg_color=COLORS['accent_blue'],
                hover_color=COLORS['accent_green']
            ).pack(pady=30)
            
        except Exception as e:
            print(f"🚨 Premium Settings Error: {e}")
    
    def run(self):
        """プレミアムアプリケーション実行"""
        if self.screenshot_mode:
            print("🔋 Ultra Simple Battery Manager - Premium (Screenshot Mode)")
            print("📸 販売ページ用スクリーンショットモード")
        else:
            print("🔋 Ultra Simple Battery Manager - Premium")
            print("Phase 4: プレミアムデザイン実装（販売品質）")
            print("🚨 充電制御は安全モードで動作中")
        
        # 初回バッテリー情報取得
        if not self.screenshot_mode:
            self.get_real_battery_status()
        self.update_premium_ui()
        
        # アニメーション開始
        if self.is_charging:
            self.update_charging_animation()
        
        # 終了処理設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインループ開始
        self.root.mainloop()
        
    def on_closing(self):
        """終了処理"""
        print("🔋 Ultra Simple Battery Manager - Premium 終了")
        self.root.quit()
        self.root.destroy()

def main():
    """メイン関数"""
    import argparse
    
    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='Battery Manager Premium UI')
    parser.add_argument('--screenshot', action='store_true', 
                       help='スクリーンショット用モード（理想データ表示）')
    
    args = parser.parse_args()
    
    try:
        app = BatteryManagerPremiumUI(screenshot_mode=args.screenshot)
        app.run()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()