# Copyright 2011 Isotoma Limited
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

import inspect, sys

import yay
from yay.nodes import Node, BoxingFactory, Sequence
from yay.nodes.datastore.bind import DataStore


class InstanceList(Node):

    """
    I am a list of Instance nodes - i.e. a one-to-many relationship
    """

    def __init__(self, value):
        self.value = value

    def get(self, idx):
        v = self.value.all()[idx]
        return BoxingFactory.box(v)

    def resolve(self):
        return list(x.resolve() for x in self.__iter__())

    def __iter__(self):
        for i in range(self.value.count()):
            yield self.get(i)


class Instance(Node):

    def __init__(self, value):
        self.value = value

        self.related = [x.get_accessor_name() for x in self.value._meta.get_all_related_objects()]
        self.many_to_many = [x.get_accessor_name() for x in self.value._meta.get_all_related_many_to_many_objects()]

    def get(self, key):
        v = getattr(self.value, key)

        if key in self.related or key in self.many_to_many:
            return InstanceList(v)

        return BoxingFactory.box(getattr(self.value, key))

    def resolve(self):
        mapping = {}
        for k in self.value._meta.get_all_field_names():
            if hasattr(self.value, k) and not isinstance(self.value._meta.get_field_by_name(k)[0], models.fields.related.ForeignKey):
                mapping[k] = self.get(k).resolve()
        return mapping


class Table(Node):

    def __init__(self, value):
        self.value = value

    def expand(self):
        seq = []

        for instance in self.value.objects.all():
             seq.append(Instance(instance))

        return Sequence(seq)

    def resolve(self):
        return self.expand().resolve()


_horrible_cludge = False

class DjangoStore(DataStore):

    def __init__(self, config):
        try:
            from django.conf import settings
            from django.db import models

            # Make sure our adaptor is registered....
            global _horrible_cludge
            if not _horrible_cludge:
                BoxingFactory.register(lambda x: isinstance(x, models.Model), Instance)
                _horrible_cludge = True
        except ImportError:
            self.error("Django Models are not available as cannot import django")

        self.config = config
        self.tables = {}

    def get_model(self, key):
        model = self.config.get("model").resolve()
        __import__(model)
        m = sys.modules[model]

        if not key in dir(m):
            self.error("Model '%s' not defined in '%s'" % (key, model))

        v = getattr(m, key)

        from django.db import models
        if not inspect.isclass(v) or not issubclass(v, models.Model):
            self.error("'%s' is defined in '%s', but it isn't a Django model" % (key, model))

        return Table(v)

    def get(self, key):
        if key in self.tables:
            return self.tables[key]

        if self.config.get("model"):
            tbl = self.tables[key] = self.get_model(key)
            return tbl

        self.error("'model' not specified")

    def error(self, msg):
        raise RuntimeError(msg)


