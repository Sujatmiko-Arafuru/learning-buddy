import React from 'react';
import { Container as BootstrapContainer } from 'react-bootstrap';
import Navbar from './Navbar';

interface ContainerProps {
  children: React.ReactNode;
}

const Container: React.FC<ContainerProps> = ({ children }) => {
  return (
    <>
      <Navbar />
      <BootstrapContainer className="py-4">
        {children}
      </BootstrapContainer>
    </>
  );
};

export default Container;

