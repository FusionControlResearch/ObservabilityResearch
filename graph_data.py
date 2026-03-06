import pandas as pd
import matplotlib.pyplot as plt

def plot_obs_loss(file1_path, file2_path, x_column, y_column):
    """
    Reads two CSV files and plots the specified columns on the same graph.

    :param file1_path: Path to the first CSV file.
    :param file2_path: Path to the second CSV file.
    :param x_column: The name of the common column to use for the x-axis.
    :param y_column: The name of the common column to use for the y-axis.
    """
    try:
        # Read the CSV files into pandas DataFrames
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # Create a single figure and axis object
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data from the first DataFrame
        ax.plot(df1[x_column], df1[y_column], label=f'probing disabled', color='blue', linestyle='--')
        
        # Plot data from the second DataFrame on the same axis
        ax.plot(df2[x_column], df2[y_column], label=f'probing enabled', color='red', linestyle='--')

        # Add labels, title, and a legend
        ax.set_ylabel("Observability loss L_obs")
        ax.set_xlabel("time")
        ax.set_title("Observability collapse and recovery")
        ax.axhline(y=4.05, color='green', linestyle='-')
        ax.legend()


        # Display the plot
        plt.show()

    except FileNotFoundError:
        print(f"Error: One of the files not found. Check paths: {file1_path}, {file2_path}")
    except KeyError as e:
        print(f"Error: Column name not found. Ensure '{e.args[0]}' exists in both CSV files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def plot_nom_obs_loss(file1_path, file2_path, x_column, y_column):
    """
    Reads two CSV files and plots the specified columns on the same graph.

    :param file1_path: Path to the first CSV file.
    :param file2_path: Path to the second CSV file.
    :param x_column: The name of the common column to use for the x-axis.
    :param y_column: The name of the common column to use for the y-axis.
    """
    try:
        # Read the CSV files into pandas DataFrames
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # Create a single figure and axis object
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data from the first DataFrame
        ax.plot(df1[x_column], df1[y_column], label=f'probing disabled', color='blue', linestyle='--')
        
        # Plot data from the second DataFrame on the same axis
        ax.plot(df2[x_column], df2[y_column], label=f'probing enabled', color='red', linestyle='--')

        # Add labels, title, and a legend
        ax.set_xlabel("time")
        ax.set_ylabel("Nominal Observability loss L_obs_nom")
        ax.set_title("Nominal Observability collapse and recovery")
        ax.axhline(y=4.05, color='green', linestyle='-')
        ax.legend()


        # Display the plot
        plt.show()

    except FileNotFoundError:
        print(f"Error: One of the files not found. Check paths: {file1_path}, {file2_path}")
    except KeyError as e:
        print(f"Error: Column name not found. Ensure '{e.args[0]}' exists in both CSV files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def plot_probing(file1_path, file2_path, x_column, y_column):
    """
    Reads two CSV files and plots the specified columns on the same graph.

    :param file1_path: Path to the first CSV file.
    :param file2_path: Path to the second CSV file.
    :param x_column: The name of the common column to use for the x-axis.
    :param y_column: The name of the common column to use for the y-axis.
    """
    try:
        # Read the CSV files into pandas DataFrames
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # Create a single figure and axis object
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data from the first DataFrame
        ax.plot(df1[x_column], df1[y_column], label=f'probing disabled', color='blue', linestyle='--')
        
        # Plot data from the second DataFrame on the same axis
        ax.plot(df2[x_column], df2[y_column], label=f'probing enabled', color='red', linestyle='--')

        # Add labels, title, and a legend
        ax.set_xlabel("time")
        ax.set_ylabel("Probing active")
        ax.set_title("Supervisor-triggered probing")
        ax.legend()

        # Display the plot
        plt.show()

    except FileNotFoundError:
        print(f"Error: One of the files not found. Check paths: {file1_path}, {file2_path}")
    except KeyError as e:
        print(f"Error: Column name not found. Ensure '{e.args[0]}' exists in both CSV files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def plot_gamma(file1_path, file2_path, x_column, y_column):
    """
    Reads two CSV files and plots the specified columns on the same graph.

    :param file1_path: Path to the first CSV file.
    :param file2_path: Path to the second CSV file.
    :param x_column: The name of the common column to use for the x-axis.
    :param y_column: The name of the common column to use for the y-axis.
    """
    try:
        # Read the CSV files into pandas DataFrames
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)

        # Create a single figure and axis object
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data from the first DataFrame
        ax.plot(df1[x_column], df1[y_column], label=f'probing disabled', color='blue', linestyle='--')
        
        # Plot data from the second DataFrame on the same axis
        ax.plot(df2[x_column], df2[y_column], label=f'probing enabled', color='red', linestyle='--')

        # Add labels, title, and a legend
        ax.set_xlabel("time")
        ax.set_ylabel("Estimated gamma")
        ax.axhline(1.0, linestyle="--")
        ax.set_title("Observability Change Before and After Disruption")
        ax.legend()

        # Display the plot
        plt.show()

    except FileNotFoundError:
        print(f"Error: One of the files not found. Check paths: {file1_path}, {file2_path}")
    except KeyError as e:
        print(f"Error: Column name not found. Ensure '{e.args[0]}' exists in both CSV files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Example Usage ---
# Replace 'data1.csv' and 'data2.csv' with your actual file paths.
# Replace 'X_Axis_Col' and 'Y_Axis_Col' with your actual column names.
plot_obs_loss('L_obs_data_no_probe.csv', 'L_obs_data_probe.csv', 'x_value', 'y_value')
plot_nom_obs_loss('L_obs_nom_data_no_probe.csv', 'L_obs_nom_data_probe.csv', 'x_value', 'y_value')
plot_probing('probe_off_data.csv', 'probe_on_data.csv', 'x_value', 'y_value')
plot_gamma('gamma_data_no_probe.csv', 'gamma_data_probe.csv', 'x_value', 'y_value')