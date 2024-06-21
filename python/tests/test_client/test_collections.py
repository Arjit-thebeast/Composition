"""
Test collections module.
"""

from logging import DEBUG
from unittest import mock

from composio.client.collections import (
    Trigger,
    TriggerEventData,
    TriggerSubscription,
    trigger_names_str,
)
from composio.utils import logging


class TestTriggerNamesSerialization:
    """Test `trigger_names_str` method."""

    def test_converts_trigger_objects_to_comma_separated_string(self):
        trigger_list = [
            Trigger.GITHUB_COMMIT_EVENT,
            Trigger.SLACK_NEW_MESSAGE,
            Trigger.YOUTUBE_NEW_YOUTUBE_ACTIVITY,
        ]
        result = trigger_names_str(trigger_list)
        assert (
            result
            == "github_commit_event,slack_receive_message,youtube_new_activity_trigger"
        )

    def test_converts_trigger_strings_to_comma_separated_string(self):
        trigger_list = [
            "github_commit_event",
            "slack_receive_message",
            "youtube_new_activity_trigger",
        ]
        result = trigger_names_str(trigger_list)
        assert (
            result
            == "github_commit_event,slack_receive_message,youtube_new_activity_trigger"
        )

    def test_converts_mix_of_trigger_objects_and_strings(self):
        trigger_list = [
            Trigger.GITHUB_COMMIT_EVENT,
            "slack_receive_message",
            Trigger.YOUTUBE_NEW_YOUTUBE_ACTIVITY,
        ]
        result = trigger_names_str(trigger_list)
        assert (
            result
            == "github_commit_event,slack_receive_message,youtube_new_activity_trigger"
        )


def test_trigger_subscription(capsys, caplog) -> None:
    """Test trigger subscription multiplexing."""
    logging.setup(logging.Level.DEBUG)
    subscription = TriggerSubscription()
    subscription.set_alive()

    @subscription.callback(filters={"trigger_id": "trigger_1"})
    def _callback_1(event: TriggerEventData) -> None:  # pylint: disable=unused-argument
        print("Trigger 1 called from callback 1")

    @subscription.callback(filters={"trigger_id": "trigger_1"})
    def _callback_2(event: TriggerEventData) -> None:  # pylint: disable=unused-argument
        print("Trigger 1 called from callback 2")

    @subscription.callback(filters={"trigger_id": "trigger_2"})
    def _callback_3(event: TriggerEventData) -> None:  # pylint: disable=unused-argument
        print("Trigger 2 called from callback 3")

    with mock.patch.object(
        subscription,
        "_parse_payload",
        return_value=mock.Mock(
            metadata=mock.Mock(
                id="trigger_1",
            )
        ),
    ), caplog.at_level(DEBUG):
        subscription.handle_event(event="")

    assert (
        "Trigger 1 called from callback 1\n"
        "Trigger 1 called from callback 2\n" in capsys.readouterr().out
    )

    assert (
        "Skipping `_callback_3` since `trigger_id` filter does not match the event metadata"
        in caplog.text
    )

    with mock.patch.object(
        subscription,
        "_parse_payload",
        return_value=mock.Mock(
            metadata=mock.Mock(
                id="trigger_2",
            )
        ),
    ), caplog.at_level(DEBUG):
        subscription.handle_event(event="")

    assert (
        "Skipping `_callback_1` since `trigger_id` filter does not match the event metadata"
        in caplog.text
    )
    assert (
        "Skipping `_callback_2` since `trigger_id` filter does not match the event metadata"
        in caplog.text
    )
    assert "Trigger 2 called from callback 3\n" in capsys.readouterr().out
