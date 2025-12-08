import React from 'react';
import { Navbar as BootstrapNavbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { FaGraduationCap } from 'react-icons/fa';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const userEmail =
    localStorage.getItem('userEmail') ||
    localStorage.getItem('email') ||
    localStorage.getItem('user_email');
  
  const isAuthenticated = Boolean(token && userEmail);

  const handleLogout = () => {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    localStorage.removeItem('name');
    localStorage.removeItem('user_email');
    localStorage.removeItem('userName');
    navigate('/login');
  };

  return (
    <BootstrapNavbar bg="primary" variant="dark" expand="lg" className="mb-4">
      <Container>
        <BootstrapNavbar.Brand as={Link} to="/" className="d-flex align-items-center gap-2">
          <FaGraduationCap aria-hidden="true" />
          <span>Learning Buddy</span>
        </BootstrapNavbar.Brand>
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          {isAuthenticated && (
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
          )}
          <Nav className="align-items-center">
            {isAuthenticated ? (
              <>
                <Nav.Link disabled className="text-light">
                  {userEmail}
                </Nav.Link>
                <Button variant="outline-light" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <div className="d-flex gap-2">
                <Button variant="light" size="sm" onClick={() => navigate('/login')}>
                  Login
                </Button>
                <Button variant="outline-light" size="sm" onClick={() => navigate('/register')}>
                  Register
                </Button>
              </div>
            )}
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;

