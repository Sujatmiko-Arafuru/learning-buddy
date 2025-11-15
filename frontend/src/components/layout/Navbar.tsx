import React from 'react';
import { Navbar as BootstrapNavbar, Nav, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('userEmail');

  const handleLogout = () => {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <BootstrapNavbar bg="primary" variant="dark" expand="lg" className="mb-4">
      <Container>
        <BootstrapNavbar.Brand as={Link} to="/">
          🎓 Learning Buddy
        </BootstrapNavbar.Brand>
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/dashboard">
              Dashboard
            </Nav.Link>
            <Nav.Link as={Link} to="/catalog">
              Katalog
            </Nav.Link>
            <Nav.Link as={Link} to="/chat">
              Chat Assistant
            </Nav.Link>
          </Nav>
          <Nav>
            {userEmail ? (
              <>
                <Nav.Link disabled className="text-light">
                  {userEmail}
                </Nav.Link>
                <Nav.Link onClick={handleLogout} className="text-light">
                  Logout
                </Nav.Link>
              </>
            ) : (
              <Nav.Link as={Link} to="/onboarding" className="text-light">
                Mulai Belajar
              </Nav.Link>
            )}
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;

