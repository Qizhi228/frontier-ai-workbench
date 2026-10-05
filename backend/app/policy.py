"""Permission policy for agent actions."""


class ApprovalPolicy:
    SAFE_ACTIONS = {"search_web", "fetch_source", "summarize", "save_report", "read_file"}
    APPROVAL_ACTIONS = {"modify_code", "delete_file", "deploy_service", "send_message", "run_command"}

    def requires_approval(self, action: str) -> bool:
        if action in self.SAFE_ACTIONS:
            return False
        if action in self.APPROVAL_ACTIONS:
            return True
        return True
