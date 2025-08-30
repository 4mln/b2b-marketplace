"""
Jalali Calendar Utilities
Persian (Shamsi) calendar conversion and formatting
"""
from datetime import datetime, date
from typing import Tuple, Optional
import re


class JalaliCalendar:
    """Jalali (Persian) calendar implementation"""
    
    # Jalali month names in Persian
    MONTHS_FA = [
        "فروردین", "اردیبهشت", "خرداد",
        "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر",
        "دی", "بهمن", "اسفند"
    ]
    
    # Jalali month names in English
    MONTHS_EN = [
        "Farvardin", "Ordibehesht", "Khordad",
        "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar",
        "Dey", "Bahman", "Esfand"
    ]
    
    # Weekday names in Persian
    WEEKDAYS_FA = [
        "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه",
        "چهارشنبه", "پنج‌شنبه", "جمعه"
    ]
    
    # Weekday names in English
    WEEKDAYS_EN = [
        "Saturday", "Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday"
    ]
    
    @staticmethod
    def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
        """
        Convert Gregorian date to Jalali date
        
        Args:
            gy: Gregorian year
            gm: Gregorian month (1-12)
            gd: Gregorian day (1-31)
            
        Returns:
            Tuple of (jalali_year, jalali_month, jalali_day)
        """
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        
        if gm > 2:
            gy2 = gy + 1
        else:
            gy2 = gy
            
        days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
        
        jy = -1595 + (33 * (days // 12053))
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461
        
        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365
            
        if days < 186:
            jm = 1 + (days // 31)
            jd = 1 + (days % 31)
        else:
            jm = 7 + ((days - 186) // 30)
            jd = 1 + ((days - 186) % 30)
            
        return jy, jm, jd
    
    @staticmethod
    def jalali_to_gregorian(jy: int, jm: int, jd: int) -> Tuple[int, int, int]:
        """
        Convert Jalali date to Gregorian date
        
        Args:
            jy: Jalali year
            jm: Jalali month (1-12)
            jd: Jalali day (1-31)
            
        Returns:
            Tuple of (gregorian_year, gregorian_month, gregorian_day)
        """
        jy += 1595
        days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
        
        if jm < 7:
            days += (jm - 1) * 31
        else:
            days += ((jm - 7) * 30) + 186
            
        gy = 400 * (days // 146097)
        days %= 146097
        
        if days > 36524:
            days -= 1
            gy += 100 * (days // 36524)
            days %= 36524
            
            if days >= 365:
                days += 1
                
        gy += 4 * (days // 1461)
        days %= 1461
        
        if days > 365:
            gy += (days - 1) // 365
            days = (days - 1) % 365
            
        gd = days + 1
        
        if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
            leap = 1
        else:
            leap = 0
            
        if leap == 1 and gd > 2:
            gd += 1
            
        sal_a = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        sal_b = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        if leap == 1:
            gm = 0
            while gm < 13 and gd > sal_a[gm]:
                gd -= sal_a[gm]
                gm += 1
        else:
            gm = 0
            while gm < 13 and gd > sal_b[gm]:
                gd -= sal_b[gm]
                gm += 1
                
        return gy, gm, gd
    
    @staticmethod
    def datetime_to_jalali(dt: datetime) -> Tuple[int, int, int]:
        """Convert datetime object to Jalali date"""
        return JalaliCalendar.gregorian_to_jalali(dt.year, dt.month, dt.day)
    
    @staticmethod
    def jalali_to_datetime(jy: int, jm: int, jd: int) -> datetime:
        """Convert Jalali date to datetime object"""
        gy, gm, gd = JalaliCalendar.jalali_to_gregorian(jy, jm, jd)
        return datetime(gy, gm, gd)
    
    @staticmethod
    def format_jalali_date(jy: int, jm: int, jd: int, language: str = "fa", 
                          format_type: str = "full") -> str:
        """
        Format Jalali date as string
        
        Args:
            jy: Jalali year
            jm: Jalali month (1-12)
            jd: Jalali day (1-31)
            language: Language code ('fa' or 'en')
            format_type: Format type ('full', 'short', 'numeric')
            
        Returns:
            Formatted date string
        """
        if language == "fa":
            months = JalaliCalendar.MONTHS_FA
            weekdays = JalaliCalendar.WEEKDAYS_FA
        else:
            months = JalaliCalendar.MONTHS_EN
            weekdays = JalaliCalendar.WEEKDAYS_EN
            
        if format_type == "full":
            # Get weekday
            dt = JalaliCalendar.jalali_to_datetime(jy, jm, jd)
            weekday = dt.weekday()
            weekday_name = weekdays[(weekday + 1) % 7]  # Adjust for Jalali week start
            
            if language == "fa":
                return f"{weekday_name} {jd} {months[jm-1]} {jy}"
            else:
                return f"{weekday_name}, {jd} {months[jm-1]} {jy}"
                
        elif format_type == "short":
            if language == "fa":
                return f"{jd} {months[jm-1]} {jy}"
            else:
                return f"{jd} {months[jm-1]} {jy}"
                
        elif format_type == "numeric":
            if language == "fa":
                return f"{jy}/{jm:02d}/{jd:02d}"
            else:
                return f"{jy}/{jm:02d}/{jd:02d}"
                
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    @staticmethod
    def format_datetime(dt: datetime, language: str = "fa", 
                       format_type: str = "full") -> str:
        """
        Format datetime object to Jalali date string
        
        Args:
            dt: datetime object
            language: Language code ('fa' or 'en')
            format_type: Format type ('full', 'short', 'numeric')
            
        Returns:
            Formatted date string
        """
        jy, jm, jd = JalaliCalendar.datetime_to_jalali(dt)
        return JalaliCalendar.format_jalali_date(jy, jm, jd, language, format_type)
    
    @staticmethod
    def parse_jalali_date(date_string: str, language: str = "fa") -> Optional[Tuple[int, int, int]]:
        """
        Parse Jalali date string
        
        Args:
            date_string: Date string to parse
            language: Language code ('fa' or 'en')
            
        Returns:
            Tuple of (year, month, day) or None if parsing fails
        """
        try:
            if language == "fa":
                # Try numeric format: YYYY/MM/DD
                match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_string)
                if match:
                    return int(match.group(1)), int(match.group(2)), int(match.group(3))
                    
                # Try text format: DD Month YYYY
                for i, month in enumerate(JalaliCalendar.MONTHS_FA, 1):
                    pattern = rf'(\d{{1,2}})\s*{month}\s*(\d{{4}})'
                    match = re.match(pattern, date_string)
                    if match:
                        return int(match.group(2)), i, int(match.group(1))
            else:
                # Try numeric format: YYYY/MM/DD
                match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_string)
                if match:
                    return int(match.group(1)), int(match.group(2)), int(match.group(3))
                    
                # Try text format: DD Month YYYY
                for i, month in enumerate(JalaliCalendar.MONTHS_EN, 1):
                    pattern = rf'(\d{{1,2}})\s*{month}\s*(\d{{4}})'
                    match = re.match(pattern, date_string)
                    if match:
                        return int(match.group(2)), i, int(match.group(1))
                        
        except (ValueError, AttributeError):
            pass
            
        return None
    
    @staticmethod
    def is_valid_jalali_date(jy: int, jm: int, jd: int) -> bool:
        """
        Check if Jalali date is valid
        
        Args:
            jy: Jalali year
            jm: Jalali month (1-12)
            jd: Jalali day (1-31)
            
        Returns:
            True if valid, False otherwise
        """
        if jy < 1 or jm < 1 or jm > 12 or jd < 1:
            return False
            
        # Check leap year
        leap = 0
        if jy % 33 == 1 or jy % 33 == 5 or jy % 33 == 9 or jy % 33 == 13 or jy % 33 == 17 or jy % 33 == 22 or jy % 33 == 26 or jy % 33 == 30:
            leap = 1
            
        # Days in month
        if jm <= 6:
            days_in_month = 31
        elif jm <= 11:
            days_in_month = 30
        else:  # Esfand
            days_in_month = 29 + leap
            
        return jd <= days_in_month
    
    @staticmethod
    def get_jalali_weekday(dt: datetime) -> int:
        """
        Get Jalali weekday (0=Saturday, 1=Sunday, ..., 6=Friday)
        
        Args:
            dt: datetime object
            
        Returns:
            Jalali weekday (0-6)
        """
        weekday = dt.weekday()
        return (weekday + 1) % 7  # Adjust for Jalali week start
    
    @staticmethod
    def get_jalali_weekday_name(dt: datetime, language: str = "fa") -> str:
        """
        Get Jalali weekday name
        
        Args:
            dt: datetime object
            language: Language code ('fa' or 'en')
            
        Returns:
            Weekday name
        """
        weekday = JalaliCalendar.get_jalali_weekday(dt)
        if language == "fa":
            return JalaliCalendar.WEEKDAYS_FA[weekday]
        else:
            return JalaliCalendar.WEEKDAYS_EN[weekday]


# Utility functions for easy access
def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
    """Convert Gregorian date to Jalali date"""
    return JalaliCalendar.gregorian_to_jalali(gy, gm, gd)


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> Tuple[int, int, int]:
    """Convert Jalali date to Gregorian date"""
    return JalaliCalendar.jalali_to_gregorian(jy, jm, jd)


def format_jalali_date(jy: int, jm: int, jd: int, language: str = "fa", 
                      format_type: str = "full") -> str:
    """Format Jalali date as string"""
    return JalaliCalendar.format_jalali_date(jy, jm, jd, language, format_type)


def format_datetime(dt: datetime, language: str = "fa", format_type: str = "full") -> str:
    """Format datetime object to Jalali date string"""
    return JalaliCalendar.format_datetime(dt, language, format_type)


def parse_jalali_date(date_string: str, language: str = "fa") -> Optional[Tuple[int, int, int]]:
    """Parse Jalali date string"""
    return JalaliCalendar.parse_jalali_date(date_string, language)


def is_valid_jalali_date(jy: int, jm: int, jd: int) -> bool:
    """Check if Jalali date is valid"""
    return JalaliCalendar.is_valid_jalali_date(jy, jm, jd)
