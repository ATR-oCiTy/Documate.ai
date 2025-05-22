import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'; // For .toBeInTheDocument()
import Header from './Header';

describe('Header Component', () => {
  test('renders application title', () => {
    render(<Header />);
    
    // Option 1: Find by text content
    const titleElementByText = screen.getByText(/Epic Changelog Generator/i);
    expect(titleElementByText).toBeInTheDocument();

    // Option 2: Find by role (more semantic)
    const titleElementByRole = screen.getByRole('heading', { name: /Epic Changelog Generator/i, level: 1 });
    expect(titleElementByRole).toBeInTheDocument();
  });
});
