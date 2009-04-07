#!/usr/bin/env python

# TiddlyWeb start for GoogleAppEngine.
#
# Note that TiddlyWeb itself is advancing at a faster rate
# than the adaptation of TiddlyWeb to GoogleAppEngine. This
# code may need adjustments.
#
# Based on example code that came from Google with the following
# header:
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import wsgiref.handlers

from tiddlyweb.web.serve import load_app


def main():
    wsgiref.handlers.CGIHandler().run(load_app())


if __name__ == '__main__':
    main()
