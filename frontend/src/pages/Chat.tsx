import React, { useState, useRef, useEffect } from 'react';
import { Card, Form, Button, InputGroup, Alert } from 'react-bootstrap';
import { FaComments } from 'react-icons/fa';
import Container from '../components/layout/Container';
import { chatApi } from '../api/chat';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chat: React.FC = () => {

  const loadMessagesFromStorage = (): Message[] => {
    const userEmail = localStorage.getItem('userEmail');
    if (!userEmail) {
      return [
        {
          id: 1,
          text: 'Halo! Saya Learning Buddy, asisten belajar Anda. Ada yang bisa saya bantu?',
          sender: 'bot',
          timestamp: new Date(),
        },
      ];
    }

    const storageKey = `chat_messages_${userEmail}`;
    const savedMessages = localStorage.getItem(storageKey);
    
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        return parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
      } catch (error) {
        console.error('Error loading chat history:', error);
      }
    }

    // Default welcome message
    return [
      {
        id: 1,
        text: 'Halo! Saya Learning Buddy, asisten belajar Anda. Ada yang bisa saya bantu?',
        sender: 'bot',
        timestamp: new Date(),
      },
    ];
  };

  const [messages, setMessages] = useState<Message[]>(loadMessagesFromStorage);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail && messages.length > 0) {
      const storageKey = `chat_messages_${userEmail}`;
      // Save to localStorage (convert Date to string for JSON)
      const messagesToSave = messages.map((msg) => ({
        ...msg,
        timestamp: msg.timestamp.toISOString(),
      }));
      localStorage.setItem(storageKey, JSON.stringify(messagesToSave));
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

const handleSend = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!input.trim()) return;

  const userEmail = localStorage.getItem('userEmail');
  if (!userEmail) {
    alert('Silakan lakukan onboarding terlebih dahulu');
    return;
  }

  const userMessage: Message = {
    id: messages.length + 1,
    text: input,
    sender: 'user',
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  const currentInput = input;
  setInput('');
  setLoading(true);

  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let timeoutTriggered = false; // <-- tambahan penting

  try {
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        timeoutTriggered = true; // <-- menandai timeout yang menang
        reject(new Error('TIMEOUT'));
      }, 90000);
    });

    const response = await Promise.race([
      chatApi.sendMessage(userEmail, currentInput),
      timeoutPromise,
    ]);

    // Sukses
    const botResponse: Message = {
      id: messages.length + 2,
      text: (response as any).response,
      sender: 'bot',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, botResponse]);
  } catch (error) {
    const errorResponse: Message = {
      id: messages.length + 2,
      text: timeoutTriggered
        ? 'Maaf, chatbot membutuhkan waktu lama untuk menjawab. Silakan ulangi pertanyaan Anda.'
        : 'Maaf, terjadi kesalahan saat memproses pertanyaan Anda. Silakan coba lagi.',
      sender: 'bot',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, errorResponse]);
  } finally {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    setLoading(false);
  }
};



  return (
    <Container>
      <h2 className="mb-4">Chat Assistant</h2>

      <Card>
        <Card.Header>
          <h5 className="mb-0">
            <FaComments className="me-2 text-primary" aria-hidden="true" />
            Learning Buddy Chat
          </h5>
        </Card.Header>
        <Card.Body style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              marginBottom: '1rem',
              padding: '1rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
            }}
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={`mb-3 d-flex ${
                  message.sender === 'user' ? 'justify-content-end' : 'justify-content-start'
                }`}
              >
                <div
                  className={`p-3 rounded ${
                    message.sender === 'user'
                      ? 'bg-primary text-white'
                      : 'bg-white border'
                  }`}
                  style={{ maxWidth: '70%' }}
                >
                  <div style={{ whiteSpace: 'pre-wrap' }}>{message.text}</div>
                  <small
                    className={`d-block mt-1 ${
                      message.sender === 'user' ? 'text-white-50' : 'text-muted'
                    }`}
                    style={{ fontSize: '0.75rem' }}
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </small>
                </div>
              </div>
            ))}
            {loading && (
              <div className="d-flex justify-content-start">
                <div className="p-3 rounded bg-white border">
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <Form onSubmit={handleSend}>
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Tanyakan sesuatu tentang progres belajar Anda..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <Button variant="primary" type="submit" disabled={loading}>
                Kirim
              </Button>
            </InputGroup>
          </Form>
        </Card.Body>
      </Card>

      <div className="mt-3 d-flex justify-content-between align-items-center">
        <Alert variant="info" className="mb-0 flex-grow-1 me-3">
          <strong>Tips:</strong> Coba tanyakan tentang progres belajar, rekomendasi kursus, atau skill yang perlu ditingkatkan!
        </Alert>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => {
            if (window.confirm('Apakah Anda yakin ingin menghapus semua riwayat chat?')) {
              const userEmail = localStorage.getItem('userEmail');
              if (userEmail) {
                const storageKey = `chat_messages_${userEmail}`;
                localStorage.removeItem(storageKey);
              }
              // Reset to welcome message
              setMessages([
                {
                  id: 1,
                  text: 'Halo! Saya Learning Buddy, asisten belajar Anda. Ada yang bisa saya bantu?',
                  sender: 'bot',
                  timestamp: new Date(),
                },
              ]);
              // Also clear backend history
              if (userEmail) {
                chatApi.clearHistory(userEmail).catch(console.error);
              }
            }
          }}
        >
          🗑️ Hapus Riwayat
        </Button>
      </div>
    </Container>
  );
};

export default Chat;

