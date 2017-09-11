# -*- coding: utf-8 -*-
#
# This file is part of cepces.
#
# cepces is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cepces is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cepces.  If not, see <http://www.gnu.org/licenses/>.
#
"""This module contains converters for common XML data types."""

from datetime import datetime, timedelta, tzinfo
import re


class Converter(object):
    """A base class for any value converter.

    It is responsible for converting an arbitrary input to and from a string
    for use within an XML document.
    """
    @staticmethod
    def from_string(value, t=str):
        """Parse a string and convert it to a suitable type or format.

        :param value: the string to parse, or None
        :param t: the desired type
        :raise TypeError: if the input is of an invalid type
        :return: the input as a suitable type or format, or None if value is
                 None
        """
        if value is None:
            return None
        elif not isinstance(value, t):
            raise TypeError(
                "Unsupported type (got '{}', expected '{}')".format(
                    type(value),
                    t,
                )
            )
        else:
            return value

    @staticmethod
    def to_string(value, t=str):
        """Convert a value to an explicit string.

        :param value: the value to convert, or None
        :param t: the desired type
        :raise TypeError: if the input is of an invalid type
        :return: the input as a string, or None if value is None
        """
        if value is None:
            return None
        elif not isinstance(value, t):
            raise TypeError(
                "Unsupported type (got '{}', expected '{}')".format(
                    type(value),
                    t,
                )
            )
        else:
            return str(value)


# Make StringConverter as an alias to Converter, as it defaults to the string
# type.
StringConverter = Converter


class IntegerConverter(object):
    """Converts to and from integers."""
    @staticmethod
    def from_string(value):
        """Converts the input value to an integer

        :param value: the value to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer
        :return: the input as a string, or None if value is None
        """
        result = Converter.from_string(value)

        if not result:
            return result
        else:
            return int(result)

    @staticmethod
    def to_string(value):
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer
        :return: the input as a string, or None if value is None
        """
        return Converter.to_string(value, int)


class RangedIntegerConverter(object):
    """Converts to and from integers with a range constraint."""

    @staticmethod
    def range_check(value, lower, upper):
        """Check that the given value is within the inclusive range.

        :param value: the integer to check
        :param lower: the lower (inclusive) bound
        :param upper: the upper (inclusive) bound
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        """
        if value is None:
            return None
        elif not isinstance(value, int):
            raise TypeError('Unsupported type')
        elif int(value) < int(lower) or int(value) > int(upper):
            raise ValueError(
                '{0:d} outside allowed range ({1:d}, {2:d})'.format(
                    value,
                    lower,
                    upper,
                )
            )

        return value

    @staticmethod
    def from_string(value, lower, upper):
        """Converts the input value to an integer within the allowed range.

        :param value: the integer to check
        :param lower: the lower (inclusive) bound
        :param upper: the upper (inclusive) bound
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input, if within the allowed range
        """
        result = IntegerConverter.from_string(value)

        return RangedIntegerConverter.range_check(result, lower, upper)

    @staticmethod
    def to_string(value, lower, upper):
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :param lower: the lower (inclusive) bound
        :param upper: the upper (inclusive) bound
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        result = RangedIntegerConverter.range_check(value, lower, upper)

        return IntegerConverter.to_string(result)


class SignedIntegerConverter(Converter):
    """Converts to and from signed (32-bit) integers.

    All values has to be within the allowed range -2,147,483,648 and
    2,147,483,647.
    """

    @staticmethod
    def from_string(value):
        """Converts the input value to an integer, checking that it is within
        the allowed range.

        :param value: the value to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.from_string(value, -2 ** 31, 2 ** 31 - 1)

    @staticmethod
    def to_string(value):
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.to_string(value, -2 ** 31, 2 ** 31 - 1)


class UnsignedIntegerConverter(Converter):
    """Converts to and from signed (32-bit) integers.

    All values has to be within the allowed range 0 and 4,294,967,295.
    """

    @staticmethod
    def from_string(value):
        """Converts the input value to an integer, checking that it is within
        the allowed range.

        :param value: the value to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.from_string(value, 0, 2 ** 32 - 1)

    @staticmethod
    def to_string(value):
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.to_string(value, 0, 2 ** 32 - 1)


class DateTimeConverter(Converter):
    """Converts the date time datatype.

    This datatype describes instances identified by the combination of a date
    and a time. Its value space is described as a combination of date and time
    of day in Chapter 5.4 of ISO 8601. Its lexical space is the extended
    format:

      [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]

    The time zone may be specified as Z (UTC) or (+|-)hh:mm. Time zones that
    aren't specified are considered undetermined.

    Python has a built in limitation preventing years before 1900 from being
    used. Therefore, the initial [-] is meaningless.
    """
    class FixedOffset(tzinfo):
        """Internal class representing a fixed Time Zone."""
        def __init__(self, offset, name=None):
            self._offset = timedelta(minutes=offset)
            self._name = name

        def utcoffset(self, _dt):
            return self._offset

        def tzname(self, _dt):
            return self._name

        def dst(self, _dt):
            return timedelta(0)

    @staticmethod
    def from_string(value):
        match = re.search(
            '^'
            '(?P<year>\d{4})-'
            '(?P<month>\d{2})-'
            '(?P<day>\d{2})'
            'T'
            '(?P<hour>\d{2}):'
            '(?P<minute>\d{2}):'
            '(?P<second>\d{2})'
            '(?P<tz>Z|'
            '(?P<tz_sign>[+-])'
            '(?P<tz_hour>\d{2}):'
            '(?P<tz_minute>\d{2}))'
            '$',
            value,
        )

        if match.group('tz') is 'Z':
            tz = DateTimeConverter.FixedOffset(0, 'UTC')
        else:
            tz_hour = int(match.group('tz_hour'))
            tz_minute = int(match.group('tz_minute'))
            tz_sign = match.group('tz_sign')
            offset = 60 * tz_hour + tz_minute

            tz = DateTimeConverter.FixedOffset(
                int(
                    '{0:s}{1:d}'.format(
                        tz_sign,
                        offset,
                    )
                ),
                'UTC',
            )

        return datetime(
            year=int(match.group('year')),
            month=int(match.group('month')),
            day=int(match.group('day')),
            hour=int(match.group('hour')),
            minute=int(match.group('minute')),
            second=int(match.group('second')),
            tzinfo=tz,
        )

    @staticmethod
    def to_string(value):
        # Allow None value.
        if value is None:
            return value

        # Check the value type.
        if type(value) is not datetime:
            raise TypeError('{0:s} expected, got {1:s}'.format(
                            datetime.__class__,
                            type(value).__class__))

        # If no timezone is set, default to 'Z'.
        if value.tzinfo is None:
            tz = 'Z'
        else:
            offset = int(value.utcoffset().total_seconds() / 60)
            tz = '{0:0=+3d}:{1:0=2d}'.format(offset / 60,
                                             abs(offset % 60))

        return '{0:0=2d}-{1:0=2d}-{2:0=2d}' \
               'T{3:0=2d}:{4:0=2d}:{5:0=2d}{6:s}'.format(
                    value.year,
                    value.month,
                    value.day,
                    value.hour,
                    value.minute,
                    value.second,
                    tz,
                )
