import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import random
from PIL import ImageTk, Image

# Assume 'us_map.png' exists in the current directory. Convert to GIF if no Pillow.
# Assume 'decks.xlsx' exists with sheets for each deck (e.g., 'Starter', 'Northeast Reward', 'Boss', 'Event')

#map board size
canvas_width = 1000
canvas_height = 800

# Main window
root = tk.Tk()
root.title("Board Game Prototype")

# Exit handler to free resources
def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# ---------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)
#pack frames from right to left
hand_frame_p2 = tk.Frame(root)
hand_frame_p2.pack(side=tk.RIGHT, padx=10, pady=10)
hand_frame_p1 = tk.Frame(root)
hand_frame_p1.pack(side=tk.RIGHT, padx=10, pady=10)
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)



# ---------------------------------------------------------------------
# Left Frame: Checkboxes and Map
# ---------------------------------------------------------------------

# Modes (use Radiobutton for mutual exclusivity)
mode_var = tk.StringVar(value="add minion")
modes = ["add minion", "add soldier", "move player 1", "move player 2", "add number", "del marker"]

radioFrame = ttk.Frame(left_frame)
radioFrame.pack(fill=tk.X, padx=5, pady=2)

for mode in modes:
    tk.Radiobutton(radioFrame, text=mode, variable=mode_var, value=mode).pack(anchor=tk.W, side=tk.LEFT)

# Map Canvas



canvas = tk.Canvas(left_frame, width=canvas_width, height=canvas_height)  # Adjust size based on image
canvas.pack()

# Load and scale image
try:
    img = Image.open("map.png")
    # Get canvas dimensions

    # Get original image dimensions
    img_width, img_height = img.size
    # Calculate scaling factor to fit canvas while preserving aspect ratio
    scale = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    # Resize image
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    map_ref = canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo, tags='map')
    canvas.image = photo  # Keep reference to prevent garbage collection
except FileNotFoundError:
    messagebox.showerror("Error", "us_map.png not found.")
    root.quit()

number_token_counter = 0

# Click event on map
def map_click(event):
    global number_token_counter
    mode = mode_var.get()
    x, y = event.x, event.y
    if mode == "add minion":
        canvas.create_rectangle(x-5, y-5, x+5, y+5, fill='red', tags='minion')
    elif mode == "add soldier":
        canvas.create_rectangle(x-5, y-5, x+5, y+5, fill='green', tags='soldier')
    elif mode == "move player 1":
        canvas.delete('player1')
        canvas.create_rectangle(x-5, y-5, x+5, y+5, fill='blue', tags='player1')
    elif mode == "move player 2":
        canvas.delete('player2')
        canvas.create_rectangle(x-5, y-5, x+5, y+5, fill='purple', tags='player2')
    elif mode == "add number":
        number_token_counter += 1
        canvas.create_oval(x-10, y-10, x+10, y+10, fill='yellow', tags='number_token')
        canvas.create_text(x, y, text=str(number_token_counter), tags='number_token')
    elif mode == "del marker":
        items = canvas.find_closest(x, y)
        if items and items[0] != map_ref:
            if 'number_token' in canvas.gettags(items[0]):
                canvas.delete(items[0])
                #number tokens have two components
                items = canvas.find_closest(x, y)
                if items and items[0] != map_ref and 'number_token' in canvas.gettags(items[0]):
                    canvas.delete(items[0])
            else:
                canvas.delete(items[0])

canvas.bind("<Button-1>", map_click)

# ---------------------------------------------------------------------
# Right Frame: Draw buttons, entries, roll
# ---------------------------------------------------------------------


# Load deck text from Excel
with pd.ExcelFile("decks.xlsx") as excel_file:
    deck_names = excel_file.sheet_names
    deck_texts = {name: [] for name in deck_names}

    # Simulate loading text (replace with actual Excel parsing logic)
    for name in deck_names:
        df = excel_file.parse(name)
        for _, row in df.iterrows():
            text = "\n".join(f"{col}: {row[col]}" for col in df.columns)
            deck_texts[name].append(text)

# Initial deck counts

deck_counts = {name: len(deck_texts[name]) for name in deck_names}
player_deck_texts_p1 = deck_texts[deck_names[0]].copy()  # Initial player deck
player_deck_texts_p2 = deck_texts[deck_names[0]].copy()  # Copy for Player 2

