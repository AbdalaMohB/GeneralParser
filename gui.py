import tkinter as tk
from tkinter import filedialog
import parse
import lex
def parseTxt(txt):
    tokenizer=lex.Tokenizer(txt)
    parser=parse.Parser(tokenizer.tokenize())
    parser.parse()
    return parser.errors

def on_text_edited(event=None):
    if text_area.edit_modified():
        content = text_area.get("1.0", tk.END)
        parse_result=parseTxt(content.strip())
        parse_result.reverse()
        output_box.delete("1.0", tk.END)
        for err in parse_result:
            output_box.insert("1.0", err+"\n") 
        
        text_area.edit_modified(False)
# Setup main window
root = tk.Tk()
root.title("Split Text Editor")
root.geometry("800x500")

# 1. Create a PanedWindow (the divider)
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
paned_window.pack(fill=tk.BOTH, expand=True)

# 2. Left side: The Text Editor
text_area = tk.Text(paned_window, undo=True, wrap="word", font=("Consolas", 11), padx=10, pady=10)
paned_window.add(text_area)

# 3. Right side: An empty Display/Output box
output_box = tk.Text(paned_window, bg="#f0f0f0", font=("Consolas", 11))
paned_window.add(output_box)

# 4. Bind the edit function
# We use <<Modified>> which is a virtual event built into the Text widget
text_area.bind("<<Modified>>", on_text_edited)

root.mainloop()
