import numpy as np
from numpy.f2py.auxfuncs import throw_error


class Color:
    """
    Class to represent an RGB color.
    """

    def __init__(self, r, g, b, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def lerp(color1, color2, t):
        """
        Performs linear interpolation between two colors.

        Args:
            color1 (Color): The starting color.
            color2 (Color): The ending color.
            t (float): The interpolation factor, ranging from 0 to 1.

        Returns:
            Color: The interpolated color.
        """
        return Color(
            r=color1.r + t * (color2.r - color1.r),
            g=color1.g + t * (color2.g - color1.g),
            b=color1.b + t * (color2.b - color1.b),
            a=color1.a + t * (color2.a - color1.a)
        )

    def to_array(self):
        return [self.r, self.g, self.b, self.a]


class HeatmapColors:
    """
    Class to compute colors based on a normalized value.
    """

    # Predefined color palettes
    COLOR_PALETTE_POSITIVE = [
        Color(1.0, 1.0, 1.0),  # White
        Color(1.0, 1.0, 0.0),  # Yellow
        Color(1.0, 0.0, 0.0),  # Red
    ]
    COLOR_PALETTE_NEGATIVE = [
        Color(1.0, 1.0, 1.0),  # White
        Color(0.0, 1.0, 1.0),  # Cyan
        Color(0.0, 0.0, 1.0),  # Blue
    ]

    @staticmethod
    def get_color_from_value(values, positive_breakpoints=None, negative_breakpoints=None):
        """
        Returns colors based on an array of values.

        Args:
            values (np.ndarray): Array of values.
            positive_breakpoints (np.ndarray): Array of breakpoints to use for positive values.
            negative_breakpoints (np.ndarray): Array of breakpoints to use for negative values.

        Returns:
            List[Color]: List of colors corresponding to the input values.
        """
        positive_mask = values >= 0

        colors = np.where(
            positive_mask[:, None],
            HeatmapColors.color_from_value(np.abs(values), HeatmapColors.COLOR_PALETTE_POSITIVE, positive_breakpoints),
            HeatmapColors.color_from_value(np.abs(values), HeatmapColors.COLOR_PALETTE_NEGATIVE, negative_breakpoints)
        )

        return colors

    @staticmethod
    def color_from_value(absolute_values, color_palette, break_points=None):
        """
        Returns a color from the palette based on the absolute value. Breakpoints indicates range of values where each color of the palette is used

        Args:
            absolute_values (np.ndarray): A positive value between 0 and 1.
            color_palette (list of Color): The color palette to use.
            break_points (array of 3 elements): The break points of the palette.

        Returns:
            List[Color]: The interpolated color from the palette.
        """
        if break_points is None:
            # Breakpoints are automatically assigned to be evenly spaced in the interval of values
            num_breakpoints = len(color_palette)
            step = (absolute_values.max() - absolute_values.min()) / num_breakpoints
            break_points = [absolute_values.min() + (i * step) for i in range(0, num_breakpoints)]

        break_points = np.abs(np.asarray(break_points))

        if len(break_points) != len(color_palette):
            raise ValueError("Number of breakpoints must be equal to number of colors")

        return HeatmapColors.lerp_colors(absolute_values, break_points, color_palette)

    @staticmethod
    def lerp_colors(values, break_points, color_palette):
        # digitize gives a value between 0 and len(break_points)
        color_indices = np.clip(np.digitize(values, break_points).astype(np.int32) - 1, 0,
                                len(color_palette) - 2)

        # Interval between 2 break points that each pair of color represent
        interval_delta = break_points[color_indices + 1] - break_points[color_indices]
        t = (values - break_points[color_indices]) / interval_delta
        t = np.clip(t, 0, 1)

        interpolated_colors = [
            Color.lerp(color_palette[idx], color_palette[idx + 1], t_val).to_array()
            for idx, t_val in zip(color_indices, t)
        ]

        return np.array(interpolated_colors)
