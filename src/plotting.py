import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Colour follows the series in every chart. Total is the aggregate, so it takes
# neutral ink and the three categories take the categorical hues.
SERIES_COLORS = {
    "Total": INK_SECONDARY,
    "Furniture": "#2a78d6",
    "Office Supplies": "#eb6834",
    "Technology": "#1baf7a",
}

# One hue, light -> dark, for ordered values such as successive years.
ORDINAL_BLUES = ["#86b6ef", "#2a78d6", "#104281"]

# Below / above a neutral midpoint.
DIVERGING = LinearSegmentedColormap.from_list(
    "red_gray_blue", ["#e34948", "#f0efec", "#3987e5"]
)

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

thousands = FuncFormatter(lambda value, _: f"${value / 1000:,.0f}K")


def apply_style():
    """Set the matplotlib defaults shared by every chart in the project."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.size": 10,
        "text.color": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": INK_SECONDARY,
        "axes.edgecolor": AXIS,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_SECONDARY,
        "ytick.labelcolor": INK_SECONDARY,
        "ytick.left": False,
        "lines.linewidth": 2,
        "legend.frameon": False,
    })
