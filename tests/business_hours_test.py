import random
import unittest
from datetime import datetime, timedelta, timezone

from pm4py.util.business_hours import (
    BusinessHours,
    soj_time_business_hours_diff,
)
from pm4py.util.constants import DEFAULT_BUSINESS_HOUR_SLOTS


class BusinessHoursTest(unittest.TestCase):
    def test_default_schedule_across_multiple_weeks(self):
        start = datetime(2024, 1, 1, 8, 30)
        end = datetime(2024, 1, 16, 10, 0)

        self.assertEqual(
            111 * 60 * 60 + 30 * 60,
            soj_time_business_hours_diff(
                start, end, DEFAULT_BUSINESS_HOUR_SLOTS
            ),
        )

    def test_overlapping_slots_are_counted_once(self):
        slots = [
            (9 * 60 * 60, 12 * 60 * 60),
            (10 * 60 * 60, 14 * 60 * 60),
        ]
        start = datetime(2024, 1, 1, 8, 0)
        end = datetime(2024, 1, 1, 15, 0)

        business_hours = BusinessHours(
            start, end, business_hour_slots=slots
        )

        self.assertEqual(5 * 60 * 60, business_hours.get_seconds())
        self.assertEqual(
            [[9 * 60 * 60, 14 * 60 * 60]],
            business_hours.business_hour_slots_unified,
        )

    def test_timezone_is_ignored_consistently(self):
        start = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
        end = datetime(
            2024, 1, 1, 10, 0, tzinfo=timezone(timedelta(hours=2))
        )

        self.assertEqual(
            2 * 60 * 60,
            soj_time_business_hours_diff(
                start, end, DEFAULT_BUSINESS_HOUR_SLOTS
            ),
        )

    def test_schedule_mutation_is_visible_to_later_calls(self):
        slots = [(8 * 60 * 60, 9 * 60 * 60)]
        start = datetime(2024, 1, 1, 8, 0)
        end = datetime(2024, 1, 1, 10, 0)

        self.assertEqual(
            60 * 60, soj_time_business_hours_diff(start, end, slots)
        )
        slots[0] = (8 * 60 * 60, 10 * 60 * 60)
        self.assertEqual(
            2 * 60 * 60, soj_time_business_hours_diff(start, end, slots)
        )

    def test_matches_interval_based_reference(self):
        random_generator = random.Random(1988)
        epoch = datetime(2024, 1, 1)
        slots = [
            (7 * 60 * 60, 12 * 60 * 60),
            (11 * 60 * 60, 17 * 60 * 60),
            (
                2 * 24 * 60 * 60 + 9 * 60 * 60,
                2 * 24 * 60 * 60 + 18 * 60 * 60,
            ),
            (
                4 * 24 * 60 * 60 + 8 * 60 * 60,
                4 * 24 * 60 * 60 + 16 * 60 * 60,
            ),
        ]

        for _ in range(100):
            start = epoch + timedelta(
                seconds=random_generator.randrange(35 * 24 * 60 * 60)
            )
            end = start + timedelta(
                seconds=random_generator.randrange(21 * 24 * 60 * 60)
            )
            self.assertEqual(
                self._reference_seconds(start, end, slots),
                soj_time_business_hours_diff(start, end, slots),
            )

    @staticmethod
    def _reference_seconds(start, end, slots):
        unified = []
        for begin, finish in sorted(slots):
            if unified and unified[-1][1] >= begin - 1:
                unified[-1][1] = max(unified[-1][1], finish)
            else:
                unified.append([begin, finish])

        week_start = start - timedelta(
            days=start.weekday(),
            hours=start.hour,
            minutes=start.minute,
            seconds=start.second,
            microseconds=start.microsecond,
        )
        total = 0.0
        while week_start < end:
            for begin, finish in unified:
                slot_start = week_start + timedelta(seconds=begin)
                slot_end = week_start + timedelta(seconds=finish)
                total += max(
                    0.0,
                    (
                        min(end, slot_end) - max(start, slot_start)
                    ).total_seconds(),
                )
            week_start += timedelta(days=7)
        return total


if __name__ == "__main__":
    unittest.main()
