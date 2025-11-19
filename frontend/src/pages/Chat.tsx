import React, { useState, useRef, useEffect } from 'react';
import { Card, Form, Button, InputGroup, Alert } from 'react-bootstrap';
import Container from '../components/layout/Container';
import { chatApi } from '../api/chat';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: 'Halo! Saya Learning Buddy, asisten belajar Anda. Ada yang bisa saya bantu?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

    setMessages([...messages, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      // Call chat API
      const response = await chatApi.sendMessage(userEmail, currentInput);
      
      const botResponse: Message = {
        id: messages.length + 2,
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);
    } catch (error: any) {
      const errorResponse: Message = {
        id: messages.length + 2,
        text: 'Maaf, terjadi kesalahan saat memproses pertanyaan Anda. Silakan coba lagi.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <h2 className="mb-4">Chat Assistant</h2>

      <Card>
        <Card.Header>
          <h5 className="mb-0">💬 Learning Buddy Chat</h5>
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
                  <div>{message.text}</div>
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

      <Alert variant="info" className="mt-3">
        <strong>Tips:</strong> Coba tanyakan tentang progres belajar, rekomendasi kursus, atau skill yang perlu ditingkatkan!
      </Alert>
    </Container>
  );
};

export default Chat;

