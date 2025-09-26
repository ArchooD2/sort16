import tkinter as tk
import time
import random
import math
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
records_file = os.path.join(script_dir, "records.json")
# --- Setup ---
root = tk.Tk()
root.title("Sort16")
root.geometry("1920x1080")
root.configure(bg="lightblue")  # can also use hex codes like "#ffcccc"

number_var = tk.IntVar(value=8)
template = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
main_string = ""
bracket_length = 0
bracket_pos = 0
chosen_number = None
button_pressed = False
game_won = False
records = [None] * 29  # lengths 8..36

try:
    with open(records_file, "r") as f:
        data = json.load(f)
        for key, value in data.items():
            idx = int(key) - 8
            if 0 <= idx < len(records):
                records[idx] = value
except FileNotFoundError:
    pass
except json.JSONDecodeError:
    print("Warning: JSON file is invalid. Starting with empty records.")


# --- Labels ---
label1 = tk.Label(root, text='Select character number (8-36): ', bg="lightblue", font=('calibre', 10, 'bold'))
label1.pack()

label2 = tk.Entry(root, textvariable=number_var,font=('calibre', 10, 'normal'))
label2.pack()

label3 = tk.Label(root, text="", font=('calibre', 36, 'bold'))
label3.pack_forget()

start_time = None

def update_records_display():
    for i, lbl in enumerate(record_labels):
        if records[i] is not None:
            lbl.config(text=f"{i+8}: {records[i]:.3f}s")
        else:
            lbl.config(text=f"{i+8}: -")

def bracket_first_x(text, start, x):
    chars = list(text)
    spaced_chars = "  ".join(chars)
    spaced_list = spaced_chars.split("  ")

    first_part = "  ".join(spaced_list[:start]) + " [ " + "  ".join(spaced_list[start:x]) + " ]"
    second_part = "  ".join(spaced_list[x:])

    return first_part + ("  " + second_part if second_part else "")


def shuffle_string(s):
    char_list = list(s)
    random.shuffle(char_list)
    return ''.join(char_list)


def update_timer():
    if game_won or not button_pressed:
        return
    now = time.time()
    elapsed = now - start_time
    label1.config(text=f"Time: {elapsed:.3f}", font=('calibre', 20, 'bold'))
    root.after(10, update_timer)

def generate_string(chosen_number):
    while True:
        a = shuffle_string(template[:chosen_number])
        if a != template[:chosen_number]:
            return a

def start_game():
    global main_string, bracket_length, bracket_pos, start_time, chosen_number, button_pressed, game_won
    chosen_number = number_var.get()
    if chosen_number < 8 or chosen_number > 36:
        label1.config(text="Select number from 8 to 36!", font=('calibre', 20, 'bold'))
        return

    button_pressed = True
    game_won = False
    start_time = time.time()
    update_timer()

    main_string = generate_string(chosen_number)
    bracket_length = math.ceil(chosen_number / 2)
    bracket_pos = 0

    label2.pack_forget()
    button.pack_forget()
    if chosen_number >= 33:
        label3.config(text=bracket_first_x(main_string, 0, bracket_length),font=('calibre', 24, 'bold'))
    else:
        label3.config(text=bracket_first_x(main_string, 0, bracket_length),font=('calibre', 36, 'bold'))
    label3.pack(pady=100)
    button1.pack()
    button2.pack()
    records_frame.pack_forget()
    button1.config(text="Reset", command=reset_game)

    root.bind("<Key>", key_pressed)


def reset_game():
    global button_pressed, game_won
    button_pressed = False
    game_won = False
    restart_same_number()


def restart_same_number():
    global main_string, bracket_length, bracket_pos, start_time, button_pressed, game_won
    button_pressed = True
    game_won = False
    start_time = time.time()
    update_timer()

    main_string = shuffle_string(template[:chosen_number])
    bracket_length = math.ceil(chosen_number / 2)
    bracket_pos = 0
    label3.config(text=bracket_first_x(main_string, 0, bracket_length))

    root.bind("<Key>", key_pressed)



def go_to_menu():
    global button_pressed, game_won, chosen_number
    button_pressed = False
    game_won = False
    label2.delete(0, tk.END)
    label2.insert(0, str(chosen_number)) 
    chosen_number = None
    label1.config(text='Select character number: ', font=('calibre', 10, 'bold'))
    label2.pack()
    button.pack(pady=5)
    label3.pack_forget()
    button1.pack_forget()
    button2.pack_forget()
    records_frame.pack(side="left")
    root.unbind("<Key>")
    update_records_display()

def key_pressed(event):
    global bracket_pos, bracket_length, main_string, chosen_number, game_won

    shifting = main_string[bracket_pos:bracket_pos + bracket_length]

    if event.keysym.upper() == "A" and bracket_pos > 0:
        bracket_pos -= 1
    elif event.keysym.upper() == "D" and bracket_pos + bracket_length < len(main_string):
        bracket_pos += 1

    elif event.keysym == "Left" and shifting:
        main_string = (
            main_string[:bracket_pos]
            + shiftByOne(shifting, "left")
            + main_string[bracket_pos + bracket_length:]
        )
    elif event.keysym == "Right" and shifting:
        main_string = (
            main_string[:bracket_pos]
            + shiftByOne(shifting, "right")
            + main_string[bracket_pos + bracket_length:]
        )

    label3.config(text=bracket_first_x(main_string, bracket_pos, bracket_pos + bracket_length))

    if win(main_string, chosen_number):
        game_won = True
        czas = round(time.time() - start_time, 3)

        idx = chosen_number - 8
        if records[idx] is None or czas < records[idx]:
            records[idx] = czas
        records_dict = {str(i + 8): records[i] for i in range(len(records)) if records[i] is not None}
        with open(records_file, "w") as f:
            json.dump(records_dict, f, indent=4)
        record_labels[idx+1].config(text=f"{chosen_number}: {records[idx]}s")
        label1.config(
            text=f"You win!\nTime: {czas}s\nCurrent best: {records[idx]}s",
            font=('calibre', 20, 'bold')
        )
        root.unbind("<Key>")
        button2.pack()
        button1.config(text="Play again", command=restart_same_number)

button = tk.Button(root, text="Play!", command=start_game)
button.pack(pady=5)

button1 = tk.Button(root, text="Reset", command=reset_game)
button1.pack(padx=100)
button1.pack_forget()

button2 = tk.Button(root, text="Go to main menu", command=go_to_menu)
button2.pack_forget()

record_labels = []
records_frame = tk.Frame(root, bg="lightblue")
records_frame.pack(side="left")
bests = tk.Label(records_frame, text="Best times (s):", bg="lightblue", font=('calibre', 14, 'bold'))
bests.pack()
for i in range(8, 37):
    lbl = tk.Label(records_frame, text=f"{i}: -", font=('calibre', 12), bg="lightblue", anchor="w", width=14)
    lbl.pack()
    record_labels.append(lbl)

update_records_display()

def shiftByOne(text, direction):
    if not text:
        return text
    if direction == "left":
        return text[1:] + text[0]
    elif direction == "right":
        return text[-1] + text[:-1]
    return text

def win(string, num):
    return string == template[:num]

root.mainloop()
