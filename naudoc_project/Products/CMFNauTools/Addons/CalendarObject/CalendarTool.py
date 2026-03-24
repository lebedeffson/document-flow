# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/CalendarObject/CalendarTool.py
# Compiled at: 2005-04-07 14:35:57
"""
    Helper tool to calculate dates
YYYY-MM-DD
"""
from DateTime import DateTime
months = [
 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
month_len = ((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))
days = {'Sunday': 7, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}

def firstDayOfMonth(self, year, month):
    """
        Return the full name of the first day of the <month> <year>
    """
    str_date = '%s/%s/%s' % (year, month, 1)
    return DateTime(str_date).Day()
    return


def lastDayOfMonth(self, year, month):
    """
        Return the full name of the last day of the <month> <year>
    """
    last_month_day = self.monthLength(year, month)
    str_date = '%s/%s/%s' % (year, month, last_month_day)
    return DateTime(str_date).Day()
    return


def getShortWeekInfo(self, y, m, w):
    """
            return week info for <w> week of <m> month <y> year
            return info about <m> month only! not get info about 'near' month
                   (if <w> week is include 2 months, exmp 28.02.05 - 6.03.05 : return 28.02.05 only) 
            Arguments:
                    y    -   year (int)
                    m    -   month (int)
                    w    -   number of the week of the month
            return list of DateTime objects:
    """
    info = []
    first_day_of_week = self.firstDayNumberOfWeek(y, m, w)
    m_len = self.monthLength(y, m)
    for day in range(first_day_of_week, first_day_of_week + 7):
        if day > 0 and day <= m_len:
            info.append(DateTime('%s/%s/%s' % (y, m, day)))

    return info
    return


def getWeekInfo(self, year, month, week):
    """
            return week info for <w> week of <m> month <y> year with previos or next month dates
            if <w> week is include 2 months, exmp 28.02.05 - 6.03.05 : return 28.02.05 - 6.03.05) 
            Arguments:
                    y    -   year (int)
                    m    -   month (int)
                    w    -   number of the week of the month
            return list of DateTime objects:
    """
    info = []
    first_day_of_week = self.firstDayNumberOfWeek(year, month, week)
    if first_day_of_week < 1:
        first_day_of_week = 1
    str_date = '%s/%s/%s' % (year, month, first_day_of_week)
    fd_date = DateTime(str_date)
    fd_date_dow = fd_date.dow()
    if fd_date_dow == 0:
        fd_date_dow = 7
    begin_date = fd_date - fd_date_dow + 1
    for d in range(7):
        info.append(begin_date + d)

    return info
    return


def getMonthInfo(self, year, month):
    """
        return last previos month Monday date (if first day of <month> is not Monday): date_1
               and first next month Sunday date (if last day of <month> is not Sunday): date_2

        return as list:
            [ date_1, date_2]
    """
    str_date = '%s/%s/%s' % (year, month, 1)
    first_day_of_month = DateTime(str_date)
    str_date = '%s/%s/%s' % (year, month, self.monthLength(year, month))
    last_day_of_month = DateTime(str_date)
    fd_date_dow = first_day_of_month.dow()
    if fd_date_dow == 0:
        fd_date_dow = 7
    begin_date = first_day_of_month - fd_date_dow + 1
    ld_date_dow = last_day_of_month.dow()
    if ld_date_dow == 0:
        ld_date_dow = 7
    end_date = last_day_of_month + (7 - ld_date_dow)
    return (
     begin_date, end_date)
    return


def firstDayNumberOfWeek(self, year, month, week):
    """
        return day number with week begin. if week begin with previos month
               then return -(minus) count of days previos month - 1
        exmp:
            if 1st week of 2nd month begin with 30.01, 31.01 
            then return -1
    """
    first_day_of_month = days[self.firstDayOfMonth(year, month)]
    first_day_of_week = (week - 1) * 7 + 1 - (first_day_of_month - 1)
    return first_day_of_week
    return


def isYearLeap(self, year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    return


def monthLength(self, year, month):
    return month_len[self.isYearLeap(year)][month]
    return
