import unittest
from server_project.objects.conversation_history_record import ConversationHistoryRecord


class MyTestCase(unittest.TestCase):
    def test_update_valid_field_success(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.update_field('GSR', 5)
        self.assertEqual(record.GSR, 5)
        self.assertEqual(record.max_GSR, 5)
        record.update_field('max_GSR', 10)
        self.assertEqual(record.max_GSR, 10)

    def test_ignore_undefined_field_value(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.update_field("status", 'undefined')
        self.assertNotEqual(record.status, 'undefined')

    def test_undefined_field_value(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.update_field("latestAgentId", None)
        self.assertNotEqual(record.latestAgentId, None)

    def test_initial_update(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.update_maxGSR(5)
        self.assertEqual(record.max_GSR, 5)

    def test_update_with_higher_value(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.max_GSR = 10
        record.update_maxGSR(15)
        self.assertEqual(record.max_GSR, 15)

    def test_update_with_lower_value(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.max_GSR = 20
        record.update_maxGSR(10)
        self.assertEqual(record.max_GSR, 20)

    def test_update_with_equal_value(self):
        start_time = "2024-04-29 16:10:18.818+0000"
        start_time_L = 1714407018818
        conversation_id = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id = "3998511138"
        full_dialog_status = "CLOSE"
        latest_agent_full_name = "טל הלן פרנץ"
        status = "CLOSE"
        record = ConversationHistoryRecord(start_time, start_time_L, conversation_id, latest_agent_id,
                                           full_dialog_status, latest_agent_full_name, status)
        record.max_GSR = 25
        record.update_maxGSR(25)
        self.assertEqual(record.max_GSR, 25)

    def test_update_fields(self):
        start_time1 = "2024-04-29 16:10:18.818+0000"
        start_time_L1 = 1714407018818
        conversation_id1 = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id1 = "3998511138"
        full_dialog_status1 = "CLOSE"
        latest_agent_full_name1 = "טל הלן פרנץ"
        status1 = "CLOSE"
        record1 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id1, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        conversation_id2 = "47b21186-4501-4363-8752-123124ffs"
        record2 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id2, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record1.update(record2)
        self.assertEqual(record1.conversationId, conversation_id2)

    def test_update_GSR(self):
        start_time1 = "2024-04-29 16:10:18.818+0000"
        start_time_L1 = 1714407018818
        conversation_id1 = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id1 = "3998511138"
        full_dialog_status1 = "CLOSE"
        latest_agent_full_name1 = "טל הלן פרנץ"
        status1 = "CLOSE"
        record1 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id1, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record1.GSR=10.0
        conversation_id2 = "47b21186-4501-4363-8752-123124ffs"
        record2 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id2, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record2.GSR = 5.0
        record1.update(record2)
        self.assertEqual(record1.GSR, 5.0)

    def test_ignore_none_and_undefined_values(self):
        start_time1 = "2024-04-29 16:10:18.818+0000"
        start_time_L1 = 1714407018818
        conversation_id1 = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id1 = "3998511138"
        full_dialog_status1 = "CLOSE"
        latest_agent_full_name1 = "טל הלן פרנץ"
        status1 = "CLOSE"
        record1 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id1, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record1.duration=693443
        record1.source="SHARK"
        conversation_id2 = "47b21186-4501-4363-8752-123124ffs"
        record2 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id2, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record2.duration = None
        record2.source="undefined"
        record1.update(record2)
        self.assertEqual(record1.duration, 693443)
        self.assertEqual(record1.source, "SHARK")

    def test_partial_update(self):
        start_time1 = "2024-04-29 16:10:18.818+0000"
        start_time_L1 = 1714407018818
        conversation_id1 = "47b21186-4501-4363-8752-27bc8bd212b7"
        latest_agent_id1 = "3998511138"
        full_dialog_status1 = "CLOSE"
        latest_agent_full_name1 = "טל הלן פרנץ"
        status1 = "CLOSE"
        record1 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id1, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record1.duration = 693443
        record1.source = "SHARK"
        conversation_id2 = "47b21186-4501-4363-8752-123124ffs"
        record2 = ConversationHistoryRecord(start_time1, start_time_L1, conversation_id2, latest_agent_id1,
                                            full_dialog_status1, latest_agent_full_name1, status1)
        record2.duration = 500000
        record2.source = None
        record1.update(record2)
        self.assertEqual(record1.duration, 500000)
        self.assertEqual(record1.source, "SHARK")


if __name__ == '__main__':
    unittest.main()
