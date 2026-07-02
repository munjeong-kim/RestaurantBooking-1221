from datetime import datetime, timedelta

import pytest
from pytest_mock import mocker

from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler

NOT_ON_THE_HOUR = datetime.strptime('2026/07/02 09:03', '%Y/%m/%d %H:%M')
ON_THE_HOUR = datetime.strptime('2026/07/02 09:00', '%Y/%m/%d %H:%M')

UNDER_CAPA = 2
TEST_CAPA = 3

@pytest.fixture
def customer(mocker):
    mock = mocker.Mock(spec=Customer)
    mock.phone_number = '+1555555555'
    mock.get_email.return_value = None

    return mock

@pytest.fixture
def customer_with_email(mocker):
    mock = mocker.Mock(spec=Customer)
    mock.phone_number = '+1555555555'
    mock.get_email.return_value = "email@gmail.com"

    return mock

@pytest.fixture
def booking_scheduler():
    return BookingScheduler(TEST_CAPA)

@pytest.fixture
def booking_scheduler_with_sms_mock(mocker):
    scheduler = BookingScheduler(TEST_CAPA)
    sms_sender = mocker.Mock()
    scheduler.set_sms_sender(sms_sender)
    return scheduler, sms_sender

@pytest.fixture
def booking_scheduler_with_email_mock(mocker):
    scheduler = BookingScheduler(TEST_CAPA)
    email_sender = mocker.Mock()
    scheduler.set_mail_sender(email_sender)
    return scheduler, email_sender

def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(booking_scheduler, customer):

    schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPA, customer)

    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_예약은_정시에만_가능하다_정시인_경우_예약가능(booking_scheduler, customer):

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer)
    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)

def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(booking_scheduler, customer):
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer)
    booking_scheduler.add_schedule(schedule)

    with pytest.raises(ValueError, match="Number of people is over restaurant capacity per hour"):
        booking_scheduler.add_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(booking_scheduler, customer):
    schedule = Schedule(ON_THE_HOUR, TEST_CAPA, customer)
    booking_scheduler.add_schedule(schedule)

    other_schedule = Schedule(ON_THE_HOUR + timedelta(hours=1), UNDER_CAPA, customer)
    booking_scheduler.add_schedule(other_schedule)

    assert booking_scheduler.has_schedule(schedule)
    assert booking_scheduler.has_schedule(other_schedule)

def test_예약완료시_SMS는_무조건_발송(booking_scheduler_with_sms_mock, customer):
    booking_scheduler, test_sms_sender = booking_scheduler_with_sms_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer)
    booking_scheduler.add_schedule(schedule)

    test_sms_sender.send.assert_called()

def test_이메일이_없는_경우에는_이메일_미발송(booking_scheduler_with_email_mock, customer):
    booking_scheduler, test_email_sender = booking_scheduler_with_email_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer)
    booking_scheduler.add_schedule(schedule)

    test_email_sender.send_mail.assert_not_called()

def test_이메일이_있는_경우에는_이메일_발송(booking_scheduler_with_email_mock, customer_with_email):
    booking_scheduler, test_email_sender = booking_scheduler_with_email_mock
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer_with_email)
    booking_scheduler.add_schedule(schedule)

    test_email_sender.send_mail.assert_called()

def test_현재날짜가_일요일인_경우_예약불가_예외처리(mocker, booking_scheduler, customer_with_email):
    mock_get_now = mocker.patch("booking_scheduler.BookingScheduler.get_now",
                                return_value=datetime.strptime("2026/07/05 09:00", "%Y/%m/%d %H:%M"))

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer_with_email)

    with pytest.raises(ValueError, match="Booking system is not available on Sunday"):
        booking_scheduler.add_schedule(schedule)

def test_현재날짜가_일요일이_아닌경우_예약가능(mocker, booking_scheduler, customer_with_email):
    mock_get_now = mocker.patch("booking_scheduler.BookingScheduler.get_now",
                                return_value=datetime.strptime("2026/07/06 09:00", "%Y/%m/%d %H:%M"))

    schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer_with_email)

    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)