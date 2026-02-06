import { create } from "zustand";

type Highlight = { start: number; end: number; reason?: string };

type UIBlock =
  | { type: "dependency_graph"; data: any }
  | { type: "impact_analysis"; data: any }
  | { type: "related_files"; data: any }
  | { type: "file_tree_highlight"; data: { files: string[] } }
  | { type: "code_highlights"; data: { file: string; highlights: Highlight[] } };

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  ui?: UIBlock[];
};

type StarredChat = {
  chatId: string;
  repoId: string;
  title: string;
  messages: Message[];
};

type RepoStore = {
  repoId: string | null;
  fileTree: any;

  selectedFile: string | null;
  hoveredFile: string | null;

  fileHighlights: string[];
  codeHighlights: Record<string, Highlight[]>;

  messages: Message[];
  uiPanels: UIBlock[];

  starredChats: StarredChat[];

  setRepoId: (id: string) => void;
  setFileTree: (tree: any) => void;

  setSelectedFile: (path: string | null) => void;
  setHoveredFile: (path: string | null) => void;

  addMessage: (msg: Message) => void;
  setPanels: (panels: UIBlock[]) => void;

  highlightFiles: (files: string[]) => void;
  setCodeHighlights: (file: string, highlights: Highlight[]) => void;

  starCurrentChat: (title: string) => void;
  loadStarredChats: () => void;
};

export const useRepoStore = create<RepoStore>((set, get) => ({
  repoId: null,
  fileTree: null,

  selectedFile: null,
  hoveredFile: null,

  fileHighlights: [],
  codeHighlights: {},

  messages: [],
  uiPanels: [],

  starredChats: [],

  setRepoId: (id) => set({ repoId: id }),
  setFileTree: (tree) => set({ fileTree: tree }),

  setSelectedFile: (path) => set({ selectedFile: path }),
  setHoveredFile: (path) => set({ hoveredFile: path }),

  addMessage: (msg) => set({ messages: [...get().messages, msg] }),

  setPanels: (panels) => set({ uiPanels: panels }),

  highlightFiles: (files) => set({ fileHighlights: files }),

  setCodeHighlights: (file, highlights) =>
    set({ codeHighlights: { ...get().codeHighlights, [file]: highlights } }),

  loadStarredChats: () => {
    const raw = localStorage.getItem("repomind_starred_chats");
    set({ starredChats: raw ? JSON.parse(raw) : [] });
  },

  starCurrentChat: (title) => {
    const { repoId, messages, starredChats } = get();
    if (!repoId) return;

    const newChat = {
      chatId: "chat_" + Date.now(),
      repoId,
      title,
      messages
    };

    const updated = [newChat, ...starredChats];
    localStorage.setItem("repomind_starred_chats", JSON.stringify(updated));
    set({ starredChats: updated });
  }
}));
