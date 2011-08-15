# Copyright 2010-2011 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import copy
from yay.nodes import Node

class Copy(Node):
    """
    I resolve a node and deepcopy the outcome

    I am a replacing node and do not care about data i am overlaying
    """
    def __init__(self, value):
        self.value = value
        value.set_parent(self)

    def get(self, idx, default=None):
        return self.value.get(idx, default)

    def expand(self):
        return self.value.expand()

    def resolve(self):
        return self.value.resolve()

    def walk(self):
        yield self.value

    def clone(self):
        return self.value.clone()

