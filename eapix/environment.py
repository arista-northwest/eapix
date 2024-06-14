# -*- coding: utf-8 -*-
# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import os


# EAPI_DEFAULT_VERSION: int = os.environ.get("EAPI_DEFAULT_VERSION", 1)

# Specifies the default result encoding.  The alternative is 'text'
EAPI_DEFAULT_FORMAT = os.environ.get("EAPI_DEFAULT_FORMAT", "text")

# Specifies whether to add timestamps for each command by default
EAPI_INCLUDE_TIMESTAMPS = bool(os.environ.get("EAPI_INCLUDE_TIMESTAMPS", False))

EAPI_DEFAULT_TIMEOUT = int(os.environ.get("EAPI_DEFAULT_TIMEOUT", 30.0))

# By default eapi uses HTTP.  HTTPS ('https') is also supported
EAPI_DEFAULT_TRANSPORT = os.environ.get("EAPI_DEFAULT_TRANSPORT", "http")

# Set this to false to allow untrusted HTTPS/SSL
SSL_VERIFY = bool(os.environ.get("SSL_VERIFY", True))
