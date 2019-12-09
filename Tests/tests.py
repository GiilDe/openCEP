import Processor
import ProcessingUtilities
from GraphBasedProcessing import GraphBasedProcessingUtilities
import data_formats

stock_types = ['AAME', 'AAON', 'MCRS', 'ZHNE']


if __name__ == "__main__":
    # Naive seq, and test
    processor = Processor.Processor("../sorted_NASDAQ_20080201_1.txt", data_formats.metastock7_attributes,
                                    data_formats.metastock7_time_index, data_formats.metastock7_type_index)
    stock_types_with_identifiers = \
        [ProcessingUtilities.EventTypeOrPatternAndIdentifier(type, i) for i, type in enumerate(stock_types)]
    # shuffle order for testing purposes
    temp = stock_types_with_identifiers[2]
    stock_types_with_identifiers[2] = stock_types_with_identifiers[0]
    stock_types_with_identifiers[0] = temp
    seq_event_pattern = ProcessingUtilities.EventPattern(stock_types_with_identifiers,
                                                         ProcessingUtilities.Seq(range(4)))
    seq_pattern_query = ProcessingUtilities.CleanPatternQuery(seq_event_pattern, [], 16)
    and_event_pattern = ProcessingUtilities.EventPattern(stock_types_with_identifiers, ProcessingUtilities.And())
    and_pattern_query = ProcessingUtilities.CleanPatternQuery(and_event_pattern, [], 16)
    pattern_queries = [seq_pattern_query, and_pattern_query]
    left_deep_initializer = GraphBasedProcessingUtilities.LeftDeepTreeInitializer()
    left_deep_tree_processor = GraphBasedProcessingUtilities.NaiveMultipleTreesGraphBasedProcessing(left_deep_initializer)
    processor.query(pattern_queries, left_deep_tree_processor, ProcessingUtilities.TrivialInputInterface(),
                    ProcessingUtilities.FileOutputInterface(["seq_test_results.txt", "and_test_results.txt"]))

