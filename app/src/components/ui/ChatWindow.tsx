'use client';

import { useState } from 'react';
import { Send, User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
}

export function ChatWindow({ messages, onSendMessage }: ChatWindowProps) {
  const [input, setInput] = useState('');

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-white shadow-md rounded-lg">
      {/* Message Display Area */}
      <div className="flex-grow p-6 overflow-y-auto">
        <div className="space-y-6">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={cn('flex items-start gap-4', { 'flex-row-reverse': msg.role === 'user' })}
            >
              <div className={cn('flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
                msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-700 text-white'
              )}>
                {msg.role === 'user' ? <User /> : <Bot />}
              </div>
              <div
                className={cn('p-4 rounded-lg max-w-lg',
                  msg.role === 'user' ? 'bg-blue-50 text-gray-800' : 'bg-gray-100 text-gray-800'
                )}
              >
                <p className="text-sm">{msg.content}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Message Input Area */}
      <div className="border-t p-4 bg-gray-50">
        <form onSubmit={handleSendMessage} className="flex items-center gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your document..."
            className="flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder:text-gray-500"
          />
          <button
            type="submit"
            className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}