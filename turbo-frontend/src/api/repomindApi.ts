import { api } from "./client";

export async function analyzeRepo(repoUrl: string) {
  const res = await api.post("/analyze_repo", { repo_url: repoUrl });
  return res.data;
}

export async function askRepo(repoId: string, query: string) {
  const res = await api.post("/ask", { repo_id: repoId, query });
  return res.data;
}

export async function fetchFile(repoId: string, path: string) {
  const res = await api.get("/file", { params: { repo_id: repoId, path } });
  return res.data;
}
