'use client';

import { useState } from 'react';
import { Send, User, Bot, Mic } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatWindowProps {
    messages: Message[];
    onSendMessage: (message: string) => void;
    isLoading: boolean;
    isListening: boolean;
    onMicClick: () => void;
}

export function ChatWindow({ messages, onSendMessage, isLoading, isListening, onMicClick }: ChatWindowProps) {
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
            <div className="flex-grow p-6 overflow-y-auto">
                <div className="space-y-6">
                    {messages.map((message, index) => (
                        <div key={index} className={cn('flex items-start gap-4', message.role === 'user' ? 'justify-end' : 'justify-start')}>
                            {message.role === 'assistant' && (
                                <div className='flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gray-700 text-white'>
                                    <Bot className="w-5 h-5" />
                                </div>
                            )}
                            <div className={cn('p-4 rounded-lg max-w-lg', message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800')}>
                                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            </div>
                            {message.role === 'user' && (
                                <div className='flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-blue-600 text-white'>
                                    <User className="w-5 h-5" />
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Add a loading indicator */}
                    {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
                        <div className='flex items-start gap-4'>
                            <div className='flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gray-700 text-white'>
                                <Bot />
                            </div>
                            <div className='p-4 rounded-lg max-w-lg bg-gray-100 text-gray-800'>
                                <p className="text-sm italic">Thinking...</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="border-t p-4 bg-gray-50">
                <form onSubmit={handleSendMessage} className="flex items-center gap-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={isListening ? "Listening..." : "Ask a question about your document..."}
                        className="flex-grow p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200 disabled:text-gray-500 bg-white text-gray-900 placeholder:text-gray-500"
                        disabled={isLoading || isListening}
                    />
                    <button
                        type="button"
                        onClick={onMicClick}
                        className={cn(
                            "p-3 text-white rounded-lg",
                            isListening ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700",
                            "disabled:bg-gray-300"
                        )}
                        disabled={isLoading}
                    >
                        <Mic className="w-5 h-5" />
                    </button>
                    <button
                        type="submit"
                        className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        disabled={isLoading || isListening || !input.trim()}
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}