deck_count_var_p1 = tk.StringVar(value=str(len(player_deck_texts_p1)))
deck_count_var_p2 = tk.StringVar(value=str(len(player_deck_texts_p2)))

last_drawn_deck = None
last_drawn_player_deck = None
current_button = None

# Update button text function
def update_button_text(button, deck):
    button.config(text=f"Draw from {deck} ({deck_counts[deck]} cards)")

# Draw card display
drawn_card_label = tk.Label(right_frame, text="Drawn Card:", justify=tk.LEFT)
drawn_card_label.pack()

drawn_card_text = tk.Text(right_frame, height=10, width=27, wrap="word")#, font=("Arial", 10))
drawn_card_text.pack()

deck_exhaust = False
def toggle_deck_exhaust():
    global deck_exhaust, current_button, last_drawn_deck, last_drawn_player_deck
    if deck_exhaust_cbvar.get() == 1:
        deck_exhaust = True
    else:
        deck_exhaust = False
    if current_button and not deck_exhaust:
        current_button.config(bg="SystemButtonFace")
        current_button = None
        last_drawn_deck = None
        last_drawn_player_deck = None

deck_exhaust_cbvar = tk.IntVar()
deck_exhaust_cb = ttk.Checkbutton(right_frame,text="Exhaust source decks",
                                  command=toggle_deck_exhaust, variable=deck_exhaust_cbvar,
                                  onvalue = 1, offvalue = 0).pack()

def draw_card(deck, player=1, button=None):
    global deck_counts, player_deck_texts_p1, player_deck_texts_p2, last_drawn_deck, last_drawn_player_deck, current_button, deck_exhaust
    last_drawn_deck = deck
    if deck_counts[deck] == 0:
        messagebox.showwarning("Empty Deck", f"{deck} is empty.")
        return
    #handle player decks
    if deck == deck_names[0]:
        deck_list = player_deck_texts_p1 if player == 1 else player_deck_texts_p2
        last_drawn_player_deck = player
    else:
        deck_list = deck_texts[deck]
    #Track which deck for removing cards from decks
    if button and deck_exhaust:
        if current_button:
            current_button.config(bg="SystemButtonFace")
        button.config(bg="yellow")
        current_button = button
    card_text = random.choice(deck_list)
    drawn_card_text.delete(1.0, tk.END)
    drawn_card_text.insert(tk.END, card_text)

def add_card_to_player_deck(player=1):
    global player_deck_texts_p1, player_deck_texts_p2, deck_counts, last_drawn_deck, last_drawn_player_deck, deck_exhaust
    drawn_text = drawn_card_text.get(1.0, tk.END).strip()
    if not drawn_text:
        messagebox.showwarning("No Card", "Draw a card first before adding.")
        return
    #remove cards from source deck
    if last_drawn_deck and deck_exhaust:
        if last_drawn_deck == deck_names[0] and last_drawn_player_deck:
            success = trash_card_from_player_deck(player=last_drawn_player_deck)
            if not success:
                return
            if last_drawn_player_deck == 1:
                deck_count_var_p1.set(str(len(player_deck_texts_p1)))
            else:
                deck_count_var_p2.set(str(len(player_deck_texts_p2)))
        elif drawn_text in deck_texts[last_drawn_deck]:
            deck_texts[last_drawn_deck].remove(drawn_text)
            deck_counts[last_drawn_deck] -= 1
            for button in deck_buttons:
                button_deck_name = button.cget("text").split(" (")[0].replace("Draw from ", "")
                update_button_text(button, button_deck_name)
    #add card to target deck
    if player == 1:
        player_deck_texts_p1.append(drawn_text)
        deck_count_var_p1.set(str(len(player_deck_texts_p1)))
    else:
        player_deck_texts_p2.append(drawn_text)
        deck_count_var_p2.set(str(len(player_deck_texts_p2)))
    messagebox.showinfo("Card Added", "Card added to player's deck.")

