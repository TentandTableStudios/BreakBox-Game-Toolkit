import xml.etree.ElementTree as ET
import tkinter.messagebox as mb
import os

def import_cheat_table():
    from tkinter import filedialog
    path = filedialog.askopenfilename(filetypes=[("Cheat Table", "*.ct")])
    if path:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            entries = root.find("CheatEntries")
            if entries is None:
                mb.showwarning("Warning", "No cheat entries found in table.")
                return

            cheats = []
            for ce in entries.findall("CheatEntry"):
                desc = ce.findtext("Description", "").strip('"')
                addr = ce.findtext("Address", "")
                vartype = ce.findtext("VariableType", "")
                val = ce.findtext("Value", "")

                cheats.append({
                    "description": desc,
                    "address": addr,
                    "type": vartype,
                    "value": val
                })

            mb.showinfo("Import Successful", f"Imported {len(cheats)} entries.")
            return cheats

        except Exception as e:
            mb.showerror("Import Error", f"Failed to parse CT file:\n{str(e)}")

def load_cheat_table(path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    root = tree.getroot()
    cheats = []

    for cheat in root.findall(".//CheatEntry"):
        description = cheat.findtext("Description", default="No description").strip('"')
        address = cheat.findtext("Address")
        value = cheat.findtext("Value")
        vartype = cheat.findtext("VariableType")

        if address and value:
            cheats.append({
                "description": description,
                "address": address,
                "value": value,
                "type": vartype
            })
    return cheats

def save_cheat_table(path, cheats):
    import xml.etree.ElementTree as ET

    root = ET.Element("CheatTable")
    cheat_entries = ET.SubElement(root, "CheatEntries")

    for c in cheats:
        entry = ET.SubElement(cheat_entries, "CheatEntry")
        ET.SubElement(entry, "Description").text = f'"{c.get("description","")}"'
        ET.SubElement(entry, "Address").text = c.get("address", "")
        ET.SubElement(entry, "VariableType").text = c.get("type", "")
        ET.SubElement(entry, "Value").text = c.get("value", "")

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


