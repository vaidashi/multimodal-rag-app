'use client';

import { useState } from 'react';
import { FileUpload } from '@/components/ui/FileUpload';
import { Document, DocumentList } from '@/components/ui/DocumentList';
import { ChatWindow, Message } from '@/components/ui/ChatWindow';

// --- Mock Data ---
const MOCK_DOCUMENTS: Document[] = [
  { name: 'product_roadmap.pdf' },
  { name: 'meeting_notes.txt' },
];

const MOCK_MESSAGES: Message[] = [
  { role: 'assistant', content: "Hello! I'm ready to answer questions about your documents." },
];
// --- End Mock Data ---

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>(MOCK_DOCUMENTS);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(MOCK_DOCUMENTS[0] || null);
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES);

  const handleFileUpload = (file: File) => {
    console.log('Uploading file:', file.name);
    const newDoc = { name: file.name };
    setDocuments((prevDocs) => [...prevDocs, newDoc]);
    setSelectedDocument(newDoc);
    setMessages([MOCK_MESSAGES[0]]); // Reset chat
  };

  const handleSendMessage = (messageContent: string) => {
    const userMessage: Message = { role: 'user', content: messageContent };
    setMessages((prev) => [...prev, userMessage]);

    // Mock assistant response
    setTimeout(() => {
      const assistantResponse: Message = {
        role: 'assistant',
        content: `This is a mocked response about "${selectedDocument?.name}". I will be a real AI in the next step!`,
      };
      setMessages((prev) => [...prev, assistantResponse]);
    }, 1000);
  };

  return (
    <main className="flex min-h-screen bg-gray-50 font-sans">
      {/* Sidebar for Document List */}
      <aside className="w-1/4 min-w-[300px] bg-white border-r">
        <div className="p-4 border-b">
            <h1 className="text-xl font-bold text-gray-900">Doc Intelligence</h1>
        </div>
        <DocumentList
          documents={documents}
          selectedDocument={selectedDocument}
          onSelectDocument={setSelectedDocument}
        />
      </aside>

      {/* Main Content Area */}
      <section className="flex-1 flex flex-col p-6">
        {selectedDocument ? (
          <div className="flex-1">
             <ChatWindow messages={messages} onSendMessage={handleSendMessage} />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full bg-white rounded-lg shadow-sm">
             <h2 className="text-2xl font-semibold text-gray-700 mb-4">Welcome!</h2>
             <p className="text-gray-500 mb-8">Upload a document to get started.</p>
             <div className="w-full max-w-lg">
                <FileUpload onFileUpload={handleFileUpload} />
             </div>
          </div>
        )}
      </section>
    </main>
  );
}