def trash_card_from_player_deck(player=1):
    global player_deck_texts_p1, player_deck_texts_p2, deck_counts, last_drawn_player_deck
    drawn_text = drawn_card_text.get(1.0, tk.END).strip()
    if not drawn_text:
        messagebox.showwarning("No Card", "Draw a card first before trashing.")
        return False
    deck_texts = player_deck_texts_p1 if player == 1 else player_deck_texts_p2
    if drawn_text not in deck_texts:
        messagebox.showwarning("Not Found", "Drawn card not in player's deck.")
        return False
    if player == 1:
        player_deck_texts_p1.remove(drawn_text)
        deck_count_var_p1.set(str(len(player_deck_texts_p1)))
    else:
        player_deck_texts_p2.remove(drawn_text)
        deck_count_var_p2.set(str(len(player_deck_texts_p2)))
    messagebox.showinfo("Card Trashed", "Removed card from player's deck.")
    return True

# Create draw buttons for each deck

playerdeckbtnframe = ttk.Frame(right_frame)
playerdeckbtnframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(playerdeckbtnframe).pack(side=tk.LEFT, expand=True)
p1deckbutton = tk.Button(playerdeckbtnframe, text=f"Draw from {deck_names[0]} 1")
p1deckbutton.config(command=lambda d=deck_names[0], p=1, b=p1deckbutton: draw_card(d,p,b))
p1deckbutton.pack(side=tk.LEFT)
p2deckbutton = tk.Button(playerdeckbtnframe, text=f"Draw from {deck_names[0]} 2")
p2deckbutton.config(command=lambda d=deck_names[0], p=2, b=p2deckbutton: draw_card(d,p,b))
p2deckbutton.pack(side=tk.LEFT)
tk.Frame(playerdeckbtnframe).pack(side=tk.LEFT, expand=True)

deck_buttons = []
for deck in deck_names[1:]:
    button = tk.Button(right_frame, text=f"Draw from {deck} ({deck_counts[deck]} cards)")
    button.config(command=lambda d=deck, p = 1, b = button: draw_card(d,p,b))
    button.pack()
    deck_buttons.append(button)

# Button to add last drawn card to player deck, or trash it
addcardframe = ttk.Frame(right_frame)
addcardframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(addcardframe).pack(side=tk.LEFT, expand=True)
tk.Button(addcardframe, text="P1 Add Last Drawn Card", command=lambda: add_card_to_player_deck(1)).pack(side=tk.LEFT)
tk.Button(addcardframe, text="P2 Add Last Drawn Card", command=lambda: add_card_to_player_deck(2)).pack(side=tk.LEFT)
tk.Frame(addcardframe).pack(side=tk.LEFT, expand=True)
trashcardframe = ttk.Frame(right_frame)
trashcardframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(trashcardframe).pack(side=tk.LEFT, expand=True)
tk.Button(trashcardframe, text="P1 Trash Last Drawn Card", command=lambda: trash_card_from_player_deck(1)).pack(side=tk.LEFT)
tk.Button(trashcardframe, text="P2 Trash Last Drawn Card", command=lambda: trash_card_from_player_deck(2)).pack(side=tk.LEFT)
tk.Frame(trashcardframe).pack(side=tk.LEFT, expand=True)

#tk.Button(right_frame, text="Add Last Drawn Card to Player Deck", command=add_card_to_player_deck).pack()
#tk.Button(right_frame, text="Trash Last Drawn Card", command=trash_card_from_player_deck).pack()

# Dice Fields

# Boss Dice:
tk.Label(right_frame, text="A Dice:").pack()
pqframe = ttk.Frame(right_frame)
pqframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(pqframe).pack(side=tk.LEFT, expand=True)
p_var = tk.StringVar(value="1")  # Use StringVar for persistent default
p_entry = tk.Entry(pqframe, width=10, textvariable=p_var)
p_entry.pack(side=tk.LEFT)
tk.Label(pqframe, text="d").pack(side=tk.LEFT)
q_var = tk.StringVar(value="6")
q_entry = tk.Entry(pqframe, width=10, textvariable=q_var)
q_entry.pack(side=tk.LEFT)
tk.Frame(pqframe).pack(side=tk.LEFT, expand=True)

