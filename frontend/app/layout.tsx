import type { Metadata } from "next";
import "./globals.css";
import ClientLayout from "./client-layout";

export const metadata: Metadata = {
  title: "RAG Chatbot",
  description: "Agentic RAG Chatbot powered by CopilotKit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased h-screen overflow-hidden">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
