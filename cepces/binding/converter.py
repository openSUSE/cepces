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
from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
import re


class Converter(metaclass=ABCMeta):
    """A base class for any value converter. It is responsible for converting
    an arbitrary input to and from string."""
    @staticmethod
    @abstractmethod
    def from_string(value):
        pass

    @staticmethod
    @abstractmethod
    def to_string(value):
        pass


class StringConverter(Converter):
    @staticmethod
    def from_string(value):
        if value is None:
            return value
        elif not isinstance(value, str):
            raise TypeError('Unsupported type.')
        else:
            return value

    @staticmethod
    def to_string(value):
        if value is None:
            return None
        else:
            return str(value)


class IntegerConverter(Converter):
    @staticmethod
    def from_string(value):
        if value is None:
            return value
        elif not isinstance(value, str):
            raise TypeError('Unsupported type.')
        else:
            return int(value)

    @staticmethod
    def to_string(value):
        if value is None:
            return None
        elif not isinstance(value, int):
            raise TypeError('Unsupported type.')
        else:
            return str(value)


class RangedIntegerConverter(Converter):
    @staticmethod
    def range_check(value, lower, upper):
        if value is None:
            return None
        elif not isinstance(value, int):
            raise TypeError('Unsupported type.')
        elif value < lower or value > upper:
            raise ValueError('{0:d} outside ({1:d}, {2:d})'.format(value,
                                                                   lower,
                                                                   upper))

        return value

    @staticmethod
    def from_string(value, lower, upper):
        value = IntegerConverter.from_string(value)

        return RangedIntegerConverter.range_check(value, lower, upper)

    @staticmethod
    def to_string(value, lower, upper):
        value = RangedIntegerConverter.range_check(value, lower, upper)

        return IntegerConverter.to_string(value)


class SignedIntegerConverter(Converter):
    @staticmethod
    def from_string(value):
        return RangedIntegerConverter.from_string(value, -2 ** 31, 2 ** 31 - 1)

    @staticmethod
    def to_string(value):
        return RangedIntegerConverter.to_string(value, -2 ** 31, 2 ** 31 - 1)


class UnsignedIntegerConverter(Converter):
    @staticmethod
    def from_string(value):
        return RangedIntegerConverter.from_string(value, 0, 2 ** 32 - 1)

    @staticmethod
    def to_string(value):
        return RangedIntegerConverter.to_string(value, 0, 2 ** 32 - 1)


class DateTimeConverter(Converter):
    '''Converts the date time datatype.

    This datatype describes instances identified by the combination of a date
    and a time. Its value space is described as a combination of date and time
    of day in Chapter 5.4 of ISO 8601. Its lexical space is the extended
    format:

      [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]

    The time zone may be specified as Z (UTC) or (+|-)hh:mm. Time zones that
    aren't specified are considered undetermined.

    Python has a built in limitation preventing years before 1900 from being
    used. Therefore, the initial [-] is meaningless.
    '''

    class FixedOffset(tzinfo):
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
        match = re.search('^(?P<year>\d{4})-'
                          '(?P<month>\d{2})-'
                          '(?P<day>\d{2})'
                          'T(?P<hour>\d{2}):'
                          '(?P<minute>\d{2}):'
                          '(?P<second>\d{2})'
                          '(?P<tz>Z|'
                          '(?P<tz_sign>[+-])'
                          '(?P<tz_hour>\d{2}):'
                          '(?P<tz_minute>\d{2}))$',
                          value)

        if match.group('tz') is 'Z':
            tz = DateTimeConverter.FixedOffset(0, 'UTC')
        else:
            tz_hour = int(match.group('tz_hour'))
            tz_minute = int(match.group('tz_minute'))
            tz_sign = match.group('tz_sign')
            offset = 60 * tz_hour + tz_minute
            tz = DateTimeConverter.FixedOffset(
                int('{0:s}{1:d}'.format(tz_sign, offset)),
                'UTC')

        return datetime(year=int(match.group('year')),
                        month=int(match.group('month')),
                        day=int(match.group('day')),
                        hour=int(match.group('hour')),
                        minute=int(match.group('minute')),
                        second=int(match.group('second')),
                        tzinfo=tz)

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
                    tz)
