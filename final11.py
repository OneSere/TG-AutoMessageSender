# 🚀 TG AutoMessageSender - Gradient UI & Enhanced Section Layout
# Developed by Abhishek Choudhary aka @curiosityandyou

import os
import re
import json
import asyncio
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from datetime import datetime

API_ID = 25843334
API_HASH = 'e752bb9ebc151b7e36741d7ead8e4fd0'

class TelegramAutoMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("TG AutoMessageSender")
        self.root.geometry("900x780")
        self.loop = asyncio.get_event_loop()
        self.client = None
        self.messages = []
        self.entities = []

        self.phone = tk.StringVar()
        self.otp = tk.StringVar()
        self.group_input = tk.StringVar()
        self.interval_value = tk.StringVar(value="10")
        self.interval_unit = tk.StringVar(value="Seconds")
        self.repeat_count = tk.StringVar(value="1")
        self.status_text = tk.StringVar(value="Welcome! Please login to begin.")

        self.setup_styles()
        self.build_ui()
        self.poll_asyncio()

    def setup_styles(self):
        self.root.configure(bg="#e6f0ff")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f4faff")
        style.configure("TLabel", background="#f4faff", foreground="#00264d", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("TLabelframe", background="#f4faff", foreground="#003366", font=("Segoe UI", 10, "bold"))

    def build_ui(self):
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="TG AutoMessageSender", font=("Segoe UI", 18, "bold"), foreground="#004080").grid(row=0, column=0, columnspan=3, sticky="w")
        link = tk.Label(main, text="Built by @curiosityandyou", font=("Segoe UI", 9, "underline"), foreground="blue", cursor="hand2", bg="#f4faff")
        link.grid(row=1, column=0, sticky="w")
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://t.me/curiosityandyou"))

        # Login Section
        login = ttk.Labelframe(main, text="🔐 Login Section")
        login.grid(row=2, column=0, columnspan=3, sticky="we", pady=10)
        ttk.Label(login, text="Phone:").grid(row=0, column=0)
        phone_entry = ttk.Entry(login, textvariable=self.phone, width=25)
        phone_entry.insert(0, "+91xxxxxxxxxx")
        phone_entry.bind("<FocusIn>", lambda e: phone_entry.delete(0, tk.END))
        phone_entry.grid(row=0, column=1)
        ttk.Label(login, text="OTP:").grid(row=1, column=0)
        otp_entry = ttk.Entry(login, textvariable=self.otp, width=15)
        otp_entry.insert(0, "12345")
        otp_entry.bind("<FocusIn>", lambda e: otp_entry.delete(0, tk.END))
        otp_entry.grid(row=1, column=1)
        ttk.Button(login, text="Login", command=self.login).grid(row=0, column=2, padx=5)
        ttk.Button(login, text="Submit OTP", command=self.submit_otp).grid(row=1, column=2, padx=5)
        ttk.Button(login, text="🚀 Start Messaging", command=self.start_messaging).grid(row=2, column=0, columnspan=3, pady=5)
        ttk.Label(login, textvariable=self.status_text, foreground="#009933").grid(row=3, column=0, columnspan=3, sticky="w", pady=3)

        # Group Section
        group = ttk.Labelframe(main, text="📤 Group Configuration")
        group.grid(row=3, column=0, columnspan=3, sticky="we")
        ttk.Label(group, text="Groups (comma separated):").grid(row=0, column=0)
        group_entry = ttk.Entry(group, textvariable=self.group_input, width=60)
        group_entry.insert(0, "@examplegroup")
        group_entry.bind("<FocusIn>", lambda e: group_entry.delete(0, tk.END))
        group_entry.grid(row=0, column=1)
        ttk.Button(group, text="💾 Save", command=self.save_settings).grid(row=0, column=2)

        # Messages Section
        msg_frame = ttk.Labelframe(main, text="✍️ Compose Messages")
        msg_frame.grid(row=4, column=0, columnspan=3, sticky="we")
        self.msg_entry = ttk.Entry(msg_frame, width=50)
        self.msg_entry.pack(side="left", padx=(5, 0), pady=5)
        ttk.Button(msg_frame, text="Add Message", command=self.add_message).pack(side="left", padx=5)
        self.msg_listbox = tk.Listbox(msg_frame, height=3, bg="#ffffff", fg="black", font=("Segoe UI", 10))
        self.msg_listbox.pack(fill="x", padx=5, pady=(3, 5))

        # Timing Section
        timing = ttk.Labelframe(main, text="⏱️ Timing & Repeats")
        timing.grid(row=5, column=0, columnspan=3, sticky="we")
        ttk.Label(timing, text="Gap Between Messages:").grid(row=0, column=0)
        ttk.Entry(timing, textvariable=self.interval_value, width=6).grid(row=0, column=1)
        ttk.Combobox(timing, textvariable=self.interval_unit, values=["Seconds", "Minutes", "Hours"], width=10).grid(row=0, column=2)
        ttk.Label(timing, text="Repeat Messages:").grid(row=0, column=3)
        ttk.Entry(timing, textvariable=self.repeat_count, width=6).grid(row=0, column=4)

        # Save / Load Section
        layout = ttk.Labelframe(main, text="💼 Save / Load Layouts")
        layout.grid(row=6, column=0, columnspan=3, sticky="we")
        ttk.Label(layout, text="💡 Save your layout to reload settings instantly later.").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Button(layout, text="Save Settings", command=self.save_settings).grid(row=1, column=0, pady=5, padx=5)
        ttk.Button(layout, text="Load Settings", command=self.load_settings).grid(row=1, column=1, pady=5, padx=5)

        # Log Section
        log_frame = ttk.Labelframe(main, text="📜 Live Status Updates")
        log_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=5)
        self.log = tk.Text(log_frame, height=10, bg="#ffffff", fg="#003300", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True, padx=5, pady=5)

        # Support Note
        note = tk.Label(main, text="❓ Facing issues? Contact admin @curiosityandyou", fg="blue", cursor="hand2", font=("Segoe UI", 9), bg="#f4faff")
        note.grid(row=8, column=0, columnspan=3, sticky="w", padx=10, pady=8)
        note.bind("<Button-1>", lambda e: webbrowser.open_new("https://t.me/curiosityandyou"))

    def poll_asyncio(self):
        try:
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()
        finally:
            self.root.after(100, self.poll_asyncio)

    def log_write(self, text):
        now = datetime.now().strftime("[%H:%M:%S]")
        self.log.insert("end", f"{now} {text}\n")
        self.log.see("end")
        self.status_text.set(text)

    def add_message(self):
        msg = self.msg_entry.get().strip()
        if msg:
            self.messages.append(msg)
            self.msg_listbox.insert("end", msg)
            self.msg_entry.delete(0, "end")
            self.log_write("📨 Message added")

    def login(self):
        self.log_write("🔐 Logging in...")
        self.loop.create_task(self.async_login())

    async def async_login(self):
        try:
            phone = self.phone.get().strip()
            session = f"session_{phone.replace('+', '')}"
            self.client = TelegramClient(session, API_ID, API_HASH)
            await self.client.connect()
            if await self.client.is_user_authorized():
                self.log_write("✅ Logged in with saved session.")
            else:
                await self.client.send_code_request(phone)
                self.log_write("📩 OTP sent.")
        except Exception as e:
            self.log_write(f"❌ Login failed: {e}")

    def submit_otp(self):
        self.log_write("🔐 Submitting OTP...")
        self.loop.create_task(self.async_submit_otp())

    async def async_submit_otp(self):
        try:
            await self.client.sign_in(self.phone.get().strip(), self.otp.get().strip())
            self.log_write("✅ Logged in.")
        except Exception as e:
            self.log_write(f"❌ OTP error: {e}")

    def save_settings(self):
        data = {
            "phone": self.phone.get(),
            "group_input": self.group_input.get(),
            "interval_value": self.interval_value.get(),
            "interval_unit": self.interval_unit.get(),
            "repeat_count": self.repeat_count.get(),
            "messages": self.messages
        }
        with open("settings.json", "w") as f:
            json.dump(data, f)
        self.log_write("💾 Settings saved.")

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                self.phone.set(data.get("phone", ""))
                self.group_input.set(data.get("group_input", ""))
                self.interval_value.set(data.get("interval_value", "10"))
                self.interval_unit.set(data.get("interval_unit", "Seconds"))
                self.repeat_count.set(data.get("repeat_count", "1"))
                self.messages = data.get("messages", [])
                self.msg_listbox.delete(0, "end")
                for msg in self.messages:
                    self.msg_listbox.insert("end", msg)
            self.log_write("📂 Settings loaded.")
        except Exception as e:
            self.log_write(f"❌ Load error: {e}")

    def start_messaging(self):
        self.log_write("🚀 Starting messaging round...")
        self.loop.create_task(self.async_start_messaging())

    async def async_start_messaging(self):
        try:
            groups = [g.strip() for g in self.group_input.get().split(',') if g.strip()]
            repeat = int(self.repeat_count.get())
            interval = int(self.interval_value.get())
            unit = self.interval_unit.get().lower()
            seconds = interval * {"seconds": 1, "minutes": 60, "hours": 3600}[unit]

            self.entities = []
            for group in groups:
                try:
                    entity = await self.client.get_entity(group)
                    self.entities.append(entity)
                except Exception as e:
                    self.log_write(f"⚠️ Could not join: {group} ({e})")

            for r in range(repeat):
                self.log_write(f"🔁 Round {r+1}/{repeat}")
                for i, msg in enumerate(self.messages):
                    for entity in self.entities:
                        try:
                            result = await self.client.send_message(entity, msg)
                            if result.id:
                                self.log_write(f"✅ Sent '{msg}' to {entity.title or entity.username}")
                            await asyncio.sleep(seconds)
                        except Exception as e:
                            self.log_write(f"❌ Error sending to {entity.title}: {e}")
            self.log_write("✅ All messages are sent successfully!")
        except Exception as e:
            self.log_write(f"❌ Messaging failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramAutoMessenger(root)
    root.mainloop()
