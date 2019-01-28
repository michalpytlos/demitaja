import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def bar_single(items, total, title=None, highlight=None):
    """Create simple bar chart.

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
    x = range(len(values))
    plt.bar(x, values, color=color, width=0.5)
    plt.xticks(x, names,  rotation='vertical')
    plt.title(title)
    plt.ylabel('% of all job postings')
    plt.tight_layout()
    return get_chart_base64()


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
    width = 0.35
    ind = range(len(values1))
    plt.bar(ind, values2, color=color2, width=width, label=legend[1])
    plt.bar([x + width for x in ind], values1, color=color1, width=width, label=legend[0])
    plt.xticks([x + width/2 for x in ind], names, rotation='vertical')
    plt.title(title)
    plt.ylabel('% of all job postings')
    plt.legend()
    plt.tight_layout()
    return get_chart_base64()


def get_chart_base64():
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close()
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64
