# -*- coding: utf-8 -*-
"""Event-Test: Tkinter/CTk-Events unter Python 3.14 + Tk 9.0."""
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import tkinter as tk

root = tk.Tk()
print("TkVersion:", tk.TkVersion, "TclVersion:", tk.TclVersion)
print("Tk pkg:", root.tk.call("package", "present", "Tk"))
print("tcl patchlevel:", root.tk.call("info", "patchlevel"))

hits = {"btn_cmd": 0, "enter": 0, "leave": 0, "unmap": 0, "key": 0, "ctk_btn": 0}

root.withdraw()

def on_btn():
    hits["btn_cmd"] += 1
b = tk.Button(root, text="T", command=on_btn)
b.pack()
b.update_idletasks()
b.event_generate("<Button-1>")
b.event_generate("<ButtonRelease-1>")
root.update()

lbl = tk.Label(root, text="L")
lbl.pack()
lbl.bind("<Enter>", lambda e: hits.__setitem__("enter", hits["enter"] + 1))
lbl.bind("<Leave>", lambda e: hits.__setitem__("leave", hits["leave"] + 1))
lbl.update_idletasks()
lbl.event_generate("<Enter>")
lbl.event_generate("<Leave>")
root.update()

root.bind("<Key>", lambda e: hits.__setitem__("key", hits["key"] + 1))
root.event_generate("<Key-A>")
root.update()

import customtkinter as ctk
ctk.set_appearance_mode("Light")
croot = ctk.CTk()
croot.withdraw()
def on_ctk():
    hits["ctk_btn"] += 1
cb = ctk.CTkButton(croot, text="C", command=on_ctk)
cb.pack()
croot.update_idletasks()
cb.event_generate("<Button-1>")
cb.event_generate("<ButtonRelease-1>")
croot.update()

w = tk.Toplevel(root)
w.geometry("300x200+0+0")
def on_unmap(e):
    hits["unmap"] += 1
w.bind("<Unmap>", on_unmap)
def minimize_check():
    for _ in range(40):
        w.update()
        time.sleep(0.05)
    print("state nach iconify:", w.state())
    w.destroy()
w.after(300, minimize_check)
w.after(100, w.iconify)

def finish():
    print("HITS:", hits)
    root.destroy()
    croot.destroy()
root.after(3500, finish)
root.mainloop()
print("DONE")
