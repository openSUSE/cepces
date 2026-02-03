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
# pylint: disable=arguments-differ
"""This module contains converters for common XML data types."""

from datetime import datetime, timedelta, tzinfo
from typing import Any, Protocol, TypeVar
import re
import textwrap

# Type variable for generic converter protocol
T = TypeVar("T", covariant=True)


class ConverterProtocol(Protocol[T]):
    """Protocol for converter classes.

    This protocol defines the interface that all converters must implement.
    It allows type checking without requiring inheritance, since converters
    have varying method signatures.

    The generic parameter T represents the Python type that this converter
    produces from XML string values.

    Example:
        class IntConverter(ConverterProtocol[int]):
            @staticmethod
            def from_string(value: str | None) -> int | None: ...
            @staticmethod
            def to_string(value: int | None) -> str | None: ...
    """

    @staticmethod
    def from_string(value: Any) -> T | None:
        """Parse a string and convert it to type T."""
        ...

    @staticmethod
    def to_string(value: Any) -> str | None:
        """Convert a value to a string."""
        ...


class Converter:
    """A base class for any value converter.

    It is responsible for converting an arbitrary input to and from a string
    for use within an XML document.
    """

    @staticmethod
    def from_string(value: Any, value_type: type = str) -> Any:
        """Parse a string and convert it to a suitable type or format.

        :param value: the string to parse, or None
        :param value_type: the desired type
        :raise TypeError: if the input is of an invalid type
        :return: the input as a suitable type or format, or None if value is
                 None
        """
        if value is None:
            return None
        elif not isinstance(value, value_type):
            raise TypeError(
                "Unsupported type (got '{}', expected '{}')".format(
                    type(value),
                    value_type,
                )
            )
        else:
            return value

    @staticmethod
    def to_string(value: Any, value_type: type = str) -> str | None:
        """Convert a value to an explicit string.

        :param value: the value to convert, or None
        :param value_type: the desired type
        :raise TypeError: if the input is of an invalid type
        :return: the input as a string, or None if value is None
        """
        if value is None:
            return None
        elif not isinstance(value, value_type):
            raise TypeError(
                "Unsupported type (got '{}', expected '{}')".format(
                    type(value),
                    value_type,
                )
            )
        else:
            return str(value)


# Make StringConverter as an alias to Converter, as it defaults to the string
# type.
StringConverter = Converter


class BooleanConverter:
    """Boolean Converter"""

    MAP = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
    }

    """Converts to and from booleans."""

    @staticmethod
    def from_string(value: str | None) -> bool | None:
        """Converts the input value to a boolean

        :param value: the value to convert, or None
        :raise TypeError: if the input is not a boolean
        :raise ValueError: if the input cannot be parsed as a boolean
        :return: the input as a boolean, or None if value is None
        """
        result = Converter.from_string(value)

        if not result:
            return result
        elif result not in BooleanConverter.MAP:
            raise ValueError('Unsupported value: "{}"'.format(result))
        else:
            return BooleanConverter.MAP[result]

    @staticmethod
    def to_string(value: bool | None) -> str | None:
        """Converts a boolean to a string

        :param value: the boolean to convert, or None
        :raise TypeError: if the input is not a boolean
        :raise ValueError: if the input cannot be parsed as a boolean
        :return: the input as a string, or None if value is None
        """
        if value is not None:
            result = Converter.to_string(value, bool)
            return result.lower() if result else None

        return None


class IntegerConverter:
    """Converts to and from integers."""

    @staticmethod
    def from_string(value: str | None) -> int | None:
        """Converts the input value to an integer

        :param value: the value to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer
        :return: the input as a string, or None if value is None
        """
        result = Converter.from_string(value)

        if not result:
            return result

        return int(result)

    @staticmethod
    def to_string(value: int | None) -> str | None:
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer
        :return: the input as a string, or None if value is None
        """
        return Converter.to_string(value, int)


class RangedIntegerConverter:
    """Converts to and from integers with a range constraint."""

    @staticmethod
    def range_check(value: int | None, lower: int, upper: int) -> int | None:
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
            raise TypeError("Unsupported type")
        elif int(value) < int(lower) or int(value) > int(upper):
            raise ValueError(
                "{0:d} outside allowed range ({1:d}, {2:d})".format(
                    value,
                    lower,
                    upper,
                )
            )

        return value

    @staticmethod
    def from_string(value: str | None, lower: int, upper: int) -> int | None:
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
    def to_string(value: int | None, lower: int, upper: int) -> str | None:
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
    def from_string(value: Any, value_type: type = str) -> int | None:
        """Converts the input value to an integer, checking that it is within
        the allowed range.

        :param value: the value to convert, or None
        :param value_type: ignored for compatibility with base class
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.from_string(value, -(2**31), 2**31 - 1)

    @staticmethod
    def to_string(value: Any, value_type: type = str) -> str | None:
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :param value_type: ignored for compatibility with base class
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.to_string(value, -(2**31), 2**31 - 1)


