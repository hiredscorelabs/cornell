import pytest
from cornell.signals import cornell_signals, SignalNotRegistered, signal_context, MultipleSignalSubscribers


def test_unregistered_signal():
    with pytest.raises(SignalNotRegistered) as exep:
        with signal_context("nope"):
            pass
    assert exep.match('Signal nope not registered')


def test_multiple_subscribers():
    new_signal = cornell_signals.signal("new_signal")

    @new_signal.connect
    def one():  # pylint:disable=unused-variable
        pass

    @new_signal.connect
    def two(): # pylint:disable=unused-variable
        pass

    with pytest.raises(MultipleSignalSubscribers) as exep:
        with signal_context("new_signal"):
            pass

    assert exep.match("Only one subscriber allowed for new_signal")


def test_signal_with_result():
    result_func = cornell_signals.signal("result_func")

    @result_func.connect
    def func_with_result(num):  # pylint:disable=unused-variable
        return num * num

    with signal_context("result_func", 2) as result:
        assert result == 4