# Atk Dice:
tk.Label(right_frame, text="B Dice:").pack()
rsframe = ttk.Frame(right_frame)
rsframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(rsframe).pack(side=tk.LEFT, expand=True)
r_var = tk.StringVar(value="1")
r_entry = tk.Entry(rsframe, width=10, textvariable=r_var)
r_entry.pack(side=tk.LEFT)
tk.Label(rsframe, text="d").pack(side=tk.LEFT)
s_var = tk.StringVar(value="6")
s_entry = tk.Entry(rsframe, width=10, textvariable=s_var)
s_entry.pack(side=tk.LEFT)
tk.Frame(rsframe).pack(side=tk.LEFT, expand=True)

# Def Dice:
tk.Label(right_frame, text="C Dice:").pack()
tuframe = ttk.Frame(right_frame)
tuframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(tuframe).pack(side=tk.LEFT, expand=True)
t_var = tk.StringVar(value="1")
t_entry = tk.Entry(tuframe, width=10, textvariable=t_var)
t_entry.pack(side=tk.LEFT)
tk.Label(tuframe, text="d").pack(side=tk.LEFT)
u_var = tk.StringVar(value="6")
u_entry = tk.Entry(tuframe, width=10, textvariable=u_var)
u_entry.pack(side=tk.LEFT)
tk.Frame(tuframe).pack(side=tk.LEFT, expand=True)

# Roll dice button
roll_result_label = tk.Label(right_frame, text="Roll Result:")
roll_result_label.pack()

def roll_dice():
    global p_entry, q_entry, r_entry, s_entry, t_entry, u_entry
    try:
        # Use get() with default from StringVar if empty
        p = int(p_entry.get() or p_var.get())  # Fallback to StringVar default
        q = int(q_entry.get() or q_var.get())
        r = int(r_entry.get() or r_var.get())
        s = int(s_entry.get() or s_var.get())
        t = int(t_entry.get() or t_var.get())
        u = int(u_entry.get() or u_var.get())
        
        pdq_roll = [random.randint(1, q) for _ in range(p)]
        rds_roll = [random.randint(1, s) for _ in range(r)]
        tdu_roll = [random.randint(1, u) for _ in range(t)]
        
        result = f"A: {pdq_roll} Sum: {sum(pdq_roll)}\nB: {rds_roll} Sum: {sum(rds_roll)}\nC: {tdu_roll} Sum: {sum(tdu_roll)}"
        roll_result_label.config(text=result)
    except ValueError as v:
        messagebox.showerror("Error", "Invalid numbers in fields: " + str(v))

roll_button = tk.Button(right_frame, text="Roll Dice", command=roll_dice)
roll_button.pack(pady=5)

#Round Counter
roundframe = ttk.Frame(right_frame)
roundframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(roundframe).pack(side=tk.LEFT, expand=True)
tk.Label(roundframe, text="Scratch pad 1:").pack(side=tk.LEFT)
g_entry = tk.Entry(roundframe, width=10)
g_entry.pack(side=tk.LEFT)
g_entry.insert(0, "1")  # Default
tk.Frame(roundframe).pack(side=tk.LEFT, expand=True)

#Boss HP
bosshpframe = ttk.Frame(right_frame)
bosshpframe.pack(fill=tk.X, padx=5, pady=2)
tk.Frame(bosshpframe).pack(side=tk.LEFT, expand=True)
tk.Label(bosshpframe, text="Scratch pad 2:").pack(side=tk.LEFT)
hp_entry = tk.Entry(bosshpframe, width=10)
hp_entry.pack(side=tk.LEFT)
tk.Frame(bosshpframe).pack(side=tk.LEFT, expand=True)

def show_rules():
    # Create a new top-level window
    rules_win = tk.Toplevel(root)
    rules_win.title("Rules of Play")

    # Frame for text + scrollbar
    frame = tk.Frame(rules_win)
    frame.pack(fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Text area
    rules_text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    rules_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=rules_text.yview)

    # Insert rules (replace with your actual rules text)
    with open('Rules of Play.txt', 'r') as file:
        rules = file.read()

    rules_text.insert(tk.END, rules)
    rules_text.config(state=tk.DISABLED)  # Make read-only

# Add the "Show Rules" button to your right_frame
tk.Button(right_frame, text="Show Rules", command=show_rules).pack()

