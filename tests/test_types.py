# -*- coding: utf-8 -*-
# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import pytest

from eapix.types import Target


def test_target(target, starget):

    t = Target.from_url(target)
    t = Target.from_url(t)
    assert str(t).startswith("http:")
    t = Target.from_url(starget)
    assert str(t).startswith("https:")

    with pytest.raises(ValueError):
        t = Target.from_url(":///_10:600000")


    t = Target("http", "host.lab", 80)
    assert str(t) == "http://host.lab:80"

    t = Target("http", "host", 8080)
    assert str(t) == "http://host:8080"

    with pytest.raises(ValueError):
        Target("bogus", "host", port=6000)

    with pytest.raises(ValueError):
        Target("http", "host", port=600000)