class UnsignedIntegerConverter(Converter):
    """Converts to and from signed (32-bit) integers.

    All values has to be within the allowed range 0 and 4,294,967,295.
    """

    @staticmethod
    def from_string(value: Any, value_type: type = str) -> int | None:
        """Converts the input value to an integer, checking that it is within
        the allowed range.

        :param value: the value to convert, or None
        :param value_type: ignored for compatibility with base class
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.from_string(value, 0, 2**32 - 1)

    @staticmethod
    def to_string(value: Any, value_type: type = str) -> str | None:
        """Converts the an integer to a string

        :param value: the integer to convert, or None
        :param value_type: ignored for compatibility with base class
        :raise TypeError: if the input is not an integer
        :raise ValueError: if the input cannot be parsed as an integer, or if
                           the input is outside the allowed range.
        :return: the input as a string, or None if value is None
        """
        return RangedIntegerConverter.to_string(value, 0, 2**32 - 1)


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

        def __init__(self, offset: int, name: str | None = None) -> None:
            self._offset = timedelta(minutes=offset)
            self._name = name

        def utcoffset(self, _dt: datetime | None) -> timedelta:
            return self._offset

        def tzname(self, _dt: datetime | None) -> str | None:
            return self._name

        def dst(self, _dt: datetime | None) -> timedelta:
            return timedelta(0)

    @staticmethod
    def from_string(value: Any, value_type: type = str) -> datetime | None:
        """Parse a datetime string and convert it to a datetime object.

        :param value: the datetime string to parse
        :param value_type: ignored for compatibility with base class
        :return: datetime object, or None if value is None
        """
        match = re.search(
            r"^"
            r"(?P<year>\d{4})-"
            r"(?P<month>\d{2})-"
            r"(?P<day>\d{2})"
            r"T"
            r"(?P<hour>\d{2}):"
            r"(?P<minute>\d{2}):"
            r"(?P<second>\d{2})"
            r"(?P<tz>Z|"
            r"(?P<tz_sign>[+-])"
            r"(?P<tz_hour>\d{2}):"
            r"(?P<tz_minute>\d{2}))"
            r"$",
            value,
        )

        if match is None:
            raise ValueError(f"Invalid datetime format: {value}")

        if match.group("tz") == "Z":
            timezone = DateTimeConverter.FixedOffset(0, "UTC")
        else:
            tz_hour = int(match.group("tz_hour"))
            tz_minute = int(match.group("tz_minute"))
            tz_sign = match.group("tz_sign")
            offset = 60 * tz_hour + tz_minute

            timezone = DateTimeConverter.FixedOffset(
                int(
                    "{0:s}{1:d}".format(
                        tz_sign,
                        offset,
                    )
                ),
                "UTC",
            )

        return datetime(
            year=int(match.group("year")),
            month=int(match.group("month")),
            day=int(match.group("day")),
            hour=int(match.group("hour")),
            minute=int(match.group("minute")),
            second=int(match.group("second")),
            tzinfo=timezone,
        )

    @staticmethod
    def to_string(
        value: datetime | None, value_type: type = str
    ) -> str | None:
        """Convert a datetime object to a string.

        :param value: the datetime object to convert
        :param value_type: ignored for compatibility with base class
        :return: datetime string, or None if value is None
        """
        # Allow None value.
        if value is None:
            return value

        # Check the value type.
        if not isinstance(value, datetime):
            raise TypeError(
                "{0:s} expected, got {1:s}".format(
                    datetime.__class__,
                    type(value).__class__,
                ),
            )

        # If no timezone is set, default to 'Z'.
        if value.tzinfo is None:
            timezone = "Z"
        else:
            utc_offset = value.utcoffset()
            if utc_offset is None:
                timezone = "Z"
            else:
                offset = int(utc_offset.total_seconds() / 60)
                timezone = "{0:0=+3d}:{1:0=2d}".format(
                    offset // 60,
                    abs(offset % 60),
                )

        result = "{0:0=2d}-{1:0=2d}-{2:0=2d}T{3:0=2d}:{4:0=2d}:{5:0=2d}{6:s}"

        return result.format(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            timezone,
        )


class CertificateConverter:
    """Converts to and from PEM certificates."""

    @staticmethod
    def from_string(value: str | None) -> str | None:
        """Converts the input value to a proper PEM certificate

        :param value: the value to convert, or None
        :return: the input as a string, or None if value is None
        """
        text = Converter.from_string(value)
        if text is None:
            return None

        template = "{}\n{}\n{}"

        return template.format(
            "-----BEGIN CERTIFICATE-----",
            textwrap.fill(text, 64),
            "-----END CERTIFICATE-----",
        )

    @staticmethod
    def to_string(value: str) -> str:
        """Converts the certificate to a plain string

        :param value: the certificate to convert, or None
        :return: the input as a string, or None if value is None
        """
        match = re.search(
            "-----BEGIN CERTIFICATE-----"
            "((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)"
            "-----END CERTIFICATE-----",
            "".join(value.splitlines()),
        )

        if match is None:
            raise ValueError(f"Invalid certificate format: {value}")

        result = Converter.to_string(match.group(1), str)
        # match.group(1) is a valid string, so result is never None here
        assert result is not None
        return result
