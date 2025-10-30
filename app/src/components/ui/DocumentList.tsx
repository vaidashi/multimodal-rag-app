'use client';

import { FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Document {
  name: string;
}

interface DocumentListProps {
  documents: Document[];
  selectedDocument: Document | null;
  onSelectDocument: (document: Document) => void;
}

export function DocumentList({ documents, selectedDocument, onSelectDocument }: DocumentListProps) {
  if (documents.length === 0) {
    return <div className="p-4 text-sm text-gray-500">No documents uploaded yet.</div>;
  }

  return (
    <nav className="space-y-2 p-4">
      <h2 className="text-lg font-semibold mb-2 text-gray-800">My Documents</h2>
      {documents.map((doc) => (
        <button
          key={doc.name}
          onClick={() => onSelectDocument(doc)}
          className={cn(
            'w-full flex items-center p-3 rounded-lg text-left transition-colors',
            selectedDocument?.name === doc.name
              ? 'bg-blue-600 text-white'
              : 'text-gray-700 hover:bg-gray-100'
          )}
        >
          <FileText className="w-5 h-5 mr-3 flex-shrink-0" />
          <span className="truncate flex-grow">{doc.name}</span>
        </button>
      ))}
    </nav>
  );
}