import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from io import BytesIO
import base64


def bar_single(items, total, title=None, highlight=None):
    """Create single bar chart.

    Args:
        items (list): list of tuples (item_name, value) where
            value is number of job postings with the item
        total (int): total number of job postings in the database
        title (str): title of the chart
        highlight (int): position in items of the item to be highlighted

    Returns:
        base64 encoded bar chart (str).
    """
    # restructure data
    names, values = zip(*items)
    # normalize values
    values = [val / total * 100 for val in values]
    # set colours
    color = ['#2f4b7c' for i in range(len(names))]
    if highlight:
        color[highlight] = '#ff7c43'
    # create chart
    fig, ax = create_figure()
    x = range(len(values))
    ax.bar(x, values, color=color, width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation='vertical')
    ax.set_title(title)
    ax.set_ylabel('% of all job postings')
    return get_chart_base64(fig)


def bar_double(items, total, title=None, legend=None, highlight=None):
    """Create double bar chart.

    Args:
        items (list): list of tuples (item_name, value1, value2) where
            value1 is number of job postings with the item and
            value2 is number of job postings with the item which satisfy
                the criterion
        total (tuple): (value1, value2) where
            value1 is total number of job postings in the database and
            value2 is total number of postings in the database which satisfy
                the criterion
        title (str): title of the chart
        legend (tuple): (series1_name, series2_name)
        highlight (int): position in items of the item to be highlighted

    Returns:
        base64 encoded bar chart (str).
    """
    # restructure data
    names, values1, values2 = zip(*items)
    # normalize values
    values1 = [val / total[0] * 100 for val in values1]
    values2 = [val / total[1] * 100 for val in values2]
    # set colours
    color2 = ['#ff7c43' for i in range(len(names))]
    color1 = ['#2f4b7c' for i in range(len(names))]
    # create chart
    fig, ax = create_figure()
    width = 0.35
    ind = range(len(values1))
    ax.bar(ind, values2, color=color2, width=width, label=legend[1])
    ax.bar([x + width for x in ind], values1, color=color1, width=width, label=legend[0])
    ax.set_xticks([x + width/2 for x in ind])
    ax.set_xticklabels(names, rotation='vertical')
    ax.set_title(title)
    ax.set_ylabel('% of all job postings')
    ax.legend()
    return get_chart_base64(fig)


def create_figure():
    """Create new Figure and add an Axes to it

    Returns:
        instance of matplotlib.figure.Figure
        instance of matplotlib.axes.Axes
    """
    fig = Figure(tight_layout=True)
    # Attach canvas to figure
    FigureCanvasAgg(fig)
    # Add Axes to figure
    ax = fig.add_subplot(111)
    return fig, ax


def get_chart_base64(fig):
    """Save chart to buffer and encode in Base64 scheme

    Args:
        fig (object): instance of matplotlib.figure.Figure

    Returns:
        Base64 encoded chart object (str)
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300)
    fig.clf()
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64
