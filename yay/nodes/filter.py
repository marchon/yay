
from yay.nodes import Node, Sequence
from yay.context import Context

class Filter(Node):

    def __init__(self, container, filter_expression):
        self.container = container
        if container:
            container.set_parent(self)
        self.filter_expression = filter_expression
        filter_expression.set_parent(self)

    def semi_resolve(self, context):
        if not hasattr(self.container, "semi_resolve"):
            self.error("Expected sequence, got '%s'" % self.container)

        resolved = self.container.semi_resolve(context)

        filtered = []
        for r in resolved:
            newctx = Context(context, {"@": r})
            if self.filter_expression.resolve(newctx):
                filtered.append(r)

        return Sequence(filtered)

    def get(self, context, idx):
        return self.semi_resolve(context).get(context, idx.resolve(context))

    def resolve(self, context):
        return list(f.resolve(context) for f in self.semi_resolve(context))

    def __repr__(self):
        return "Filter(%s, %s)" % (self.container, self.filter_expression)

    def walk(self, context):
        yield self.container
        yield self.filter_expression

