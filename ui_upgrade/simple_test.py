#!/usr/bin/env python3
import customtkinter as ctk

# 基本設定
ctk.set_appearance_mode("dark")

# ウィンドウ作成
root = ctk.CTk()
root.title("🔋 Battery Manager Test")
root.geometry("400x300")
root.resizable(False, False)

# 中央配置
x = (root.winfo_screenwidth() // 2) - 200
y = (root.winfo_screenheight() // 2) - 150
root.geometry(f"400x300+{x}+{y}")

# シンプルなコンテンツ
ctk.CTkLabel(
    root,
    text="🔋 Ultra Simple\nBattery Manager",
    font=ctk.CTkFont(size=24, weight="bold"),
    justify="center"
).pack(expand=True, pady=50)

ctk.CTkLabel(
    root,
    text="65% - Optimal Range",
    font=ctk.CTkFont(size=18),
    text_color="#34c759"
).pack(pady=10)

ctk.CTkButton(
    root,
    text="⚙️ Settings",
    width=120,
    height=40
).pack(pady=20)

print("🔋 Test UI Started")
print("ウィンドウが表示されているはずです")

# 前面表示
root.lift()
root.attributes('-topmost', True)
root.after(1000, lambda: root.attributes('-topmost', False))

# 自動終了（10秒後）
root.after(10000, lambda: root.quit())

root.mainloop()
print("Test Complete")