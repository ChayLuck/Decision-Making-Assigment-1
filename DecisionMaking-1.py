import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        process_file(file_path)

def process_file(file_path):
    # Reading the CSV file
    df = pd.read_csv(file_path)

    strategies = df.columns[1:].tolist()  # All columns except the first
    outcomes = df.iloc[:, 0].tolist()      # First column (outcomes)

    row1 = df.iloc[0, 1:].to_numpy()  
    row2 = df.iloc[1, 1:].to_numpy()  

    # Convert to a 2D array for calculations
    array_data = pd.DataFrame([row1, row2]).to_numpy()

    # Calculate methods
    optimistic_result = optimistic_method(array_data, strategies)
    
    pessimistic_result = pessimistic_method(array_data, strategies)
    
    laplace_result = laplace_method(array_data, strategies)
    
    savage_result = savage_method(row1,row2,array_data, strategies)

    hurwitz_values, h_values = hurwitz_method(array_data)

    # Update the table with results
    update_table(optimistic_result, pessimistic_result, laplace_result, savage_result)
    update_hurwitz_table(hurwitz_values, strategies)
    plot_hurwitz_graph(hurwitz_values, strategies, h_values)


def optimistic_method(array, strategies):

    max_index = array.argmax()  
    max_value = array.flatten()[max_index]  
    
    row_index = max_index // array.shape[1] 
    col_index = max_index % array.shape[1]   

    result = f"{strategies[col_index]} {max_value}"  
    return result

def pessimistic_method(array, strategies):

    min_values = array.min(axis=0)  
    
    max_of_mins = min_values.max() 
    
    strategy_index = min_values.argmax()  
    strategy = strategies[strategy_index]  
    
    result = f"{strategy} {max_of_mins}"
    return result

def laplace_method(array, strategies):

    averages = array.mean(axis=0) 
    
    max_average = averages.max()
    strategy_index = averages.argmax()  
    strategy = strategies[strategy_index]  
    
    result = f"{strategy} {max_average:.2f}"  
    return result

def savage_method(row1, row2, array, strategies):

    max_value_row1 = row1.max() 
    max_value_row2 = row2.max()  

    regret1 = max_value_row1 - row1  
    regret2 = max_value_row2 - row2  

    max_regret = np.maximum(regret1, regret2)  

    min_max_regret_index = max_regret.argmin() 
    min_max_regret_value = max_regret[min_max_regret_index]  
    strategy = strategies[min_max_regret_index] 
    
    result = f"{strategy} {min_max_regret_value}"
    return result

def hurwitz_method(array):
    hurwitz_values = []
    h_values = np.linspace(0, 1, 11) 
    for h in h_values:
        hurwitz_row = []
        for col in array.T:
            value = h * col.max() + (1 - h) * col.min()
            hurwitz_row.append(round(value, 2))
        hurwitz_values.append([h] + hurwitz_row)
    return hurwitz_values, h_values  

def update_hurwitz_table(hurwitz_values, strategies):

    for row in tree.get_children():
        tree.delete(row)
        
    for row in hurwitz_values:
        tree_hurwitz.insert("", "end", values=[row[0]] + row[1:])

def plot_hurwitz_graph(hurwitz_values, strategies, h_values):
    fig, ax = plt.subplots()
    hurwitz_values_array = np.array(hurwitz_values)[:, 1:].T 
    for idx, strategy_values in enumerate(hurwitz_values_array):
        ax.plot(h_values, strategy_values, marker='o', label=strategies[idx])

    ax.set_xlabel('h')
    ax.set_ylabel('Alternative scores')
    ax.set_title('Hurwitz Scores Across h')
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

def update_table(optimistic_result, pessimistic_result, laplace_result, savage_result):
    # Clear the existing table
    for row in tree.get_children():
        tree.delete(row)

    tree.insert("", "end", values=["Optimistic Result", optimistic_result])
    tree.insert("", "end", values=["Pessimistic Result", pessimistic_result])
    tree.insert("", "end", values=["Laplace Result", laplace_result])
    tree.insert("", "end", values=["Savage Result", savage_result])


# Setting up the Tkinter window
root = tk.Tk()
root.title("CSV File Processor")

# Create a button to select the CSV file
select_button = tk.Button(root, text="Select CSV File", command=select_file)
select_button.pack(pady=20)

# Create a Treeview widget for displaying the results
tree = ttk.Treeview(root, height=4, columns=("Description", "Result"), show='headings')
tree.heading("Description", text="Description")
tree.heading("Result", text="Result")
tree.pack(pady=20)

# Hurwitz table
columns = ["h"] + ["status quo", "expansion", "building HQ", "collaboration"]
tree_hurwitz = ttk.Treeview(root, height=11, columns=columns, show="headings")
for col in columns:
    tree_hurwitz.heading(col, text=col)
tree_hurwitz.pack(pady=25)

# Start the Tkinter event loop
root.mainloop()