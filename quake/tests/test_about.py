# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

import pytest

from quake import quake_version
from quake.about import AboutDialog


@pytest.fixture
def dialog(mocker, monkeypatch):
    mocker.patch("quake.simplegladeapp.Gtk.Widget.show_all")
    monkeypatch.setenv("LANGUAGE", "en_US.UTF-8")
    yield AboutDialog()


def test_version_test(dialog):
    assert dialog.get_widget("aboutdialog").get_version() == quake_version()


def test_title(dialog):
    assert dialog.get_widget("aboutdialog").get_title() == "About Quake"
