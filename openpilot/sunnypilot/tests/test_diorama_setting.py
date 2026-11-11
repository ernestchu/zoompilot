"""
Copyright (c) 2026-, Ernie Chu.

This file is part of zoompilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.sunnypilot import diorama_setting
from openpilot.sunnypilot.diorama_setting import BEFORE, KEY, sync_link
from openpilot.sunnypilot.jetlink_adapter import KEYS

OFF, USB, WIFI = 0, 1, 2
LINK_OFF, LINK_USB, LINK_IOS = 0, 1, 2


class FakeParams:
  def __init__(self, **values):
    self.values = dict(values)

  def get(self, key):
    return self.values.get(key)

  def put(self, key, value, block=False):
    self.values[key] = value

  def remove(self, key):
    self.values.pop(key, None)


def _params(diorama, link):
  return FakeParams(**{KEY: diorama, KEYS.link: link})


def test_mode():
  assert [diorama_setting.mode(_params(i, 0)) for i in (OFF, USB, WIFI)] == ["off", "usb", "wifi"]
  assert diorama_setting.mode(_params(None, 0)) == "off"
  assert diorama_setting.mode(_params(5, 0)) == "off"


def test_usb_holds_jetlink_on_ios_and_gives_it_back():
  for link in (LINK_OFF, LINK_USB, LINK_IOS):
    p = _params(USB, link)
    sync_link(p)
    assert p.get(KEYS.link) == LINK_IOS and p.get(BEFORE) == link
    sync_link(p)  # every params pass: still held, the user's own setting still kept
    assert p.get(KEYS.link) == LINK_IOS and p.get(BEFORE) == link
    p.put(KEY, WIFI)
    sync_link(p)
    assert p.get(KEYS.link) == link and p.get(BEFORE) is None


def test_off_and_wifi_leave_jetlink_alone():
  for diorama in (OFF, WIFI):
    for link in (LINK_OFF, LINK_USB, LINK_IOS):
      p = _params(diorama, link)
      sync_link(p)
      assert p.get(KEYS.link) == link and p.get(BEFORE) is None


def test_held_link_moved_elsewhere_goes_back_to_ios():
  p = _params(USB, LINK_USB)
  sync_link(p)
  p.put(KEYS.link, LINK_OFF)
  sync_link(p)
  assert p.get(KEYS.link) == LINK_IOS and p.get(BEFORE) == LINK_USB
