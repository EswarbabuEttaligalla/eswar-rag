import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";

export default function AppLayout({ children }) {
  return (
    <div className="min-h-screen grid md:grid-cols-[260px_1fr]">
      <Sidebar />
      <div className="flex flex-col">
        <Navbar />
        <main className="px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
