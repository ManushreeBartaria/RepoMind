import { BrowserRouter, Routes, Route } from "react-router-dom";
import UploadRepoPage from "./pages/UploadRepoPage";
import RepoChatPage from "./pages/RepoChatPage";
import StarredChatsPage from "./pages/StarredChatsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadRepoPage />} />
        <Route path="/chat" element={<RepoChatPage />} />
        <Route path="/starred" element={<StarredChatsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
