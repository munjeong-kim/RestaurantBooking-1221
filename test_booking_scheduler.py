from datetime import datetime, timedelta

import pytest

from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler
from testSender import TestSmsSender, TestEmailSender

NOT_ON_THE_HOUR = datetime.strptime('2026/07/02 09:03', '%Y/%m/%d %H:%M')
ON_THE_HOUR = datetime.strptime('2026/07/02 09:00', '%Y/%m/%d %H:%M')
TEST_CUSTOMER = Customer("tester", "1234-1234")
TEST_CUSTOMER_WITH_EMAIL = Customer("tester", "1234-1234", "email@gmail.com")


UNDER_CAPA = 2
TEST_CAPA = 3
OVER_CAPA = 4

class TestableBookingScheduler(BookingScheduler):
    def __init__(self, date_time):
        super().__init__(TEST_CAPA)
        self.date_time = date_time

    def get_now(self):
        return datetime.strptime(self.date_time, "%Y/%m/%d %H:%M")

@pytest.fixture
def booking_scheduler():
    return BookingScheduler(TEST_CAPA)

@pytest.fixture
def booking_scheduler_with_sms_mock():
    scheduler = BookingScheduler(TEST_CAPA)
    sms_sender = TestSmsSender()
    scheduler.set_sms_sender(sms_sender)
    return scheduler, sms_sender

@pytest.fixture
def booking_scheduler_with_email_mock():
    scheduler = BookingScheduler(TEST_CAPA)
    email_sender = TestEmailSender()
    scheduler.set_mail_sender(email_sender)
    return scheduler, email_sender

def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(booking_scheduler):

    schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)

    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_예약은_정시에만_가능하다_정시인_경우_예약가능(booking_scheduler):

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)

def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(booking_scheduler):
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    with pytest.raises(ValueError, match="Number of people is over restaurant capacity per hour"):
        booking_scheduler.add_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(booking_scheduler):
    schedule = Schedule(ON_THE_HOUR, TEST_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    other_schedule = Schedule(ON_THE_HOUR + timedelta(hours=1), UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(other_schedule)

    assert booking_scheduler.has_schedule(schedule)
    assert booking_scheduler.has_schedule(other_schedule)

def test_예약완료시_SMS는_무조건_발송(booking_scheduler_with_sms_mock):
    booking_scheduler, test_sms_sender = booking_scheduler_with_sms_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    assert test_sms_sender.called

def test_이메일이_없는_경우에는_이메일_미발송(booking_scheduler_with_email_mock):
    booking_scheduler, test_email_sender = booking_scheduler_with_email_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    assert not test_email_sender.called

def test_이메일이_있는_경우에는_이메일_발송(booking_scheduler_with_email_mock):
    booking_scheduler, test_email_sender = booking_scheduler_with_email_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER_WITH_EMAIL)
    booking_scheduler.add_schedule(schedule)

    assert test_email_sender.called

def test_현재날짜가_일요일인_경우_예약불가_예외처리():
    booking_scheduler = TestableBookingScheduler("2026/07/05 09:00")

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER_WITH_EMAIL)

    with pytest.raises(ValueError, match="Booking system is not available on Sunday"):
        booking_scheduler.add_schedule(schedule)

def test_현재날짜가_일요일이_아닌경우_예약가능():
    booking_scheduler = TestableBookingScheduler("2026/07/06 09:00")

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, TEST_CUSTOMER_WITH_EMAIL)

    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)