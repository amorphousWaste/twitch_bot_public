#!/usr/bin/env python
"""From:
https://www.machinelearningplus.com/plots/top-50-matplotlib-visualizations-the-master-plots-python/
"""

import asyncio
import pandas
from matplotlib import pyplot


async def example():
    # Import Data
    df = pandas.read_csv(
        'https://github.com/selva86/datasets/raw/master/AirPassengers.csv'
    )
    df.rename(columns={'value': 'traffic'}, inplace=True)

    font_dict = {
        'family': 'sans-serif',
        'color': 'black',
        'weight': 'normal',
        'size': 12,
    }

    # Draw Plot
    pyplot.figure(figsize=(16, 10), tight_layout=True, dpi=100)
    pyplot.plot(
        'date',
        'traffic',
        data=df,
        color='purple',
        linestyle='solid',
        linewidth=1,
    )

    # Decoration
    pyplot.ylim(50, 750)
    xtick_location = df.index.tolist()[::12]
    xtick_labels = [x[-4:] for x in df.date.tolist()[::12]]
    pyplot.xticks(
        ticks=xtick_location,
        labels=xtick_labels,
        rotation=45,
        fontsize=12,
        horizontalalignment='center',
        alpha=0.7,
    )

    pyplot.yticks(fontsize=12, alpha=0.7)
    pyplot.title("Air Passengers Traffic (1949 - 1969)", fontdict=font_dict)
    pyplot.xlabel("Date/Time", fontdict=font_dict)
    pyplot.ylabel("Viewer Count", fontdict=font_dict)
    pyplot.grid(
        axis='both', alpha=0.2, color='black', linestyle='--', linewidth=0.5
    )

    # Remove borders
    pyplot.gca().spines["top"].set_alpha(0.0)
    pyplot.gca().spines["bottom"].set_alpha(0.3)
    pyplot.gca().spines["right"].set_alpha(0.0)
    pyplot.gca().spines["left"].set_alpha(0.3)
    pyplot.show()


async def run():
    pass


if __name__ == '__main__':
    asyncio.run(example())
