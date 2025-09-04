#!/usr/bin/env python3
"""
Battery Manager Demo - Simple Screenshot Version
確実に表示される簡易版
"""

import customtkinter as ctk

# 設定
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# メインウィンドウ
root = ctk.CTk()
root.title("🔋 Ultra Simple Battery Manager")
root.geometry("450x600")
root.resizable(False, False)

# 画面中央配置
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - 225
y = (root.winfo_screenheight() // 2) - 300
root.geometry(f"450x600+{x}+{y}")

# === ヘッダー ===
header_frame = ctk.CTkFrame(root, height=50)
header_frame.pack(fill='x', padx=15, pady=(15, 5))
header_frame.pack_propagate(False)

ctk.CTkLabel(
    header_frame,
    text="Ultra Simple Battery Manager",
    font=ctk.CTkFont(size=16, weight="bold")
).pack(expand=True)

# === バッテリー表示 ===
battery_frame = ctk.CTkFrame(root, height=180)
battery_frame.pack(fill='x', padx=15, pady=5)
battery_frame.pack_propagate(False)

ctk.CTkLabel(
    battery_frame,
    text="🔋 65%",
    font=ctk.CTkFont(size=48, weight="bold"),
    text_color="#34c759"
).pack(expand=True, pady=(20, 10))

ctk.CTkLabel(
    battery_frame,
    text="最適範囲",
    font=ctk.CTkFont(size=14),
    text_color="#8e8e93"
).pack(pady=(0, 10))

# プログレスバー
progress = ctk.CTkProgressBar(battery_frame, width=350, height=12)
progress.pack(pady=(0, 20))
progress.set(0.65)

# === ステータス ===
status_frame = ctk.CTkFrame(root, height=80)
status_frame.pack(fill='x', padx=15, pady=5)
status_frame.pack_propagate(False)

ctk.CTkLabel(
    status_frame,
    text="状態: 最適範囲",
    font=ctk.CTkFont(size=14, weight="bold"),
    text_color="#007aff"
).pack(pady=(15, 5))

ctk.CTkLabel(
    status_frame,
    text="バッテリー保護が有効です",
    font=ctk.CTkFont(size=12),
    text_color="#8e8e93"
).pack(pady=(0, 15))

# === コントロール ===
control_frame = ctk.CTkFrame(root, height=100)
control_frame.pack(fill='x', padx=15, pady=5)
control_frame.pack_propagate(False)

control_inner = ctk.CTkFrame(control_frame, fg_color="transparent")
control_inner.pack(expand=True, fill='both', padx=20, pady=20)

ctk.CTkLabel(
    control_inner,
    text="🤖 Smart Battery Protection",
    font=ctk.CTkFont(size=14, weight="bold")
).pack(pady=(10, 10))

switch = ctk.CTkSwitch(control_inner, text="", width=60, height=30)
switch.pack(pady=(0, 10))
switch.select()

# === ボタン ===
button_frame = ctk.CTkFrame(root, height=80)
button_frame.pack(fill='x', padx=15, pady=5)
button_frame.pack_propagate(False)

button_inner = ctk.CTkFrame(button_frame, fg_color="transparent")
button_inner.pack(expand=True, fill='both', padx=20, pady=15)

# 2x2ボタングリッド
buttons = [
    ("⚙️ 設定", "#007aff"),
    ("📊 統計", "#007aff"), 
    ("📝 ログ", "#007aff"),
    ("ℹ️ About", "#007aff")
]

for i, (text, color) in enumerate(buttons):
    btn = ctk.CTkButton(
        button_inner,
        text=text,
        width=80,
        height=25,
        font=ctk.CTkFont(size=11),
        fg_color=color
    )
    row = i // 2
    col = i % 2
    btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

button_inner.grid_columnconfigure(0, weight=1)
button_inner.grid_columnconfigure(1, weight=1)

# === フッター ===
footer_frame = ctk.CTkFrame(root, height=40)
footer_frame.pack(fill='x', padx=15, pady=(5, 15))
footer_frame.pack_propagate(False)

ctk.CTkLabel(
    footer_frame,
    text="v2.0 Final | 最終更新: 14:27",
    font=ctk.CTkFont(size=10),
    text_color="#8e8e93"
).pack(expand=True)

print("🔋 Battery Manager Demo 起動")
print("📸 スクリーンショット用デモ版（65%, 最適範囲）")

# ウィンドウを前面に
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False))

# メインループ
root.mainloop()