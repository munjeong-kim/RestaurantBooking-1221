from datetime import datetime

import pytest

from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler

NOT_ON_THE_HOUR = datetime.strptime('2026/07/02 09:03', '%Y/%m/%d %H:%M')
ON_THE_HOUR = datetime.strptime('2026/07/02 09:00', '%Y/%m/%d %H:%M')
TEST_CUSTOMER = Customer("tester", "1234-1234")

UNDER_CAPA = 2
TEST_CAPA = 3
OVER_CAPA = 4

@pytest.fixture
def booking_scheduler():
    return BookingScheduler(TEST_CAPA)

def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(booking_scheduler):

    schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)

    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_예약은_정시에만_가능하다_정시인_경우_예약가능(booking_scheduler):

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)

def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생():
    pass

def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공():
    pass

def test_예약완료시_SMS는_무조건_발송():
    pass

def test_이메일이_없는_경우에는_이메일_미발송():
    pass

def test_이메일이_있는_경우에는_이메일_발송():
    pass

def test_현재날짜가_일요일인_경우_예약불가_예외처리():
    pass

def test_현재날짜가_일요일이_아닌경우_예약가능():
    pass