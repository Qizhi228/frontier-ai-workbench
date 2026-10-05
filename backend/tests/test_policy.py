import unittest

from app.policy import ApprovalPolicy


class ApprovalPolicyTests(unittest.TestCase):
    def test_research_actions_are_safe_but_side_effects_require_approval(self):
        policy = ApprovalPolicy()

        self.assertFalse(policy.requires_approval("search_web"))
        self.assertFalse(policy.requires_approval("save_report"))
        self.assertTrue(policy.requires_approval("modify_code"))
        self.assertTrue(policy.requires_approval("delete_file"))
        self.assertTrue(policy.requires_approval("deploy_service"))
        self.assertTrue(policy.requires_approval("send_message"))


if __name__ == "__main__":
    unittest.main()
