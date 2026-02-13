const API_BASE_URL = import.meta.env.VITE_BACKEND_URL;


export const apiService = {
  async ingestRepo(repoUrl) {
    const res = await fetch(`${API_BASE_URL}/ingest/repo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ git_url: repoUrl })
    });
    return res.json();
  },

  async getParsingStatus(repoId) {
    const res = await fetch(`${API_BASE_URL}/ingest/status/${repoId}`);
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
    const res = await fetch(`${API_BASE_URL}/query/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message, intent })
    });
    
    if (!res.ok) {
      throw new Error("Query failed");
    }
    
    return res.json();
  }
};
