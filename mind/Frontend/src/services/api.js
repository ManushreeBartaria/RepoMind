<<<<<<< HEAD
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
=======
const API_BASE_URL = "http://127.0.0.1:8000";

let currentRepoUrl = null;
>>>>>>> 81426f0459cbfe3e235c8be0cd8b79ee0b53b473

export const apiService = {
  async ingestRepo(repoUrl) {
    const res = await fetch(`${API_BASE_URL}/ingest/repo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ git_url: repoUrl })
    });
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to analyze repository");
    }

    // store repo url for future queries
    currentRepoUrl = repoUrl;
    
    return res.json();
  },

  async getParsingStatus(repoId) {
    const res = await fetch(`${API_BASE_URL}/ingest/status/${repoId}`);
    
    if (!res.ok) {
      throw new Error("Failed to get parsing status");
    }
    
    return res.json();
  },

  async getFileContent(repoId, filePath) {
    const res = await fetch(
      `${API_BASE_URL}/api/repository/file?repo_id=${repoId}&path=${encodeURIComponent(filePath)}`
    );

    if (!res.ok) {
      throw new Error("Failed to fetch file content");
    }

    return res.json();
  },

  async queryRepo(message, intent) {
    if (!currentRepoUrl) {
      throw new Error("No repository selected. Please ingest a repository first.");
    }

    const res = await fetch(`${API_BASE_URL}/query/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repo_url: currentRepoUrl,
        query: message,
        intent
      })
    });
    
    if (!res.ok) {
      throw new Error("Query failed");
    }
    
    return res.json();
  },

  async getChatHistory() {
    const res = await fetch(`${API_BASE_URL}/query/history`);
    
    if (!res.ok) {
      throw new Error("Failed to fetch chat history");
    }
    
    return res.json();
  },

  async clearChatHistory() {
    const res = await fetch(`${API_BASE_URL}/query/history`, {
      method: "DELETE"
    });
    
    if (!res.ok) {
      throw new Error("Failed to clear chat history");
    }
    
    return res.json();
  }
};