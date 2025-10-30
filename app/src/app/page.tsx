'use client';

import { useState, useEffect } from 'react';
import { FileUpload } from '@/components/ui/FileUpload';
import { Document, DocumentList } from '@/components/ui/DocumentList';
import { ChatWindow, Message } from '@/components/ui/ChatWindow';

const GREETING_MESSAGE: Message = {
  role: 'assistant',
  content: "Hello! Upload a document and I'll be ready to answer your questions.",
};

export default function Home() {
  // Use environment variable if set, otherwise use empty string for relative URLs
  const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [messages, setMessages] = useState<Message[]>([GREETING_MESSAGE]);

  const [isUploading, setIsUploading] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    setIsUploading(true);
    setMessages([{ role: 'assistant', content: `Processing ${file.name}...` }]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/api/ingest`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Failed to ingest document';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If response is not JSON, use the text
          const errorText = await response.text();
          errorMessage = errorText || `Server error: ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Ingestion successful:', data);

      const newDoc = { name: file.name };
      // For now, just replace the doc list with the new one.
      // A more robust app would maintain a list.
      setDocuments([newDoc]);

      // Update selected document and message together to avoid race condition
      setSelectedDocument(newDoc);
      setMessages([{ role: 'assistant', content: `Successfully uploaded ${file.name}! Ask me anything about it.` }]);

    } catch (error) {
      console.error('Upload error:', error);
      setMessages([{ role: 'assistant', content: `Error uploading file: ${error instanceof Error ? error.message : 'Unknown error'}` }]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (messageContent: string) => {
    if (!selectedDocument) return;

    const userMessage: Message = { role: 'user', content: messageContent };
    setMessages((prev) => [...prev, userMessage]);
    setIsAnswering(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: messageContent, filename: selectedDocument.name }),
      });

      if (!response.ok) {
        let errorMessage = 'Failed to get response from chat API';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If response is not JSON, use the text
          const errorText = await response.text();
          errorMessage = errorText || `Server error: ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      const { answer, sources } = await response.json();
      console.log('Chat response:', answer, sources);

      const assistantMessage: Message = { role: 'assistant', content: answer };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = { role: 'assistant', content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsAnswering(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-gray-100 font-sans">
      {/* Sidebar for Document List */}
      <aside className="w-1/4 min-w-[300px] bg-white border-r">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-gray-900">Doc Intelligence</h1>
        </div>
        <div className="p-4">
          <FileUpload onFileUpload={handleFileUpload} disabled={isUploading} />
        </div>
        <DocumentList
          documents={documents}
          selectedDocument={selectedDocument}
          onSelectDocument={setSelectedDocument}
        />
      </aside>

      {/* Main Content Area */}
      <section className="flex-1 flex flex-col p-6">
        <div className="flex-1 h-full">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isAnswering || isUploading}
          />
        </div>
      </section>
    </main>
  );
}