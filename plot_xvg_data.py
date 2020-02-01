import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes


def read_xvg(file_name):
    f = open(file_name, "r")
    lines = f.readlines()

    plot_kwargs = {}
    plot_operations = {}
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith("@TYPE"):
            _type = line.split()[-1]
            if _type != "xy":
                print("Unsupport data format")
                sys.exit(1)
        if line.startswith("#"):
            continue
        if line.startswith("@ s0 "):
            break
        if line.startswith("@"):
            _update_plot_kwargs_and_operations(plot_kwargs, plot_operations, line)
        else:
            break

    lines = lines[i:]

    dtypes = [("time", np.float)]
    
    for i in range(len(lines)):
        line = lines[i]
        if not line.startswith("@ s" + str(i)):
            break
        label = _extract_value_from_line("legend", line)
        dtypes.append((label, np.float))        

    data_lines = lines[i:]

    if len(dtypes) > 1:
        data = _read_data_into_array_with_dtypes(data_lines, dtypes)
    else:
        data = _read_data_into_array_without_dtypes(data_lines)
                
    return data, plot_kwargs, plot_operations


def _read_data_into_array_with_dtypes(data_lines, dtypes):
    data = np.empty(len(data_lines), dtype=dtypes)
    for j in range(len(data_lines)):        
        data_line_j = np.fromstring(data_lines[j], dtype=float, sep=" ")
        for k in range(len(dtypes)):
            data[dtypes[k][0]][j] = data_line_j[k]
    return data


def _read_data_into_array_without_dtypes(data_lines):
    first_data_line = np.fromstring(data_lines[0], dtype=float, sep=" ")
    data = np.empty((len(first_data_line), len(data_lines)), dtype=np.float)
    for j in range(len(data_lines)):
        data[:, j] = np.fromstring(data_lines[j], dtype=float, sep=" ")
    return data


def _update_plot_kwargs_and_operations(plot_kwargs: dict, plot_operations: dict, line: str):
    line = " ".join(line.split())
    if line.count("title"):
        title = _extract_value_from_line("title", line)
        plot_operations["title"] = [Axes.set_title, [title]]
        return

    if line.count("xaxis label"):
        xaxis_label = _extract_value_from_line("xaxis label", line)
        plot_operations["xaxis_label"] = [Axes.set_xlabel, [xaxis_label]]
        return

    if line.count("yaxis label"):
        yaxis_label = _extract_value_from_line("yaxis label", line)
        plot_operations["yaxis_label"] = [Axes.set_ylabel, [yaxis_label]]
        return


def _extract_value_from_line(key: str, line: str):
    value = line.split(key)[-1]
    value = value.strip().replace("\"", "")
    return value


def plot_xvg_data(ax, data, plot_kwargs, plot_operations):

    names = data.dtype.names

    if names:
        for i in range(1, len(names)):
            ax.plot(data[names[0]], data[names[i]], label=names[i], **plot_kwargs)
    else:
        for i in range(1, data.shape[0]):
            ax.plot(data[0, :], data[i, :])

    for function, arguments in plot_operations.values():
        function(ax, *arguments)


def main():
    if len(sys.argv) != 2:
        msg = "Requires exactly one argument: an xvg file name!"
        raise RuntimeError(msg)
    xvg_file_name = sys.argv[1]

    if not os.path.isfile(xvg_file_name):
        msg = "file \"%s\" not found!" % xvg_file_name
        raise IOError(msg)

    f, ax = plt.subplots(1, 1)

    data, kwargs, operations = read_xvg(xvg_file_name)

    plot_xvg_data(ax, data, kwargs, operations)
    ax.legend()
    plt.savefig(sys.argv[1][:-4] + ".png", dpi=400)

main()