# ---------------------------------------------------------------------
# hand frames: cards in hand and gear
# ---------------------------------------------------------------------

#Cards in hand area

hand_texts_p1 = [tk.Text(hand_frame_p1, height=5, width=27, wrap="word") for _ in range(5)]
for t in hand_texts_p1:
    t.pack()
    
hand_texts_p2 = [tk.Text(hand_frame_p2, height=5, width=27, wrap="word") for _ in range(5)]
for t in hand_texts_p2:
    t.pack()

def draw_hand(player=1):
    global player_deck_texts_p1, player_deck_texts_p2, deck_counts
    deck_texts = player_deck_texts_p1 if player == 1 else player_deck_texts_p2
    count_var = deck_count_var_p1 if player == 1 else deck_count_var_p2
    hand_texts = hand_texts_p1 if player == 1 else hand_texts_p2
    if len(deck_texts) < 5:
        messagebox.showwarning("Not Enough Cards", f"Player {player}'s deck has fewer than 5 cards.")
        return
    hand = random.sample(deck_texts, 5)
    for t, text in zip(hand_texts, hand):
        t.delete(1.0, tk.END)
        t.insert(tk.END, text)


p1dcframe = ttk.Frame(hand_frame_p1)
p1dcframe.pack(fill=tk.X, padx=5, pady=2)
tk.Label(p1dcframe, text="P1 Deck Count:").pack(side=tk.LEFT)
tk.Label(p1dcframe, textvariable=deck_count_var_p1).pack(side=tk.LEFT)

p2dcframe = ttk.Frame(hand_frame_p2)
p2dcframe.pack(fill=tk.X, padx=5, pady=2)
tk.Label(p2dcframe, text="P2 Deck Count:").pack(side=tk.LEFT)
tk.Label(p2dcframe, textvariable=deck_count_var_p2).pack(side=tk.LEFT)
tk.Button(hand_frame_p1, text="P1 Draw Hand", command=lambda: draw_hand(1)).pack()
tk.Button(hand_frame_p2, text="P2 Draw Hand", command=lambda: draw_hand(2)).pack()

#player 1
#HP and G
tk.Label(hand_frame_p1, text="P1 HP").pack()
hp_entry_p1 = tk.Entry(hand_frame_p1)
hp_entry_p1.pack()
hp_entry_p1.insert(0, "10")
tk.Label(hand_frame_p1, text="P1 ?").pack()
g_entry_p1 = tk.Entry(hand_frame_p1)
g_entry_p1.pack()
g_entry_p1.insert(0, "0")

#Gear
tk.Label(hand_frame_p1, text="P1 Scratch 1:").pack()
gear1_p1 = tk.Text(hand_frame_p1, height=5, width=25, wrap="word")
gear1_p1.pack()
tk.Label(hand_frame_p1, text="P1 Scratch 2:").pack()
gear2_p1 = tk.Text(hand_frame_p1, height=5, width=25, wrap="word")
gear2_p1.pack()
tk.Label(hand_frame_p1, text="P1 Scratch 3:").pack()
gear3_p1 = tk.Text(hand_frame_p1, height=5, width=25, wrap="word")
gear3_p1.pack()

#Player 2
#HP and G
tk.Label(hand_frame_p2, text="P2 HP").pack()
hp_entry_p2 = tk.Entry(hand_frame_p2)
hp_entry_p2.pack()
hp_entry_p2.insert(0, "10")
tk.Label(hand_frame_p2, text="P2 ?").pack()
g_entry_p2 = tk.Entry(hand_frame_p2)
g_entry_p2.pack()
g_entry_p2.insert(0, "0")
#Gear
tk.Label(hand_frame_p2, text="P2 Scratch 1:").pack()
gear1_p2 = tk.Text(hand_frame_p2, height=5, width=25, wrap="word")
gear1_p2.pack()
tk.Label(hand_frame_p2, text="P2 Scratch 2:").pack()
gear2_p2 = tk.Text(hand_frame_p2, height=5, width=25, wrap="word")
gear2_p2.pack()
tk.Label(hand_frame_p2, text="P2 Scratch 3:").pack()
gear3_p2 = tk.Text(hand_frame_p2, height=5, width=25, wrap="word")
gear3_p2.pack()

root.mainloop()
