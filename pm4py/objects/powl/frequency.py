"""
Frequency tagging for POWL objects.

Provides mixin class for adding frequency information to POWL nodes.
This is part of making PM4Py self-contained for POWL functionality.
"""

from typing import Optional, Tuple


class FrequencyTagged:
    """
    Mixin class for frequency-tagged POWL objects.

    Adds min_freq and max_freq attributes to POWL nodes for
    frequency-based process mining operations.

    This is compatible with the official POWL package's frequency tagging
    but implemented independently to maintain Apache 2.0 license compatibility.
    """

    def __init__(self, *args, min_freq: int = 1, max_freq: Optional[int] = None, **kwargs):
        """
        Initialize frequency tagging.

        Args:
            min_freq: Minimum frequency (default: 1)
            max_freq: Maximum frequency (None for unbounded)
        """
        super().__init__(*args, **kwargs)
        self._min_freq = min_freq
        self._max_freq = max_freq if max_freq is not None else min_freq

    @property
    def min_freq(self) -> int:
        """Get minimum frequency."""
        return getattr(self, '_min_freq', 1)

    @min_freq.setter
    def min_freq(self, value: int) -> None:
        """Set minimum frequency."""
        self._min_freq = value

    @property
    def max_freq(self) -> Optional[int]:
        """Get maximum frequency."""
        return getattr(self, '_max_freq', None)

    @max_freq.setter
    def max_freq(self, value: Optional[int]) -> None:
        """Set maximum frequency."""
        self._max_freq = value

    def is_skippable(self) -> bool:
        """
        Check if this node can be skipped (min_freq == 0).

        Returns:
            True if min_freq is 0, False otherwise
        """
        return self.min_freq == 0

    def is_repeatable(self) -> bool:
        """
        Check if this node can be repeated (max_freq > 1 or unbounded).

        Returns:
            True if max_freq > 1 or None, False otherwise
        """
        return self.max_freq is None or self.max_freq > 1

    def is_unbounded(self) -> bool:
        """
        Check if this node has unbounded repetition (max_freq is None).

        Returns:
            True if max_freq is None, False otherwise
        """
        return self.max_freq is None

    def freq_range(self) -> Tuple[int, Optional[int]]:
        """
        Get the frequency range as a tuple.

        Returns:
            Tuple of (min_freq, max_freq)
        """
        return (self.min_freq, self.max_freq)

    def set_freq_range(self, min_freq: int, max_freq: Optional[int] = None) -> None:
        """
        Set the frequency range.

        Args:
            min_freq: Minimum frequency
            max_freq: Maximum frequency (None for unbounded, defaults to min_freq)
        """
        self.min_freq = min_freq
        self.max_freq = max_freq if max_freq is not None else min_freq

    def __repr__(self) -> str:
        """Include frequency info in repr."""
        base_repr = super().__repr__()
        freq_info = f"[{self.min_freq}"
        if self.max_freq is not None and self.max_freq != self.min_freq:
            freq_info += f"-{self.max_freq}"
        elif self.max_freq is None:
            freq_info += "-*"
        freq_info += "]"
        return f"{base_repr}{freq_info}"


__all__ = [
    "FrequencyTagged",
]
