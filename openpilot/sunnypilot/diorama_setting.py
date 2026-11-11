"""
Copyright (c) 2026-, Ernie Chu.

This file is part of zoompilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The Diorama setting: off, usb or wifi, stored as an index into MODES. dioramad
(the diorama_repo submodule) listens on every interface, so manager runs it
for either of the last two.

usb is an iPhone on the comma's one USB-C port. Its network is jetlink's iOS
gadget, which only jetlinkd builds, so usb holds the Jetlink setting on iOS
and the panels lock it there: the port is Diorama's, and jetlink runs no big
model over it. The Jetlink setting the user had is kept in BEFORE and put
back once Diorama leaves usb. off and wifi leave Jetlink alone.

The standard library only, as jetlink_adapter: manager imports it to build the
process list.
"""
from __future__ import annotations

from openpilot.sunnypilot.jetlink_adapter import KEYS, MODES as LINK_MODES

KEY = "Diorama"
MODES = ("off", "usb", "wifi")
# the Jetlink setting from before Diorama took the port; there only while it holds it
BEFORE = "DioramaJetlinkBefore"
LINK_IOS = LINK_MODES.index("ios")


def mode(params) -> str:
  """The setting, one of MODES; unset or out of range is off."""
  index = params.get(KEY)
  return MODES[index] if isinstance(index, int) and 0 <= index < len(MODES) else "off"


def streaming(params) -> bool:
  """Should dioramad run (onroad)?"""
  return mode(params) != "off"


def holds_port(params) -> bool:
  """Diorama on usb: the Jetlink setting is held on iOS for it."""
  return mode(params) == "usb"


def sync_link(params) -> None:
  """Hold the Jetlink setting on iOS while Diorama is on usb, and give it back
  after. From the state, not the tap, so it holds whoever changed either setting;
  the UI calls it on its params pass."""
  before = params.get(BEFORE)
  link = params.get(KEYS.link)
  if holds_port(params):
    if before is None:
      params.put(BEFORE, link if isinstance(link, int) else 0, block=True)
    if link != LINK_IOS:
      params.put(KEYS.link, LINK_IOS, block=True)
  elif before is not None:
    params.put(KEYS.link, before if 0 <= before < len(LINK_MODES) else 0, block=True)
    params.remove(BEFORE)
