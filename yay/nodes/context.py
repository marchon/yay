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

from yay.nodes import Node

class Context(Node):
    """
    A way of capturing context in the graph
    """

    def __init__(self, value, context):
        super(Context, self).__init__(value)
        self.context = context

    def get_context(self, key):
        val = self.context.get(key, None)
        if not val:
            val = super(Context, self).get_context(key)
        return val

    def semi_resolve(self, context):
        return self.value.semi_resolve(context)

    def resolve(self, context):
        return self.value.resolve(context)

    def __repr__(self):
        return "Context(%s)" % self.value

