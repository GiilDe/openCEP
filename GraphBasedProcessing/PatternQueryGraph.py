from typing import List, Union
import ProcessingUtilities


class Node:
    """
    abstract class, predecessor of ConditionNode and EventNode
    """
    def __init__(self, conditions: List[ProcessingUtilities.Condition] = None, parent=None):
        if conditions is None:
            self.conditions = []
        self.conditions = conditions if conditions else []
        self.parent = parent
        self.partial_results_buffer = []

    def add_condition(self, condition: ProcessingUtilities.Condition):
        self.conditions.append(condition)

    def set_parent(self, parent):
        self.parent = parent

    def _check_conditions(self, partial_result: Union[ProcessingUtilities.PartialResult, ProcessingUtilities.Event])\
            -> bool:
        if partial_result.end_time - partial_result.start_time > ProcessingUtilities._time_limit:
            return False
        return all(condition.check_condition(partial_result) for condition in self.conditions)

    def _get_results(self):
        return self.partial_results_buffer

    def get_results(self):
        return [list(partial_result.completely_unpack().values()) for partial_result in self.partial_results_buffer]


class ConditionNode(Node):
    """
    represents an inner node in the graph that holds an operator and a condition list and partial results
    """
    def __init__(self, children: List[Node], operator: ProcessingUtilities.Operator, identifier=None,
                 conditions: List[ProcessingUtilities.Condition] = None, parent=None):
        """
        :param children:
        :param conditions:
        :param operator:
        :param parent:
        """
        super().__init__(conditions, parent)
        self.children = children
        self.operator = operator
        self.identifier = identifier

    def try_add_partial_result(self, partial_result: ProcessingUtilities.PartialResult, diffuser_child: Node):
        """
        :param partial_result:
        :param diffuser_child:
        :return:
        """
        children_buffers = [child._get_results() for child in self.children if child != diffuser_child]
        for new_result in self.operator.get_new_results(children_buffers, partial_result, self.identifier):
            if self._check_conditions(new_result):
                new_result.operator_type_of_node = type(self.operator)
                self.partial_results_buffer.append(new_result)
                if self.parent:
                    self.parent.try_add_partial_result(new_result, self)
        return self


class EventNode(Node):
    """
    represents a leaf node in the graph that holds events
    """
    def __init__(self, event_type_and_identifier: ProcessingUtilities.EventTypeOrPatternAndIdentifier,
                 parent: ConditionNode = None, conditions: List[ProcessingUtilities.Condition] = None):
        super().__init__(conditions, parent)
        self.event_type = event_type_and_identifier.event_type_or_pattern
        self.event_identifier = event_type_and_identifier.identifier

    def try_add_partial_result(self, event: ProcessingUtilities.Event):
        """
        adds a partial result
        :param event: an event corresponding to this leaf node
        :return: self
        """
        if self.event_type == event.get_type():
            partial_result = ProcessingUtilities.PartialResult({self.event_identifier: event},
                                                               identifier=self.event_identifier)
            if self._check_conditions(partial_result):
                self.partial_results_buffer.append(partial_result)
                self.parent.try_add_partial_result(partial_result, self)
        return self


class PatternQueryGraph:
    """
    a graph that represents a pattern query without operator nesting
    """
    def __init__(self, root_node: ConditionNode, event_nodes: List[EventNode]):
        self.root_node = root_node
        self.event_nodes = event_nodes


