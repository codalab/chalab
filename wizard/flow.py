from itertools import chain


def drop_first(xs, n=1):
    it = iter(xs)
    for i in range(n):
        next(it)
    return it


class FlowItem(object):
    name = None

    def __init__(self, id_, challenge, current_cls):
        assert self.name is not None, "Missing flow name"

        self._challenge = challenge

        self.id = id_
        self.slug = self.name.lower()
        self.active = self.__class__ == current_cls
        self.url = 'wizard:challenge:%s' % self.slug
        self.descr_template = 'wizard/flow/descr/_%s.html' % self.slug

    @property
    def is_prepared(self):
        try:
            self._is_ready(self._challenge)
            return True
        except AttributeError:
            return False

    @property
    def is_ready(self):
        return self._is_ready(self._challenge)

    def _is_ready(self, challenge):
        raise NotImplemented


class DataFlowItem(FlowItem):
    name = 'Data'

    def _is_ready(self, c):
        return c.dataset.is_ready


class SplitFlowItem(FlowItem):
    name = 'Split'

    def _is_ready(self, c):
        return c.task.is_ready


class MetricFlowItem(FlowItem):
    name = 'Metric'

    def _is_ready(self, c):
        return c.metric.is_ready


class ProtocolFlowItem(FlowItem):
    name = 'Protocol'

    def _is_ready(self, c):
        return c.protocol.is_ready


class BaselineFlowItem(FlowItem):
    name = 'Baseline'

    def _is_ready(self, c):
        return c.baseline.is_ready


class DocumentationFlowItem(FlowItem):
    name = 'Documentation'

    def _is_ready(self, c):
        return c.documentation.is_ready


class Flow(object):
    FLOW = [DataFlowItem, SplitFlowItem, MetricFlowItem, ProtocolFlowItem,
            BaselineFlowItem, DocumentationFlowItem]

    def __init__(self, current_clss, challenge):
        self._current_clss = current_clss
        self._challenge = challenge

    @property
    def current(self):
        xs = [x for x in self if x.active]

        assert len(xs) <= 1
        return xs[0] if xs else None

    @property
    def id(self):
        return self.current.id

    @property
    def name(self):
        return self.current.name

    @property
    def slug(self):
        return self.current.slug

    @property
    def previous(self):
        for (prev, cur) in zip(chain([None], self), self):
            if cur.active:
                return prev

        assert False, "Unknown current: %s" % self._current_clss

    @property
    def next(self):
        for (cur, next_) in zip(self, chain(drop_first(self), [None])):
            if cur.active:
                return next_

        assert False, "Unknown current: %s" % self._current_clss

    def __iter__(self):
        return (X(i + 1, self._challenge, self._current_clss)
                for i, X in enumerate(self.FLOW))

    def __len__(self):
        return len(self.FLOW)


class FlowOperationMixin:
    current_flow = None

    def get_context_data(self, challenge=None, **kwargs):
        context = super(FlowOperationMixin, self).get_context_data(**kwargs)
        context['flow'] = Flow(self.current_flow, challenge)
        return context
