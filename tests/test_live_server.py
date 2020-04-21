"""
End-to-end tests with a live SMTP server.

Andrew DeOrio <awdeorio@umich.edu>
"""
import textwrap
from pathlib import Path
import logging
import sh
import pytest
import aiosmtpd.controller
import aiosmtpd.handlers


# The sh library triggers lot of false no-member errors
# pylint: disable=no-member

# Test fixtures need to be inputs, but aren't always used
# pylint: disable=unused-argument

logging.getLogger("sh").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


@pytest.fixture(name='live_smtp_server')
def setup_teardown_live_smtp_server():
    """Start a message-swallowing SMTP server in a separate thread."""
    controller = aiosmtpd.controller.Controller(
        aiosmtpd.handlers.Sink(),
        port=8025,
    )
    controller.start()
    yield controller
    controller.stop()


def test_simple(tmpdir, live_smtp_server):
    """Simple, unauthenticated test."""
    # Simple template
    template_path = Path(tmpdir/"template.txt")
    template_path.write_text(textwrap.dedent(u"""\
        TO: to@test.com
        FROM: from@test.com

        {{message}}
    """))

    # Simple database
    database_path = Path(tmpdir/"database.csv")
    database_path.write_text(textwrap.dedent(u"""\
        message
        hello
    """))

    # Simple unsecure server config
    config_path = Path(tmpdir/"server.conf")
    config_path.write_text(textwrap.dedent(u"""\
        [smtp_server]
        host = localhost
        port = 8025
    """))

    # Run mailmerge
    sh.mailmerge(
        "--template", template_path,
        "--database", database_path,
        "--config", config_path,
        "--no-dry-run",
    )