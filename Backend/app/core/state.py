class AppState:
    def __init__(self):
        self.graph = None
        self.repos = {}  # repo_id → {status, tree}


state = AppState()
