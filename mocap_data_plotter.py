import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # <-- need to keep this for 3D plotting

# helper function for getting adjacent X/Y/Z columns
def create_xyz_tuples(column_data, name_row_idx):
    pos_row_idx = name_row_idx + 2
    axis_row_idx = name_row_idx + 3
    column_xyz_pts = []
    for i in range(0, len(column_data) - 2):
        col = column_data[i]
        col = list(filter(lambda a: a != '', col))
        # checking if this column is a position X column
        if col[pos_row_idx] == 'Position' and col[axis_row_idx] == 'X':
            col_next = column_data[i + 1]
            col_next = list(filter(lambda a: a != '', col_next))
            col_nextnext = column_data[i + 2]
            col_nextnext = list(filter(lambda a: a != '', col_nextnext))
            # checking if next two columns are Y and Z columns
            if col_next[axis_row_idx] == 'Y' and col_nextnext[axis_row_idx] == 'Z':
                column_xyz_pts.append([col, col_next, col_nextnext])
    return column_xyz_pts

# helper function for plotting data points with color gradients
def plot_xyz_pts(data_xyz_pts, ax, name_row_idx, color, time_data):
    data_row_idx = name_row_idx + 4
    for triplet in data_xyz_pts:
        # x, y, and z values to plot
        x_vals = np.array(triplet[0][data_row_idx:]).astype(np.float)
        y_vals = np.array(triplet[1][data_row_idx:]).astype(np.float)
        z_vals = np.array(triplet[2][data_row_idx:]).astype(np.float)
        # print('x shape: ', np.shape(x_vals))
        # print('y shape: ', np.shape(y_vals))
        # print('z shape: ', np.shape(z_vals))

        # real second values for plotting dimension vs time
        real_time_vals = np.array(time_data[data_row_idx:len(x_vals) + data_row_idx]).astype(np.float)

        # tune 0.2 and 0.8 for lighter/darker points
        gradient_values = np.linspace(0.2, 0.8, num=len(x_vals))

        # getting a color gradient for each point
        colors = np.matmul(np.reshape(gradient_values, (len(gradient_values), 1)), np.reshape(color, (1, len(color))))

        print(np.shape(colors))

        line = ax.scatter(x_vals, z_vals, c=colors)
    return ax

# helper function for getting the maximum column index to prevent strange
# parsing issues with differently-sized columns
def get_column_names(data_file, data_file_delimiter):

    # The max column count a line in the file could have
    largest_column_count = 0

    # Loop the data lines
    with open(data_file, 'r') as temp_f:
        # Read the lines
        lines = temp_f.readlines()

        for l in lines:
            # Count the column count for the current line
            column_count = len(l.split(data_file_delimiter)) + 1

            # Set the new most column count
            largest_column_count = column_count if largest_column_count < column_count else largest_column_count

    # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
    column_names = [i for i in range(0, largest_column_count)]
    return column_names

# helper function to parse CSV and find the
# row that corresponds to the names of the markers
def get_row_name_idx(csv_data):
    name_row_idx = 0
    for i in range(0, len(csv_data)):
        row = csv_data[i]
        if row[1] == 'Name':
            return i

def main():
    ## USER INPUTS ##
    data_file = 'AtlasTake_02.csv'
    x_label = 'Time [sec]'
    y_label = 'Time [sec]'
    atlas_color = [1, 0, 0]
    human_color = [0, 0, 1]
    atlas_marker_name = 'Atlas'
    human_marker_name = 'Human2'
    figure_width = 10
    figure_height = 7
    #################

    atlas_data = []
    human_data = []
    data_file_delimiter = ','

    column_names = get_column_names(data_file, data_file_delimiter)

    df = pd.read_csv(data_file, delimiter=data_file_delimiter, names=column_names)
    csv_data = df.to_numpy()

    name_row_idx = get_row_name_idx(csv_data)
    idx = 0
    time_data = []
    for name in csv_data[name_row_idx]:
        # checking for columns that are for Atlas
        if atlas_marker_name == str(name):
            atlas_data.append([row[idx] for row in csv_data])
        # checking for columns that are for human
        if human_marker_name == str(name):
            human_data.append([row[idx] for row in csv_data])
        # checking for time columns
        if 'Name' == str(name):
            time_data = [row[idx] for row in csv_data]
        idx += 1

    # Taking the Atlas and Human columns and coupling the corresponding X/Y/Z columns
    atlas_xyz_pts = create_xyz_tuples(atlas_data, name_row_idx)
    human_xyz_pts = create_xyz_tuples(human_data, name_row_idx)

    # setting up figure
    fig, ax = plt.subplots()
    fig.set_size_inches(figure_width, figure_height)

    # plotting points
    ax = plot_xyz_pts(atlas_xyz_pts, ax, name_row_idx, atlas_color, time_data)
    ax = plot_xyz_pts(human_xyz_pts, ax, name_row_idx, human_color, time_data)

    # dummy figure to create red/blue legend dots
    fig2, ax2 = plt.subplots()
    custom_dots = [ax2.scatter([0], [0], color=atlas_color),
                   ax2.scatter([0], [0], color=human_color)]
    ax.legend(custom_dots, ['Atlas', 'Human'])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # ax.set_zlabel('Z [m]')
    plt.show()

main()